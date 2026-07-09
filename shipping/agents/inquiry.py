import os

from google.adk.agents import Agent

from policymesh.config import settings
from policymesh.toolbox import load_tool

model = settings.model

def read_prompt(filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "../prompts", filename)
    with open(file_path) as f:
        return f.read()

get_order_tool = load_tool(os.environ.get("SHIPPING_GET_ORDER_TOOL", "get-order"), settings.shipping_toolbox_url)

inquiry_instruction = read_prompt("inquiry-prompt.txt")

inquiry_agent = Agent(
    name="shipping_inquiry_agent",
    description="Handles questions about shipping policies and tracking.",
    model=model,
    instruction=inquiry_instruction,
    tools=[get_order_tool],
)
