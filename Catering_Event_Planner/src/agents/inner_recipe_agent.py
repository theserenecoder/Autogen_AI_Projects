from autogen_agentchat.agents import AssistantAgent
import sys

from logger.custom_logger import CustomLogger
from exception.custom_exception import CustomException
from utils.config_loader import load_config
from prompts.system_messages import PROMPT_MESSAGES

def getRecipeAgent(model_client):
    '''Funtion to get the Recipe Agent. 
    It will be responsible for creating recipe from the menu.
    '''
    log = CustomLogger().get_logger(__name__)
    
    try:
        ## log info
        log.info("Initializing Recipe Agent")
        config = load_config()
        agent_info = config['agents']['RecipeAgent']
        
        planner_agent = AssistantAgent(
            name = agent_info['name'],
            model_client=model_client,
            description='An agent that create receipe based on the food menu',
            system_message=PROMPT_MESSAGES.get(agent_info['system_message_key'])
        )
        log.info("Recipe Agent Initialized", agent_info = list(agent_info.keys()))
        
        return planner_agent
    
    except Exception as e:
        log.error("Error Initializing Recipe Agent", agent_info = list(agent_info.keys()))
        raise CustomException("Error Initializing Recipe Agent", sys)
    
    
    
if __name__ =='__main__':
    from models.model_loader import ModelLoader
    from autogen_agentchat.ui import Console
    import asyncio
    
    async def run_code():
        loader  =ModelLoader()
        model_client = loader.load_llm()
        
        agent = getRecipeAgent(model_client)
        await Console(agent.run_stream(task='Create receipe for a quick meal which takes 2 mins and should be in 4 lines'))
        
    asyncio.run(run_code())
    