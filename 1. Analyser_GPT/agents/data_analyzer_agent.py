from autogen_agentchat.agents import AssistantAgent
from prompts.system_messages import DATA_ANALYZER_SYSTEM_MESSAGE

def getDataAnalyserAgent(model_client):
    
    data_analyzer_agent = AssistantAgent(
        name='Data_Analyzer_Agent',
        model_client=model_client,
        system_message=DATA_ANALYZER_SYSTEM_MESSAGE
    )