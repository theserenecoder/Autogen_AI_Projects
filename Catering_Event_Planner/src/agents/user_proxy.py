from autogen_agentchat.agents import UserProxyAgent
import sys
import streamlit as st

from logger.custom_logger import CustomLogger
from exception.custom_exception import CustomException
from utils.config_loader import load_config
from prompts.system_messages import PROMPT_MESSAGES



def getCulinaryTeamUserApproval():
    """Funtion to get Culinary Team User Approval"""
    log = CustomLogger().get_logger(__name__)
    try:
        ## logging info
        log.info("Initializing Culinary Team Approval Agent")
        ## loading config
        config = load_config()
        agent_info = config['agents']['CulinaryTeamUserApproval']
        ## agent
        culinary_team_user_approval = UserProxyAgent(
            name = agent_info['name'],
            description='A proxy agent that represent the user',
            input_func= input,
        )
        log.info("Successfully Initialized Culinary Team Approval Agent", agent_info=list(agent_info.keys()))
        
        return culinary_team_user_approval
    except Exception as e:
        log.error("Error Initializing Culinary Team Approval Agent",agent_info= list(agent_info.keys()))
        raise CustomException("Error Initializing Culinary Team Approval Agent", sys)
    
    
def getFinalApproval():
    """Funtion to get Final Approval"""
    log = CustomLogger().get_logger(__name__)
    try:
        ## logging info
        log.info("Initializing Final Approval Agent")
        ## loding config
        config = load_config()
        agent_info = config['agents']['FinalApproval']
        ##agent
        final_approval = UserProxyAgent(
            name = agent_info['name'],
            description="A proxy agent that represent the user for final approval",
            input_func=input
        )
        log.info("Successfully Initialized Final Approval Agent", agent_info= list(agent_info.keys()))
        
        return final_approval
    except Exception as e:
        log.error("Error Initializing Final Approval Agent",agent_info= list(agent_info.keys()))
        raise CustomException("Error Initializing Final Approval Agent", sys)