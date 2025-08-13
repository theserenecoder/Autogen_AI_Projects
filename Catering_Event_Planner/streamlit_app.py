import streamlit as st
from src.team.event_management_team import getEventManagementTeam
from autogen_agentchat.messages import TextMessage
from models.model_loader import ModelLoader
import asyncio
import platform
import traceback


# --- Fallback note ---
# We keep the previous fallback in place but rely on UI approvals to avoid terminal I/O.
# Do not use stdin in production deployments.
# ---------------- Page setup & loop policy ----------------
st.set_page_config(page_title="Culinary Event Planner", page_icon="🍽️", layout="wide")

# On Windows, prefer selector loop policy for compatibility
if platform.system() == "Windows":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # type: ignore[attr-defined]
    except Exception:
        pass

# Async runner: prefer asyncio.run; if a loop is already running (rare on Streamlit),
# fall back to running the coroutine in a dedicated background thread with its own loop.
def run_coro(coro):
    try:
        return asyncio.run(coro)
    except RuntimeError as e:
        if "asyncio.run() cannot be called from a running event loop" in str(e) or \
           "This event loop is already running" in str(e):
            import threading
            result, err = {}, {}
            def _runner():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result["value"] = loop.run_until_complete(coro)
                except Exception as ex:
                    err["e"] = ex
                finally:
                    loop.close()
            t = threading.Thread(target=_runner, daemon=True)
            t.start(); t.join()
            if "e" in err:
                st.error(f"Streaming error: {err['e']}")
                traceback.print_exc()
            return result.get("value")
        else:
            st.error(f"Streaming error: {e}")
            traceback.print_exc()
            return None

