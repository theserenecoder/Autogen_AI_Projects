from autogen_agentchat.agents import AssistantAgent
from prompts.dsa_problem_solver_system_message import DSA_PROBLEM_SOLVER_SYSTEM_MESSAGE

def getDSASolverAgent(model_client):
    '''
    Function to get the DSA solver agent.
    This agent is responsible for solving DSA problems.
    It will work with the Python_Code_Executor agent to execute the code.
    '''
    dsa_solver_agent = AssistantAgent(
        name='DSA_Solver_Agent',
        model_client=model_client,
        description='An Agent that solves the DSA Problem and gives the code as well',
        system_message=DSA_PROBLEM_SOLVER_SYSTEM_MESSAGE
    )
    
    return dsa_solver_agent