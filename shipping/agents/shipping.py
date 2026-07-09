import os

# OrderStatus Enum for consistency with DB strings
from enum import Enum

from google.adk.agents import (
    Agent,
    LlmAgent,
    ParallelAgent,
    SequentialAgent,
)
from google.adk.tools.tool_context import ToolContext
from pydantic import BaseModel, Field

from policymesh.config import settings
from policymesh.toolbox import load_tool

from .products import products
from .rates import SHIPPING_RATES, TAX_RATES


class OrderStatus(Enum):
    PENDING = "pending"
    PLACED = "placed"
    PACKAGED = "packaged"
    SHIPPED = "shipped"
    RECEIVED = "received"

model = settings.model

def read_prompt(filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "../prompts", filename)
    with open(file_path) as f:
        return f.read()

get_order_tool = load_tool(os.environ.get("SHIPPING_GET_ORDER_TOOL", "get-order"), settings.shipping_toolbox_url)
get_open_order_tool = load_tool(
    os.environ.get("SHIPPING_GET_OPEN_ORDER_TOOL", "get-open-order-for-user"),
    settings.shipping_toolbox_url,
)
update_order_address_tool = load_tool(
    os.environ.get("SHIPPING_UPDATE_ORDER_ADDRESS_TOOL", "update-order-address"),
    settings.shipping_toolbox_url,
)
update_order_status_tool = load_tool(
    os.environ.get("SHIPPING_UPDATE_ORDER_STATUS_TOOL", "update-order-status"),
    settings.shipping_toolbox_url,
)
update_order_costs_tool = load_tool(
    os.environ.get("SHIPPING_UPDATE_ORDER_COSTS_TOOL", "update-order-costs"),
    settings.shipping_toolbox_url,
)

# --- Schemas ---

class ShippingCostOutput(BaseModel):
    shipping_cost: float = Field(description="The calculated shipping cost.")
    shipping_type: str = Field(description="The type of shipping used.")

class TaxCostOutput(BaseModel):
    tax_amount: float = Field(description="The calculated tax amount.")
    state: str = Field(description="The state used for tax calculation.")
    subtotal: float = Field(description="The subtotal of the order.")

class ComputeOrderOutput(BaseModel):
    order_id: str = Field(description="The ID of the order.")
    subtotal: float = Field(description="The order subtotal.")
    shipping_cost: float = Field(description="The shipping cost.")
    tax_amount: float = Field(description="The tax amount.")
    total_cost: float = Field(description="The final total cost.")
    order_status: str = Field(description="The status of the order.")

class AddressOutput(BaseModel):
    name: str
    address_1: str
    address_2: str | None = None
    city: str
    state: str
    postal_code: str

class PlaceOrderOutput(BaseModel):
    cart: list = Field(description="List of items in the cart.")
    address: AddressOutput = Field(description="The shipping address.")

# --- Tools ---

def get_user(tool_context: ToolContext):
    return {
        "user_id": tool_context.session.user_id,
    }

def calculate_shipping_cost(shipping_type: str = "standard") -> dict:
    """Calculates the shipping cost for an order.

    Args:
        shipping_type: The type of shipping (e.g., "standard", "express"). Defaults to "standard".
    """
    cost = SHIPPING_RATES.get(shipping_type.lower(), SHIPPING_RATES["standard"])
    return {"shipping_cost": cost, "shipping_type": shipping_type}

def calculate_taxes_cost(cart_items: list[str], state: str) -> dict:
    """Calculates the tax cost for an order based on the shipping state.

    Args:
        cart_items: A list of strings with the items in the cart
        state: The two-letter state code for tax calculation (e.g., "CA", "NY").
    """
    subtotal = 0.0
    for product_id in cart_items:
        if product_id in products:
            subtotal += products[product_id]["price"]

    rate = TAX_RATES.get(state.upper(), TAX_RATES["default"])
    tax_amount = subtotal * rate
    return {"tax_amount": round(tax_amount, 2), "state": state, "subtotal": subtotal}

def compute_subtotal(cart_items: list[str]) -> float:
    subtotal = 0.0
    for product_id in cart_items:
        if product_id in products:
            subtotal += products[product_id]["price"]
    return subtotal

def compute_order_cost(cart_items: list[str], shipping_cost: float, tax_amount: float) -> dict:
    """Compute the order cost by adding shipping and taxes, and updates the order.

    Args:
        cart_items: A list of strings with the items in the cart
        shipping_cost: The calculated shipping cost.
        tax_amount: The calculated tax amount.
    """
    subtotal = compute_subtotal(cart_items)
    total_cost = subtotal + shipping_cost + tax_amount
    
    return {
        "subtotal": round(subtotal, 2),
        "shipping_cost": shipping_cost,
        "tax_amount": tax_amount,
        "total_cost": round(total_cost, 2),
    }



# --- Sub-Agents --- 

shipping_cost_agent = LlmAgent(
    name="shipping_cost_agent",
    description="Calculates the shipping cost for an order.",
    model=model,
    instruction=read_prompt("shipping-cost-prompt.txt"),
    tools=[calculate_shipping_cost],
    output_schema=ShippingCostOutput,
)

taxes_cost_agent = LlmAgent(
    name="taxes_cost_agent",
    description="Calculates the tax amount for an order based on the destination state.",
    model=model,
    instruction=read_prompt("taxes-cost-prompt.txt"),
    tools=[calculate_taxes_cost],
    output_schema=TaxCostOutput,
)

costs_agent = ParallelAgent(
    name="other_costs_agent",
    description="Calculates shipping and taxes in parallel.",
    sub_agents=[shipping_cost_agent, taxes_cost_agent],
)

compute_order_agent = LlmAgent(
    name="compute_order_agent",
    description="Combines shipping and tax costs to compute the order total.",
    model=model,
    instruction=read_prompt("compute-order-prompt.txt"),
    tools=[compute_order_cost, update_order_costs_tool],
    output_schema=ComputeOrderOutput,
)

place_order_agent = LlmAgent(
    name="place_order_agent",
    description="Handles the initial placement of an order by setting the address.",
    model=model,
    instruction=read_prompt("place-order-prompt.txt"),
    tools=[get_user, get_order_tool, get_open_order_tool, update_order_address_tool],
    output_schema=PlaceOrderOutput,
)

order_summary_agent = LlmAgent(
    name="order_summary_agent",
    description="Summarizes the order details for the customer.",
    model=model,
    instruction=read_prompt("order-summary-prompt.txt"),
)

approve_order_agent = LlmAgent(
    name="approve_order_agent",
    description="Approves the order and sets status to PLACED upon user confirmation.",
    model=model,
    instruction=read_prompt("approve-order-prompt.txt"),
    tools=[update_order_status_tool],
)

# --- Main Shipping Agent ---

shipping_instruction = read_prompt("shipping-prompt.txt")

# The new full fulfillment workflow
fulfillment_workflow_agent = SequentialAgent(
    name="fulfillment_workflow",
    description="Calculates costs after an order is placed.",
    sub_agents=[
        place_order_agent,
        costs_agent,
        compute_order_agent,
        order_summary_agent,
    ],
)

# Main orchestrator for shipping domain
shipping_agent = Agent(
    name="shipping_agent",
    description="Handles all shipping related tasks: placing orders and calculating final costs.",
    model=model,
    instruction=shipping_instruction,
    sub_agents=[fulfillment_workflow_agent, approve_order_agent],
)
