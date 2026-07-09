import os

from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH, RemoteA2aAgent

from policymesh.config import settings

model = settings.model

def read_prompt(filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "prompts", filename)
    with open(file_path) as f:
        return f.read()

shipping_agent = RemoteA2aAgent(
    name="shipping_agent",
    agent_card=f"{settings.shipping_a2a_url}{AGENT_CARD_WELL_KNOWN_PATH}"
)

shopping_agent = RemoteA2aAgent(
    name="shopping_agent",
    agent_card=f"{settings.shopping_a2a_url}{AGENT_CARD_WELL_KNOWN_PATH}"
)

storefront_instruction = read_prompt("agent-prompt.txt")

root_agent = Agent(
    name="storefront_agent",
    description="Main storefront orchestrator.",
    model=model,
    instruction=storefront_instruction,
    sub_agents=[shipping_agent, shopping_agent],
)
