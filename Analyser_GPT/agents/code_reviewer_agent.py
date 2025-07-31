from prompts.code_reviewer_system_message import CODE_REVIEWER_SYSTEM_MESSAGE
from autogen_agentchat.agents import AssistantAgent

def getCodeReviewerAgent(model_client):
    '''
    Function to get the code reviewer agent.
    This agent is responsible for reviewing output of code executor agent.
    '''
    
    code_reviewer_agent = AssistantAgent(
        name = 'Code_Reviewer_Agent',
        model_client=model_client,
        description='An agent who analyze the output of Python_Code_Executo_Agent',
        system_message=CODE_REVIEWER_SYSTEM_MESSAGE
    )
    
    return code_reviewer_agent