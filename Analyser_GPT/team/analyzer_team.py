from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from agents.code_executor_agent import getCodeExecutorAgent
from agents.data_analyzer_agent import getDataAnalyserAgent
from config.constant import TEXT_MENTION, MAX_TURNS

def getAnalyzerTeam(docker,model_client):
    '''
    Function to get the data analyzer agent team.
    '''
    code_executor_agent = getCodeExecutorAgent(docker)
    data_analyzer_agent = getDataAnalyserAgent(model_client)
    text_mention_termination = TextMentionTermination(TEXT_MENTION)
    
    analyzer_team = RoundRobinGroupChat(
        participants=[data_analyzer_agent, code_executor_agent],
        max_turns=MAX_TURNS,
        termination_condition=text_mention_termination
    )
    
    return analyzer_team