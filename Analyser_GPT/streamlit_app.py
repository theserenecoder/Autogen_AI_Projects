import streamlit as st
import asyncio
import os

from team.analyzer_team import getAnalyzerTeam
from config.docker_util import getDockerCommandLineExecutor, start_docker_container, stop_docker_container
from models.openai_model_client import getOpenAIModelClient
from config.constant import DOCKER_WORKING_DIRECTORY_NAME
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.base import TaskResult


st.title('Analyzer GPT - Digital Data Analyzer')

upload_file = st.file_uploader("Upload a CSV file", type=["csv"])

task = st.chat_input("Enter your task here...")

async def run_analyzer_gpt(docker, openai_model_client,task):
    try:
        await start_docker_container(docker)
        analyzer_team = getAnalyzerTeam(docker,openai_model_client)
        
        async for message in analyzer_team.run_stream(task=task):
            if isinstance(message,TextMessage):
                st.markdown(f"{message.content}")
            elif isinstance(message,TaskResult):
                st.markdown(f"{message.stop_reason}")
            
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None
    
    finally:
        await stop_docker_container(docker)
        return None
    
if task:
    if upload_file is not None:
        
        if not os.path.exists(DOCKER_WORKING_DIRECTORY_NAME):
            os.makedirs(DOCKER_WORKING_DIRECTORY_NAME, exist_ok=True)
        
        file_path = os.path.join(DOCKER_WORKING_DIRECTORY_NAME,'data.csv')
        
        with open(file_path, 'wb') as file:
            file.write(upload_file.getbuffer())
            
        openai_model_client = getOpenAIModelClient()
        docker = getDockerCommandLineExecutor()
        
        error = asyncio.run(run_analyzer_gpt(docker,openai_model_client,task))
        
        if error:
            st.error('An error has occured: {error}')
            
        image_path = os.path.join(DOCKER_WORKING_DIRECTORY_NAME,'output.png')
        
        if os.path.exists(image_path):
            st.image(image_path)
    
    else:
        st.warning('Please upload a file and then provide a task')