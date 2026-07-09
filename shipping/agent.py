import os

from google.adk.agents import Agent

from policymesh.config import settings

from .agents.inquiry import inquiry_agent
from .agents.shipping import shipping_agent

model = settings.model

# Helper to read prompt
def read_prompt(filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "prompts", filename)
    with open(file_path) as f:
        return f.read()

# Read instructions
orchestrator_instruction = read_prompt("agent-prompt.txt")

# Create Orchestrator
root_agent = Agent(
    name="shipping_orchestrator",
    description="Main orchestrator for shipping tasks.",
    model=model,
    instruction=orchestrator_instruction,
    sub_agents=[shipping_agent, inquiry_agent],
)
