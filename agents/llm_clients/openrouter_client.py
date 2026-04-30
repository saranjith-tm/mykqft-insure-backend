import os
from agno.models.openai import OpenAIChat

def get_openrouter_model(model_id: str):
    """Returns an Agno OpenAIChat model configured for OpenRouter with hardcoded base URL."""
    api_key = os.getenv("LLM_MODEL_KEY")
    
    # Compatibility fix: some internal Agno/OpenAI components check for this env var
    if api_key and not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = api_key

    return OpenAIChat(
        id=model_id,
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )
