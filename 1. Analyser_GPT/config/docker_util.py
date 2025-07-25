from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
from constant import DOCKER_WORKING_DIRECTORY_NAME,DOCKER_TIMEOUT

def getDockerCommandLineExecutor():
    
    docker = DockerCommandLineCodeExecutor(
        container_name='Analyzer_GPT_Code_Executor',
        work_dir=DOCKER_WORKING_DIRECTORY_NAME,
        timeout=DOCKER_TIMEOUT
    )
    return docker

async def start_docker_container(docker):
    '''This function when call will set the working env variable connects to docker and start the code execution'''
    print("Start Docker")
    await docker.stop()
    print("Docker Started")
    
async def stop_docker_container(docker):
    '''This function when call will stop the docker container and clean up any temporary files along with the directory'''
    print("Stop Docker")
    await docker.stop()
    print("Docker Container Started")
    