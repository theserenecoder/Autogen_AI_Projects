from autogen_ext.models.openai import OpenAIChatCompletionClient
from utils.config_loader import load_config
from logger.custom_logger import CustomLogger
from dotenv import load_dotenv
import os


class ModelLoader():
    """ A class to load llm models"""
    def __init__(self):
        self.log = CustomLogger().get_logger(__name__)
        load_dotenv()
        ## loading the config
        self.config = load_config()
        
    def _validate_env(self):
        """A function to validate environment variable and ensure api key exits"""
        ## we are defining all the keys which we anticipate should be available
        required_vars = ['OPENAI_API_KEY']
        ## get all keys from the env
        self.api_keys = {key:os.getenv(key) for key in required_vars}
        ## listing out any api key which is missing
        missing = [k for k,v in self.api_keys.items() if not v]
        ## if any api key is missing will log and raise an exception
        
        if missing:
            self.log.error("Missing environment variables", missing_var= missing)