from agno.agent import Agent
from agents.llm_clients.model_factory import get_vlm_model
from agents.prompts.agent_prompts import VLM_SPECIALIST_DESCRIPTION, VLM_SPECIALIST_INSTRUCTIONS

def get_vlm_agent():
    """Returns an Agno agent configured for VLM tasks."""
    return Agent(
        model=get_vlm_model(),
        description=VLM_SPECIALIST_DESCRIPTION,
        instructions=VLM_SPECIALIST_INSTRUCTIONS,
        markdown=True,
    )
