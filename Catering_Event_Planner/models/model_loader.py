import asyncio
from autogen_ext.models.openai import OpenAIChatCompletionClient

from utils.config_loader import load_config
from logger.custom_logger import CustomLogger
from exception.custom_exception import CustomException

from dotenv import load_dotenv
import os
import sys


class ModelLoader():
    """ A class to load llm models"""
    def __init__(self):
        self.log = CustomLogger().get_logger(__name__)
        load_dotenv()
        self._validate_env()
        ## loading the config
        self.config = load_config()
        self.log.info("Configuration loaded sucessfully", config_keys=list(self.config.keys()))
        
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
            raise CustomException("Missing environment variables", sys)
        
        self.log.info("Environment variables validated", available_keys=[k for k in self.api_keys if self.api_keys[k]])
        
    def load_llm(self):
        """Load and return llm model"""
        try:
            self.log.info('Loading LLM model')
            
            llm_block = self.config['llm_config']
            
            provider_key = os.getenv('LLM_PROVIDER','openai')
            
            if provider_key not in llm_block:
                self.log.error('LLM provider not found in config',provider_key = provider_key)
                raise ValueError(f"Provider '{provider_key}' not found in config")
            
            llm_config = llm_block[provider_key]
            provider = llm_config.get('provider')
            model_name = llm_config.get('model_name')
            
            self.log.info("Loading LLM", provider=provider, model_name=model_name)
            
            if provider == 'openai':
                model_client = OpenAIChatCompletionClient(
                    model=model_name,
                    #api_key=self.api_keys['OPENAI_API_KEY']
                )
            
            return model_client
        
        except Exception as e:
            self.log.error("Error loading LLM", provider=provider, model_name=model_name)
            raise CustomException("Error loading LLM",sys)
        
if __name__ == '__main__':
    from autogen_core.models import UserMessage
    async def run_code():
        loader = ModelLoader()
        llm = loader.load_llm()
        result = await llm.create([UserMessage(content='Hi How are you', source='user')])
        print(result)
        await llm.close()
    
    asyncio.run(run_code())
    