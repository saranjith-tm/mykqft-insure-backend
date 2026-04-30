import os
from agno.models.openai import OpenAIChat

def get_openai_model(model_id: str):
    """Returns an Agno OpenAIChat model configured for native OpenAI."""
    return OpenAIChat(
        id=model_id,
        api_key=os.getenv("LLM_MODEL_KEY"),
    )
