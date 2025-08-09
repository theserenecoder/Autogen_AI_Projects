# 🍽️ Multi-Agent Culinary & Event Management System

A two-layer, config-driven multi‑agent application that plans menus, produces recipes, critiques feasibility, then generates logistics and budgets for events. It’s built on **autogen_agentchat** with robust logging and exception handling.

---

## Architecture

```mermaid
flowchart TD
    %% ========= LLM / Config / Prompts / Infra =========
    subgraph Infra[Infrastructure & Shared Utilities]
        ML[Model Loader<br/>(OpenAIChatCompletionClient)]
        CFG[Config Loader<br/>(config/config.yaml)]
        PROMPTS[System Messages<br/>(PROMPT_MESSAGES)]
        LOG[Custom Logger<br/>(structlog + AutoGen loggers)]
        EXC[Custom Exception<br/>(rich traceback)]
    end

    %% ========= Outer Team =========
    subgraph OUTER[Outer Team • Event Management]
        EMT[RoundRobinGroupChat<br/>EventManagementTeam]
        SoM[SocietyOfMindAgent<br/>CulinaryTeamAsAgent]
        LOGI[AssistantAgent<br/>LogisticAgent]
        BUD[AssistantAgent<br/>BudgetAgent]
        FINAL[UserProxyAgent<br/>FinalApproval]
    end

    %% ========= Inner Team =========
    subgraph INNER[Inner Team • Culinary]
        PLAN[AssistantAgent<br/>PlannerAgent]
        REC[AssistantAgent<br/>RecipeAgent]
        CRIT[AssistantAgent<br/>CritiqueAgent]
        UAPP[UserProxyAgent<br/>CulinaryTeamUserApproval]
    end

    %% ========= Wiring =========
    User((User)) --> EMT

    %% Outer sequencing
    EMT --> SoM
    EMT --> LOGI
    EMT --> BUD
    EMT --> FINAL

    %% Inner sequencing via SoM
    SoM --> PLAN --> REC --> CRIT --> UAPP
    UAPP -- approve/revise --> PLAN

    %% ========= Dependencies =========
    ML --> PLAN
    ML --> REC
    ML --> CRIT
    ML --> LOGI
    ML --> BUD
    ML --> FINAL
    ML --> SoM
    ML --> EMT

    CFG -. agents, teams, termination .-> PLAN
    CFG -. agents, teams, termination .-> REC
    CFG -. agents, teams, termination .-> CRIT
    CFG -. agents, teams, termination .-> LOGI
    CFG -. agents, teams, termination .-> BUD
    CFG -. agents, teams, termination .-> EMT
    CFG -. stop word / max turns .-> EMT
    CFG -. stop word / max msg turns .-> SoM

    PROMPTS -. system_message_key .-> PLAN
    PROMPTS -. system_message_key .-> REC
    PROMPTS -. system_message_key .-> CRIT
    PROMPTS -. system_message_key .-> LOGI
    PROMPTS -. system_message_key .-> BUD

    LOG -. JSON logs for all agents/teams .-> EMT
    LOG -. JSON logs for all agents/teams .-> SoM
    LOG -. JSON logs for all agents/teams .-> PLAN
    LOG -. JSON logs for all agents/teams .-> REC
    LOG -. JSON logs for all agents/teams .-> CRIT
    LOG -. JSON logs for all agents/teams .-> LOGI
    LOG -. JSON logs for all agents/teams .-> BUD
    LOG -. JSON logs for all agents/teams .-> FINAL

    EXC -. wrapped setup/runtime errors .-> EMT
    EXC -. wrapped setup/runtime errors .-> SoM
    EXC -. wrapped setup/runtime errors .-> PLAN
    EXC -. wrapped setup/runtime errors .-> REC
    EXC -. wrapped setup/runtime errors .-> CRIT
    EXC -. wrapped setup/runtime errors .-> LOGI
    EXC -. wrapped setup/runtime errors .-> BUD
    EXC -. wrapped setup/runtime errors .-> FINAL
```

---

## Components

### Inner “Culinary Team”
- **PlannerAgent** → interprets user brief and proposes a structured menu.
- **RecipeAgent** → produces detailed recipes and yields.
- **CritiqueAgent** → checks feasibility, conflicts, and consistency; requests revision as needed.
- **CulinaryTeamUserApproval** → interactive user proxy for approval in the inner loop.

