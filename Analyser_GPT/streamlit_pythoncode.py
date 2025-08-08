import streamlit as st
import subprocess
from streamlit_ace import st_ace
import os


st.set_page_config(page_title="Python in Streamlit", page_icon='🐍', layout='wide')

## Session State 
if 'code_to_run' not in st.session_state:
    st.session_state.python_code = ''
if 'code_output' not in st.session_state:
    st.session_state.code_output = ''
if 'editor_code' not in st.session_state:
    st.session_state.editor_code = ''


def run_python_code(code):
    
    file_path = 'temp_code.py'
    with open(file_path,'w') as file:
        file.write(code)
    try:
        process = subprocess.run(
            ['python', file_path],
            capture_output=True,
            text=True,
            check=False  # Don't raise an exception if the command returns a non-zero exit code
        )
        
        # Clean up the temporary file
        os.remove(file_path)
        
        return process.stdout + process.stderr
        
    except Exception as e:
        print(f"Exeption : {str(e)}")
        st.warning(e)
        
def generate_output():
    try:
        st.session_state.code_to_run = st.session_state.editor_code
        
        output = run_python_code(st.session_state.code_to_run)
        
        st.session_state.code_output = output
        
        with col2:
            st.subheader('Code Content')
            st.code(st.session_state.code_to_run, language='python')
            st.subheader('Code Output')
            st.code(st.session_state.code_output)
            
    except Exception as e:
        print(f"Exception : {str(e)}")
        

        
        
## main Application
st.title('Python in Streamlit')

col1,col2 = st.columns(2)


with col1:
    st.subheader('Code Input')
    code_dir = 'work_dir_docker'
    python_files = []
    
    if os.path.exists(code_dir) and os.path.isdir(code_dir):
        python_files = sorted([f for f in os.listdir(code_dir) if f.endswith('.py')])
    else:
        st.error(f"The directory '{code_dir}' does not exists")
        st.stop()
        
    ## Create a select box
    if python_files:
        selected_files = st.selectbox('Select a python script to run', python_files)
        
        ## Read the content of the selected file and update the editor's state
        file_path = os.path.join(code_dir, selected_files)
        try:
            with open(file_path,'r') as file:
                file_content = file.read()
                
            # This 
            if st.session_state.editor_code != file_content:
                st.session_state.editor_code = file_content
                print(st.session_state.editor_code)
                   
                #st.rerun()
        except Exception as e:
            st.error(f'Could not read the file {selected_files} : {str(e)}')
        
    
    else:
        st.warning(f"No python file found in {code_dir}")
        
        
    ## Ace Editor for code input
    
    st.caption(f'Content of {selected_files}')
    st_ace(
        value=st.session_state.editor_code,
        language='python',
        min_lines=20,
        theme='monokai',
        key='editor_code'
    )
    
    print(st.session_state.editor_code)
    
    st.button('Run Code', on_click=generate_output, type='primary', use_container_width=True)
    

    
    
    
