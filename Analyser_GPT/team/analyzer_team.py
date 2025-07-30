from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from agents.code_executor_agent import getCodeExecutorAgent
from agents.data_analyzer_agent import getDataAnalyserAgent

def getAnalyzerTeam(docker,model_client):
    
    code_executor_agent = getCodeExecutorAgent(docker)
    data_analyzer_agent = getDataAnalyserAgent(model_client)
    text_mention_termination = TextMentionTermination('STOP')
    
    analyzer_team = RoundRobinGroupChat(
        participants=[data_analyzer_agent, code_executor_agent],
        max_turns=15,
        termination_condition=text_mention_termination
    )
    
    return analyzer_team