# ----------------- Lightweight styling -----------------
CUSTOM_CSS = """
<style>
/* tighten page */
.block-container { padding-top: 1rem; padding-bottom: 2rem; }

/* nice chat bubbles */
.chat-bubble { padding: .75rem .9rem; border-radius: 14px; border: 1px solid rgba(0,0,0,.06); }
.user-bubble { background:#eef6ff; }
.agent-bubble { background:#f7f7f8; }
.sender { font-weight:600; font-size:.92rem; opacity:.75; margin-bottom:.15rem; }
.small { font-size:.85rem; opacity:.8; }

/* stage indicator */
.stage-row { display:flex; gap:6px; flex-wrap:wrap; align-items:center; margin:.5rem 0 1rem 0; }
.stage-pill { padding:6px 10px; border-radius:999px; border:1px solid #e6e6e6; background:#f8f9fb; font-size:.85rem; }
.stage-pill.done { background:#eafff2; border-color:#16a34a; }
.stage-pill.current { background:#f3e8ff; border-color:#7c3aed; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ----------------- State -----------------
if "messages" not in st.session_state:
    # Each item: {role: "user"|"assistant", content: str, sender?: str}
    st.session_state.messages = []

if "model_client" not in st.session_state:
    loader = ModelLoader()
    st.session_state.model_client = loader.load_llm()


# UI prefs & action flags
if "typewriter" not in st.session_state:
    st.session_state.typewriter = True
if "speed_ms" not in st.session_state:
    st.session_state.speed_ms = 4
if "trigger_send" not in st.session_state:
    st.session_state.trigger_send = False
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = ""
if "composer_text" not in st.session_state:
    st.session_state.composer_text = ""

# ----------------- Avatars & mapping -----------------
AGENT_AVATARS = {
    "PlannerAgent": {"name": "Planner Agent", "icon": "📝"},
    "RecipeAgent": {"name": "Recipe Agent", "icon": "👨‍🍳"},
    "CritiqueAgent": {"name": "Critique Agent", "icon": "🧐"},
    "CulinaryTeamAsAgent": {"name": "Culinary Team", "icon": "🍽️"},
    "LogisticAgent": {"name": "Logistics Agent", "icon": "📦"},
    "BudgetAgent": {"name": "Budget Agent", "icon": "💰"},
    "FinalApproval": {"name": "User Approval", "icon": "✅"},
    "CulinaryTeamUserApproval": {"name": "User Approval", "icon": "✅"},
    "Default": {"name": "Assistant", "icon": "🤖"},
}


def resolve_display(sender: str):
    if not sender:
        meta = AGENT_AVATARS["Default"]
        return meta["name"], meta["icon"]
    for key, meta in AGENT_AVATARS.items():
        if key != "Default" and sender.startswith(key):
            return meta["name"], meta["icon"]
    meta = AGENT_AVATARS["Default"]
    return meta["name"], meta["icon"]

# ----------------- Stage indicator helpers -----------------
STAGES = [
    ("PlannerAgent", "Planner", "📝"),
    ("RecipeAgent", "Recipe", "👨‍🍳"),
    ("CritiqueAgent", "Critique", "🧐"),
    ("CulinaryTeamUserApproval", "Inner Approval", "✅"),
    ("CulinaryTeamAsAgent", "Culinary Team", "🍽️"),
    ("LogisticAgent", "Logistics", "📦"),
    ("BudgetAgent", "Budget", "💰"),
    ("FinalApproval", "Final Approval", "✅"),
]

def _stage_index_from_sender(sender: str):
    if not sender:
        return None
    for i, (key, _, _) in enumerate(STAGES):
        if sender.startswith(key):
            return i
    return None

def get_current_stage_index(messages):
    # Look at last assistant message with a sender
    for m in reversed(messages):
        if m.get("role") == "assistant":
            idx = _stage_index_from_sender(m.get("sender", ""))
            if idx is not None:
                return idx
    return None

def render_stage_indicator(container=None):
    idx = get_current_stage_index(st.session_state.messages)
    pills = []
    for i, (_, label, icon) in enumerate(STAGES):
        cls = "stage-pill"
        if idx is None and i == 0:
            cls += " current"
        elif idx is not None:
            if i < idx:
                cls += " done"
            elif i == idx:
                cls += " current"
        pills.append(f'<div class="{cls}">{icon} {label}</div>')
    html = '<div class="stage-row"><span class="small" style="margin-right:6px;">Workflow:</span>' + "".join(pills) + '</div>'
    if container is None:
        st.markdown(html, unsafe_allow_html=True)
    else:
        container.markdown(html, unsafe_allow_html=True)

# ----------------- Streaming -----------------
async def stream_messages(model_client, task: str, use_typewriter: bool = True, speed_s: float = 0.004):
    """Build a fresh team for each run and stream messages. We render as raw text while
    typing (to avoid mid-markdown glitches) and switch to markdown when complete."""
    # Echo user
    # if task:
    #     with st.chat_message("You", avatar="😀"):
    #         st.markdown(task)
    #     st.session_state.messages.append({"role": "user", "content": task})

    # Build a NEW team for this run
    team = getEventManagementTeam(model_client)

    try:
        async for message in team.run_stream(task=task):
            if not isinstance(message, TextMessage):
                continue
            sender = getattr(message, "source", "Default") or "Default"
            name, icon = resolve_display(sender)

            # Stream with typewriter -> render as plain text while streaming,
            # then replace with full markdown to preserve formatting
            with st.chat_message(name, avatar=icon):
                # Show agent name on first line, content below
                st.markdown(f"**{name}**")
                placeholder = st.empty()
                text = message.content or ""
                if use_typewriter and text:
                    buf = ""
                    for ch in text:
                        buf += ch
                        placeholder.text(buf)
                        await asyncio.sleep(speed_s)
                    placeholder.markdown(text)
                else:
                    placeholder.markdown(text)

            # Save to transcript
            st.session_state.messages.append({"role": "assistant", "sender": sender, "content": text})
            if "stage_ph" in st.session_state:
                render_stage_indicator(st.session_state.stage_ph)

    except Exception as e:
        st.error(f"Stream failed: {e}")
        traceback.print_exc()

# ----------------- UI -----------------
st.title("🍽️Culinary Event Planner")

# Sidebar: Event Setup (prompt builder; optional, non-invasive)
with st.sidebar:
    st.header("Event Setup")
    colA, colB = st.columns(2)
    with colA:
        guests = st.number_input("Guests", 1, 500, 30, 1)
    with colB:
        budget_pp = st.slider("Budget ($/guest)", 10, 200, 40, 5)

    event_type = st.selectbox("Event type", ["Formal Dinner", "Buffet", "Cocktail", "Wedding", "Corporate Lunch", "Other"], index=0)
    service = st.selectbox("Service style", ["Table service", "Buffet", "Passed canapés"], index=0)
    cuisines = st.multiselect("Cuisine", ["Indian", "Mughlai", "Italian", "French", "Mexican", "Mediterranean", "Pan-Asian", "Modern"], default=["Modern"]) 
    dietary = st.multiselect("Dietary", ["Vegetarian", "Vegan", "Gluten-free", "Nut-free", "Halal", "Kosher"])
    extras = st.text_area("Notes (optional)", placeholder="Any constraints or must-haves…", height=80)

    def _build_prompt():
        parts = [
            f"Please plan a menu for a {event_type.lower()} for {guests} guests.",
            f"The budget for food is ${budget_pp} per person.",
            f"Service style: {service}.",
        ]
        if cuisines:
            parts.append("Cuisine preference: " + ", ".join(cuisines) + ".")
        if dietary:
            parts.append("Please include options for: " + ", ".join(dietary) + ".")
        if extras.strip():
            parts.append("Additional instructions: " + extras.strip())
        #parts.append("Ask for my approval before moving to logistics and budget.")
        return " ".join(parts)

    st.markdown("#### Prompt preview")
    built = _build_prompt()
    prompt_box = st.text_area("Edit before sending", value=built, height=140)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("➕ Add to chat", use_container_width=True):
            st.session_state.composer_text = prompt_box
            st.toast("Added to chat composer.")
    with c2:
        if st.button("▶ Build & Send", use_container_width=True):
            st.session_state.pending_prompt = prompt_box
            st.session_state.trigger_send = True

    st.markdown("---")
    st.subheader("Workflow")
    if "stage_ph" not in st.session_state:
        st.session_state.stage_ph = st.empty()
    render_stage_indicator(st.session_state.stage_ph)

    st.markdown("---")
    st.subheader("Display")
    st.session_state.typewriter = st.toggle("Typewriter mode", value=st.session_state.typewriter, help="Animate messages as they arrive")
    st.session_state.speed_ms = st.slider("Speed (ms/char)", min_value=1, max_value=20, value=st.session_state.speed_ms, step=1)
    # if st.button("Reset transcript", use_container_width=True):
    #     st.session_state.messages = []
    #     st.session_state.composer_text = ""
    #     st.experimental_rerun()

    # st.markdown("---")
    # if st.button("Open approval panel", use_container_width=True):
    #     st.session_state.approval_needed = True
    #     st.session_state.approval_hint = "Manually opened: provide approval or feedback."

# If sidebar requested an immediate send, do it HERE (outside sidebar) so output appears in main area
if st.session_state.trigger_send and st.session_state.pending_prompt.strip():
    run_coro(
        stream_messages(
            st.session_state.model_client,
            st.session_state.pending_prompt,
            use_typewriter=st.session_state.typewriter,
            speed_s=st.session_state.speed_ms / 1000.0,
        )
    )
    st.session_state.trigger_send = False
    st.session_state.pending_prompt = ""

# Chat composer (lets sidebar prefill into a message and send from main pane)
if st.session_state.composer_text:
    st.markdown("#### Chat draft")
    st.text_area("Draft to send", key="composer_text", height=120)
    send_col, _ = st.columns([1, 9])
    if send_col.button("Send draft"):
        text_to_send = st.session_state.composer_text.strip()
        if text_to_send:
            run_coro(
                stream_messages(
                    st.session_state.model_client,
                    text_to_send,
                    use_typewriter=st.session_state.typewriter,
                    speed_s=st.session_state.speed_ms / 1000.0,
                )
            )
            st.session_state.composer_text = ""

# Replay transcript so new runs append at the end
for entry in st.session_state.messages:
    if entry.get("role") == "user":
        with st.chat_message("You", avatar="😀"):
            st.markdown(entry.get("content", ""))
    else:
        name, icon = resolve_display(entry.get("sender", "Default"))
        with st.chat_message(name, avatar=icon):
            st.markdown(entry.get("content", ""))

# Chat input
prompt = st.chat_input("Describe your event plan request")
if prompt:
    run_coro(
        stream_messages(
            st.session_state.model_client,
            prompt.strip(),
            use_typewriter=st.session_state.typewriter,
            speed_s=st.session_state.speed_ms / 1000.0,
        )
    )

