from autogen_agentchat.agents import SocietyOfMindAgent
import sys

from logger.custom_logger import CustomLogger
from exception.custom_exception import CustomException
from utils.config_loader import load_config
from prompts.system_messages import PROMPT_MESSAGES
from src.team.culinary_team import getCulinaryTeam

def getCulinaryTeamAsAgent(model_client):
    """Funtion to call the Culinary Team as Agent."""
    log = CustomLogger().get_logger(__name__)
    try:
        ## logging info
        log.info("Initializing Culinary Team as Agent")
        ## loading config
        config = load_config()
        agent_info = config['agents']['CulinaryTeamAsAgent']
        ## team
        culinary_team =getCulinaryTeam(model_client)
        
        culinary_team_as_agent = SocietyOfMindAgent(
            name=agent_info['name'],
            team=culinary_team,
            model_client=model_client,
            description="A culinary team agent which will build the menu and receipes.",
            response_prompt=PROMPT_MESSAGES[agent_info['system_message_key']]
        )
        log.info("Culinary Team as Agent Initialized", agent_info=list(agent_info.keys()))
        
        return culinary_team_as_agent
        
    except Exception as e:
        log.error("Error Initializing Culinary Team as Agent")
        raise CustomException("Error Initializing Culinary Team as Agent", sys)
    
if __name__ =='__main__':
    from models.model_loader import ModelLoader
    from autogen_agentchat.ui import Console
    import asyncio
    
    async def run_code():
        loader  =ModelLoader()
        model_client = loader.load_llm()
        
        team = getCulinaryTeamAsAgent(model_client)
        
        task="""
        Please plan a menu for a formal dinner party for 15 people.
        The guests have no dietary restrictions but prefer a menu that includes a mix of textures and flavors'''
        """
        await Console(team.run_stream(task=task))
        
    asyncio.run(run_code())