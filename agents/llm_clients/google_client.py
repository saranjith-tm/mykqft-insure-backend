import os
from agno.models.google import Gemini

def get_google_model(model_id: str):
    """Returns an Agno Gemini model configured for Google AI Studio."""
    return Gemini(
        id=model_id,
        api_key=os.getenv("LLM_MODEL_KEY"),
    )
