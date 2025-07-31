import streamlit as st
import asyncio
import os
import pandas as pd
from datetime import datetime
import regex as re

from team.analyzer_team import getAnalyzerTeam
from config.docker_util import getDockerCommandLineExecutor, start_docker_container, stop_docker_container
from models.openai_model_client import getOpenAIModelClient
from config.constant import DOCKER_WORKING_DIRECTORY_NAME
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.base import TaskResult


st.header('Analyzer GPT - Digital Data Analyzer')

#upload_file = st.file_uploader("Upload a CSV file", type=["csv"])

## Session State Initialize

if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'autogen_team_state' not in st.session_state:
    st.session_state.autogen_team_state = None
if 'image_paths' not in st.session_state:
    st.session_state.image_paths = []
if 'saved_file_path' not in st.session_state:
    st.session_state.saved_file_path = None

with st.sidebar:
    current_upload_file = st.file_uploader('Upload a CSV file.',type=['csv'])

## Chat input for Task and File upload
current_task = st.chat_input(
    "Enter your task here..."
)


async def run_analyzer_gpt(docker, openai_model_client,task):
    try:
        await start_docker_container(docker)
        analyzer_team = getAnalyzerTeam(docker,openai_model_client)
        
        if st.session_state.autogen_team_state is not None:
            await analyzer_team.load_state(st.session_state.autogen_team_state)

        # Clear image paths at the start of a new task execution
        st.session_state.image_paths = []
        
        async for message in analyzer_team.run_stream(task=task):
            if isinstance(message, TextMessage):
                if message.source.startswith('user'):
                    with st.chat_message('User', avatar=':material/face:'):
                        st.markdown(message.content)

                elif message.source.startswith('Data_Analyzer_Agent'):
                    with st.chat_message('Data Analyzer', avatar=':material/smart_toy:'):
                        st.markdown(message.content)

                elif message.source.startswith('Python_Code_Executor'):
                    with st.chat_message('Code Executor', avatar=':material/android:'):
                        st.text(message.content)
                        
                st.session_state.messages.append(message.content)
                
                ## Image Detection Logic
                if message.source.startswith('Python_Code_Executor'):
                    image_list_match = re.search(r'Generated_Images:\s*(.*)',message.content)
                    
                    if image_list_match:
                        filename_str = image_list_match.group(1)
                        generated_relative_paths = [f.strip() for f in filename_str.split(",") if f.strip().endswith('.png')]
                        
                        for relative_path in generated_relative_paths:
                            image_file_path = os.path.join(DOCKER_WORKING_DIRECTORY_NAME,relative_path)
                            #st.image(image_file_path, caption=image_file_path)
                            
                            if os.path.exists(image_file_path) and image_file_path not in st.session_state.image_paths:
                                st.session_state.image_paths.append(image_file_path)
                                #st.rerun()
                
            elif isinstance(message,TaskResult):
                st.markdown(f"Stop Reason : {message.stop_reason}")
                st.session_state.messages.append(message.stop_reason)
                
        st.session_state.autogen_team_state = await analyzer_team.save_state()

        return None
    
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None
    
    finally:
        await stop_docker_container(docker)
        return None
    
if st.session_state.messages:
    for msg in st.session_state.messages:
        st.markdown(msg)
        
if st.session_state.image_paths:
    for img in st.session_state.image_paths:
        st.image(img, caption=img)
    
if current_task:
    if current_upload_file is not None:
        
        if not os.path.exists(DOCKER_WORKING_DIRECTORY_NAME):
            os.makedirs(DOCKER_WORKING_DIRECTORY_NAME, exist_ok=True)
        
        
        file_path = os.path.join(DOCKER_WORKING_DIRECTORY_NAME,'data.csv')
        
        with open(file_path, 'wb') as file:
            file.write(current_upload_file.getbuffer())
            
        openai_model_client = getOpenAIModelClient()
        docker = getDockerCommandLineExecutor()
        
        error = asyncio.run(run_analyzer_gpt(docker,openai_model_client,current_task))
        
        if error:
            st.error('An error has occured: {error}')
        

        if st.session_state.image_paths:
            for img in st.session_state.image_paths:
                st.image(img, caption=img)
    
    else:
        st.warning('Please upload a file and then provide a task')
        
else:
    st.warning('Please provide the task')