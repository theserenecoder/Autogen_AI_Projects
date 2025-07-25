from autogen_ext.models.openai import OpenAIChatCompletionClient
from config.constant import MODEL_OPENAI
from dotenv import load_dotenv
import os
load_dotenv()

def getOpenAIModelClient():
    
    openai_model_client = OpenAIChatCompletionClient(
        model = MODEL_OPENAI,
        api_key=os.getenv('OPENAI_API_KEY')
    )
    return openai_model_client