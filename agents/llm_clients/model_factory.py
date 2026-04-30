import os
from agents.llm_clients.openrouter_client import get_openrouter_model
from agents.llm_clients.openai_client import get_openai_model
from agents.llm_clients.google_client import get_google_model



def get_model(model_id: str = None):
    """
    Factory function to return an Agno model based on the LLM_PROVIDER in .env.
    Supports: 'openrouter', 'openai', 'google'.
    """
    provider = os.getenv("LLM_PROVIDER", "openrouter").lower()
    
    if provider == "openrouter":
        return get_openrouter_model(model_id)
    elif provider == "openai":
        return get_openai_model(model_id)
    elif provider == "google":
        return get_google_model(model_id)
    else:
        # Fallback to OpenRouter
        return get_openrouter_model(model_id)

def get_gpt4o_model():
    """Returns the orchestrator model configured via .env."""
    model_id = os.getenv("LLM_MODEL", "openai/gpt-4o")
    return get_model(model_id)

def get_vlm_model():
    """Returns the VLM specialist model. Defaults to orchestrator model if not specified."""
    # Note: If using Google provider, model_id should be something like 'gemini-2.0-flash-exp'
    model_id = os.getenv("LLM_MODEL", "openai/gpt-4o")
    return get_model(model_id)
