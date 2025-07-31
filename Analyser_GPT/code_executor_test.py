from autogen_agentchat.agents import CodeExecutorAgent
import asyncio
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from prompts.dsa_problem_solver_system_message import DSA_PROBLEM_SOLVER_SYSTEM_MESSAGE
from autogen_agentchat.agents import AssistantAgent
from models.openai_model_client import getOpenAIModelClient
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.base import TaskResult

async def main():
    
    model_client = getOpenAIModelClient()
    
    docker = DockerCommandLineCodeExecutor(
        work_dir='temp',
        timeout=120
    )
    
    code_executor_agent = CodeExecutorAgent(
        name = 'Python_Code_Executor_Agent',
        code_executor = docker
    )
    
    dsa_solver_agent = AssistantAgent(
        name='DSA_Solver_Agent',
        model_client=model_client,
        description='An Agent that solves the DSA Problem and gives the code as well',
        system_message=DSA_PROBLEM_SOLVER_SYSTEM_MESSAGE
    )
    
    dsa_code_reviewer_Agent = AssistantAgent(
        name = 'DSA_Code_Reviewer_Agent',
        model_client=model_client,
        description='An agent who analyze the output of Python_Code_Executo_Agent',
        system_message='You are a Code Reviewer agent who is expert in python. Your task is to analyze the output of the Python_Code_Executor and if there is an error analyse what went wrong, check the script and explain what need to be corrected in the code for DSA_Solver_Agent to take further action. IF the code is successful and output is printed say that "Code Run Successfully"'
    )
    
    text_termination = TextMentionTermination('STOP')
    
    dsa_solver_team = RoundRobinGroupChat(
        participants=[dsa_solver_agent,code_executor_agent, dsa_code_reviewer_Agent],
        termination_condition=text_termination,
        max_turns=15
    )
    
    try:
        await docker.start()
        task = '''
        Problem: Minimum Meeting Rooms Required. Given a list of meeting time intervals, where each interval is represented as [start, end], determine the minimum number of conference rooms required to hold all the meetings. 
        Assume that the end time of a meeting is exclusive. For example, a meeting [5, 10] and another [10, 15] do not overlap and can be held in the same room.
        
        Example: 
        Input: meetings = [[0, 30], [5, 10], [15, 20]]
        Output: 2
        
        Explanation:
        The meeting [0, 30] starts. Room 1 is occupied.
        The meeting [5, 10] starts. [0, 30] is still in progress, so Room 2 is occupied.
        The meeting [5, 10] ends. Room 2 becomes free.
        The meeting [15, 20] starts. [0, 30] is still in progress, but Room 2 is free, so it can be used.
        At the peak, two meetings ([0, 30] and [5, 10]) were happening simultaneously. Therefore, the minimum number of rooms required is 2.
        
        Constraints
        1 <= meetings.length <= 10^4
        0 <= start_i < end_i <= 10^6
        '''
        
        async for message in dsa_solver_team.run_stream(task=task):
            print("=="*20)
            
            if isinstance(message,TextMessage):
                print(f"{message.source} : {message.content}")
            
            elif isinstance(message, TaskResult):
                print(f"Stop Reason : {message.stop_reason}")
        
    except Exception as e:
        print(f'Exception {str(e)}')
    finally:
        await docker.stop()
    
if __name__ == '__main__':
    asyncio.run(main())