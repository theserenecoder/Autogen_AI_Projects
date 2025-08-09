from autogen_agentchat.agents import AssistantAgent
import sys

from logger.custom_logger import CustomLogger
from exception.custom_exception import CustomException
from utils.config_loader import load_config
from prompts.system_messages import PROMPT_MESSAGES

def getCritiqueAgent(model_client):
    """Funtion to call the Critique Agent.
    It will review the menu, ingridients and recipes and provide feedback to user.
    """
    log = CustomLogger().get_logger(__name__)
    try:
        log.info("Initializing Critique Agent")
        config = load_config()
        agent_info = config['agents']['CritiqueAgent']
        
        critique_agent = AssistantAgent(
            name=agent_info['name'],
            model_client=model_client,
            description="An agent that evaluate the menu and receipes",
            system_message=PROMPT_MESSAGES[agent_info['system_message_key']]
        )
        log.info("Critique Agent Initialized", agent_info=list(agent_info.keys()))
        
        return critique_agent
        
    except Exception as e:
        log.error("Error Initializing Critique Agent")
        raise CustomException("Error Initializing Critique Agent",sys)
    
if __name__ =='__main__':
    from models.model_loader import ModelLoader
    from autogen_agentchat.ui import Console
    import asyncio
    
    async def run_code():
        loader  =ModelLoader()
        model_client = loader.load_llm()
        task = """
        Review the reciepe
        **Quick Avocado Toast**
        **Ingredients:**
        - 1 ripe avocado
        - 2 slices of whole-grain bread
        - Salt and pepper to taste
        - Optional: Red pepper flakes or lemon juice for extra flavor

        **Instructions:**
        1. Toast the slices of whole-grain bread until golden brown.
        2. Mash the ripe avocado in a bowl and season with salt, pepper, and optional lemon juice.
        3. Spread the mashed avocado generously over the toasted bread.
        4. Sprinkle with red pepper flakes if desired and serve immediately.

        """
        agent = getCritiqueAgent(model_client)
        await Console(agent.run_stream(task=task))
        
    asyncio.run(run_code())