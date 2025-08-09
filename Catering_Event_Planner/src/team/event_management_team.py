from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
import sys

from src.agents.som_culinary_team_agent import getCulinaryTeamAsAgent
from src.agents.outer_logistic_agent import getLogisticAgent
from src.agents.outer_budget_agent import getBudgetAgent
from src.agents.user_proxy import getFinalApproval
from utils.config_loader import load_config
from logger.custom_logger import CustomLogger
from exception.custom_exception import CustomException


def getEventManagementTeam(model_client):
    '''Funtion to initialize culinary team'''
    log = CustomLogger().get_logger(__name__)
    
    ## mapping agent members from config to python fuctions
    agent_map = {
        "CulinaryTeamAsAgent": getCulinaryTeamAsAgent,
        "LogisticAgent": getLogisticAgent,
        "BudgetAgent" : getBudgetAgent,
        "FinalApproval": getFinalApproval
    }
    
    try:
        log.info("Defining Event Management Team Defined")
        ## loading config
        config = load_config()
        ## termination constants
        stop_word = config['termination']['word']
        max_turns= config['termination']['max_turns']
        
        ## team info
        team_info = config['teams']['EventManagementTeam']
        team_name = team_info['name']
        team_members = team_info['members']
                
        ## Agents
        ## checking if all the agents are available
        available_agents = set(agent_map.keys())
        required_agents = set(team_members)
        
        if not required_agents.issubset(available_agents):
            missing_agents = required_agents-available_agents
            log.error("Following agents are not available but required",missing_agents=missing_agents)
            raise CustomException("Missing agent in agent map")
        
        ## creating agents from agent map
        participants = []
        for agent_name in team_members:
            agent_creat_func = agent_map[agent_name]
            
            if agent_name =='FinalApproval':
                agent = agent_creat_func()
            else:
                agent = agent_creat_func(model_client)
            participants.append(agent)
        
        ## termination condition
        termination_condition = TextMentionTermination(stop_word) 
        
        event_management_team = RoundRobinGroupChat(
            participants=participants,
            termination_condition=termination_condition,
            max_turns=max_turns
        )
        log.info("Event Management Team Defined", members=team_members)
        
        return event_management_team
        
    except Exception as e:
        log.error("Error Initializing Event Management Team Defined", team_info=team_info)
        raise CustomException("Error Initializing Event Management Team Defined",sys)
    
if __name__ =='__main__':
    from models.model_loader import ModelLoader
    from autogen_agentchat.ui import Console
    import asyncio
    
    async def run_code():
        loader = ModelLoader()
        model_client = loader.load_llm()
        
        team = getEventManagementTeam(model_client)
        
        task="""
        Please plan a menu for a formal dinner party for 30 people.
        The guests have no dietary restrictions but prefer a menu that includes a mix of textures and flavors'''
        """
        
        await Console(team.run_stream(task=task))
        
    asyncio.run(run_code())