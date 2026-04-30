from agno.agent import Agent
from agents.llm_clients.model_factory import get_gpt4o_model
from agents.prompts.agent_prompts import ORCHESTRATOR_DESCRIPTION, ORCHESTRATOR_INSTRUCTIONS
from agents.tools.azure_client import extract_with_azure
from agents.tools.azure_processor import process_azure_result

def get_orchestrator_agent():
    """Returns an Agno agent that orchestrates the document extraction process."""
    return Agent(
        model=get_gpt4o_model(),
        description=ORCHESTRATOR_DESCRIPTION,
        instructions=ORCHESTRATOR_INSTRUCTIONS,
        tools=[extract_with_azure, process_azure_result],
        markdown=True,
    )
