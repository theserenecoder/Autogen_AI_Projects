from autogen_agentchat.teams import RoundRobinGroupChat
from agents.dsa_solver_agent import getDSASolverAgent
from agents.code_executor_agent import getCodeExecutorAgent
from agents.code_reviewer_agent import getCodeReviewerAgent
from autogen_agentchat.conditions import TextMentionTermination
from config.constant import TEXT_MENTION, MAX_TURNS

def getDSASolverTeam(docker,model_client):
    '''
    Function to get the dsa solver agent team.
    '''
    code_executor_agent = getCodeExecutorAgent(docker)
    dsa_solver_agent = getDSASolverAgent(model_client)
    code_reviewer_agent = getCodeReviewerAgent(model_client)
    termination_condition = TextMentionTermination(TEXT_MENTION)
    
    dsa_solver_team = RoundRobinGroupChat(
        participants=[dsa_solver_agent, code_executor_agent, code_reviewer_agent],
        max_turns=MAX_TURNS,
        termination_condition=termination_condition,
    )
    
    return dsa_solver_team