from policymesh.toolbox import offline_tool
from shopping.agents.cart import add_to_cart, get_order
from shopping.agents.inventory import check_inventory


class _ToolContext:
    def __init__(self):
        self.state = {}


def test_offline_tool_is_deterministic():
    tool = offline_tool("search-products")

    assert tool(search="headphones") == {
        "tool": "search-products",
        "offline": True,
        "arguments": {"search": "headphones"},
        "message": "Toolbox is disabled for this process.",
    }


def test_inventory_unknown_product_returns_error():
    assert check_inventory("NOPE") == {"error": "Product ID not found"}


def test_cart_flow_creates_order_then_adds_product():
    context = _ToolContext()

    order = get_order(context)
    result = add_to_cart("P001", context)

    assert order["order_id"].startswith("ORDER_")
    assert result["status"] == "success"
    assert "P001" in result["cart"]
