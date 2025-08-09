from models.model_loader import ModelLoader
from autogen_agentchat.ui import Console
from src.team.event_management_team import getEventManagementTeam
import asyncio


async def run_code():
    loader = ModelLoader()
    model_client = loader.load_llm()
    
    team = getEventManagementTeam(model_client)
    
    task="""
    Please plan a menu for a formal dinner party for 30 people. The budget for food is $50 per person. 
    The guests have no dietary restrictions but prefer a menu that includes a mix of textures and flavors. 
    Keep the item list to 5 items only
    """
    
    await Console(team.run_stream(task=task))
    
asyncio.run(run_code())