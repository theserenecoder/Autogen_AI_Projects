import asyncio
from models.openai_model_client import getOpenAIModelClient
from config.docker_util import getDockerCommandLineExecutor, start_docker_container, stop_docker_container
from team.analyzer_team import getAnalyzerTeam
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.base import TaskResult


async def main():
    
    openai_model_client = getOpenAIModelClient()
    
    docker  = getDockerCommandLineExecutor()
    
    agents_team = getAnalyzerTeam(docker,openai_model_client)
    
    try:
        task = 'Give me a graph of sepal length based on variety iris.csv'
        
        await start_docker_container(docker)
        
        async for message in agents_team.run_stream(task=task):
            if isinstance(message,TextMessage):
                if message.source.startswith('user'):
                    print('User')
                if message.source.startswith('Data_Analyzer_Agent'):
                    print("Data Analyzer Agent")
                elif message.source.startswith('Python_Code_Executor'):
                    print('Python Code Executor')
            elif isinstance(message,TaskResult):
                print(message.messages[-1].content)
            
        
            
    except Exception as e:
        print(f'\nException : {str(e)}\n')
    finally:
        await stop_docker_container(docker)
        
    
if __name__ == '__main__':
    asyncio.run(main())