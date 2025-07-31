from autogen_agentchat.agents import AssistantAgent
from Analyser_GPT.prompts.data_analyzer_system_messages import DATA_ANALYZER_SYSTEM_MESSAGE

def getDataAnalyserAgent(model_client):
    '''
    Function to get the Data Analyzer Agent.
    This agent is responsible for solving data analysis problems.
    It will work with the Python_Code_Executor agent to execute the code.
    '''
    
    data_analyzer_agent = AssistantAgent(
        name='Data_Analyzer_Agent',
        model_client=model_client,
        description='An Agent that solves the Data Analysis Problem and gives the code as well',
        system_message=DATA_ANALYZER_SYSTEM_MESSAGE
    )
    return data_analyzer_agent