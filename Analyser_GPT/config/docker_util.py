from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
from config.constant import DOCKER_WORKING_DIRECTORY_NAME,DOCKER_TIMEOUT

def getDockerCommandLineExecutor():
    
    docker = DockerCommandLineCodeExecutor(
        container_name='Analyzer_GPT_Code_Executor',
        work_dir=DOCKER_WORKING_DIRECTORY_NAME,
        timeout=DOCKER_TIMEOUT
    )
    return docker

async def start_docker_container(docker):
    '''This function when call will set the working env variable connects to docker and start the code execution'''
    print("Start Docker Container")
    await docker.start()
    print("Docker Container Started")
    
async def stop_docker_container(docker):
    '''This function when call will stop the docker container and clean up any temporary files along with the directory'''
    print("Stop Docker Container")
    await docker.stop()
    print("Docker Container Stopped")
    