### Outer “Event Management Team”
- **CulinaryTeamAsAgent (SocietyOfMindAgent)** → wraps the inner team as a single capability.
- **LogisticAgent** → shopping list, equipment needs, prep timeline & day-of schedule.
- **BudgetAgent** → costs for ingredients and rentals; total budget & assumptions.
- **FinalApproval (UserProxyAgent)** → end-of-pipeline sign-off.

### Termination
- **Inner team**: `TextMentionTermination(stop_word)` ⋁ `MaxMessageTermination(max_message_turns)`  
- **Outer team**: `TextMentionTermination(stop_word)` ⋁ `MaxMessageTermination(max_turns)`

---

## Configuration (YAML)

`config/config.yaml` drives agent names, prompt keys, team members, and termination rules.

```yaml
llm_config:
  provider: openai
  model_name: gpt-4o-mini

termination:
  word: "<STOP>"
  max_turns: 24
  max_message_turns: 12

teams:
  CulinaryTeam:
    name: "Culinary Team"
    members: ["PlannerAgent", "RecipeAgent", "CritiqueAgent", "CulinaryTeamUserApproval"]

  EventManagementTeam:
    name: "Event Management Team"
    members: ["CulinaryTeamAsAgent", "LogisticAgent", "BudgetAgent", "FinalApproval"]

agents:
  PlannerAgent:
    name: "Planner"
    system_message_key: "planner_message"

  RecipeAgent:
    name: "Recipe Writer"
    system_message_key: "recipe_message"

  CritiqueAgent:
    name: "Critic"
    system_message_key: "critique_message"

  LogisticAgent:
    name: "Logistics"
    system_message_key: "logistics_message"

  BudgetAgent:
    name: "Budgeter"
    system_message_key: "budget_message"
```

> Ensure `system_message_key` values exist in your `PROMPT_MESSAGES` map.

---

## Logging & Exceptions

- **Custom Logger**
  - Writes **JSON** logs via `structlog`.
  - Configures AutoGen's **EVENT** (INFO) and **TRACE** (DEBUG) loggers.
  - Creates a timestamped file in `./logs/` per run.

- **Custom Exception**
  - Captures file, line, message, and full traceback.
  - Stringified error is human-readable and log-friendly.

---

## Directory Layout (suggested)

```
.
├─ config/
│  └─ config.yaml
├─ logger/
│  ├─ __init__.py
│  └─ custom_logger.py
├─ exception/
│  ├─ __init__.py
│  └─ custom_exception.py
├─ prompts/
│  └─ system_messages.py
├─ src/
│  ├─ agents/
│  │  ├─ inner_planner_agent.py
│  │  ├─ inner_recipe_agent.py
│  │  ├─ inner_critique_agent.py
│  │  ├─ outer_logistic_agent.py
│  │  ├─ outer_budget_agent.py
│  │  ├─ som_culinary_team_agent.py
│  │  └─ user_proxy.py
│  ├─ team/
│  │  ├─ culinary_team.py
│  │  └─ event_management_team.py
│  └─ models/
│     └─ model_loader.py
└─ utils/
   └─ config_loader.py
```

---

## Quickstart

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set your LLM credentials**
   ```bash
   export OPENAI_API_KEY=sk-...
   # optionally:
   export LLM_PROVIDER=openai
   ```

3. **Run a demo (outer team)**
   ```bash
   python -m src.team.event_management_team
   ```

4. **Run the inner team only**
   ```bash
   python -m src.team.culinary_team
   ```

---

## Example Task

> “Please plan a menu for a formal dinner party for 30 people. The guests have no dietary restrictions but prefer a menu that includes a mix of textures and flavors.”

The system will:
1) Inner team: Plan → Recipe → Critique → user approve.  
2) Outer team: Logistics → Budget → final user approval.  
3) Produce a structured final report.

---

## Troubleshooting

- **Config path on Windows**: Use `config\\config.yaml` or prefer POSIX `config/config.yaml` for cross‑platform.
- **Missing prompt keys**: Ensure every `agents.*.system_message_key` exists in `PROMPT_MESSAGES`.
- **Terminations not triggering**: Verify `termination.word`, `max_turns`, and `max_message_turns` are set.
- **No logs**: Check that `./logs/` is writable and that the process has permissions.

---

## License

MIT (or your preferred license).
