from autogen_ext.models.openai import OpenAIChatCompletionClient
from config.constant import MODEL_OPENAI
from dotenv import load_dotenv
import os
load_dotenv()
from autogen_core.models import UserMessage

def getOpenAIModelClient():
    
    openai_model_client = OpenAIChatCompletionClient(
        model = MODEL_OPENAI,
        api_key=os.getenv('OPENAI_API_KEY')
    )
    return openai_model_client



if __name__=='__main__':
    print("\n")
    load_dotenv()
    print("Current working directory:", os.getcwd())
    print("OPENAI_API_KEY:", os.getenv('OPENAI_API_KEY'))
    print("\n")
    import asyncio
    async def run_model():
        model = getOpenAIModelClient()
        result = await model.create([UserMessage(content='What is the full form of RCB', source='user')])
        print(result)
        await model.close()
    
    asyncio.run(run_model())