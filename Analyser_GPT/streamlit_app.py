import streamlit as st
import asyncio
import os

from team.dsa_solver_team import getDSASolverTeam
from config.docker_util import getDockerCommandLineExecutor, start_docker_container, stop_docker_container
from models.openai_model_client import getOpenAIModelClient
from config.constant import DOCKER_WORKING_DIRECTORY_NAME
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.base import TaskResult


st.header('AgentGini - DSA Solver')

#upload_file = st.file_uploader("Upload a CSV file", type=["csv"])

## Session State Initialize

if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'autogen_team_state' not in st.session_state:
    st.session_state.autogen_team_state = None

## Chat input for Task and File upload
task= st.chat_input("Enter your DSA Query to solve")


async def run_analyzer_gpt(docker, openai_model_client, task):
    try:
        await start_docker_container(docker)
        dsa_solver_team = getDSASolverTeam(docker, openai_model_client)
        
        if st.session_state.autogen_team_state is not None:
            await dsa_solver_team.load_state(st.session_state.autogen_team_state)
        
        async for message in dsa_solver_team.run_stream(task=task):
            if isinstance(message, TextMessage):
                if message.source.startswith('user'):
                    with st.chat_message('User', avatar=':material/face:'):
                        st.markdown(message.content)

                elif message.source.startswith('DSA_Solver_Agent'):
                    with st.chat_message('Data Analyzer', avatar=':material/smart_toy:'):
                        st.markdown(message.content)

                elif message.source.startswith('Python_Code_Executor'):
                    with st.chat_message('Code Executor', avatar=':material/android:'):
                        st.text(message.content)
                        
                elif message.source.startswith('Code_Reviewer_Agent'):
                    with st.chat_message('Code Reviewer', avatar=':material/support_agent:'):
                        st.markdown(message.content)
                        
                st.session_state.messages.append(message.content)
                
            elif isinstance(message,TaskResult):
                with st.chat_message('stopper',avatar=':material/dangerous:'):
                    st.markdown(f"Task Completed : {message.stop_reason}")
                st.session_state.messages.append(message.stop_reason)
                
        st.session_state.autogen_team_state = await dsa_solver_team.save_state()

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
    
if task:    
    openai_model_client = getOpenAIModelClient()
    docker = getDockerCommandLineExecutor()
    
    error = asyncio.run(run_analyzer_gpt(docker,openai_model_client,task))
    
    if error:
        st.error('An error has occured: {error}')
    
        
