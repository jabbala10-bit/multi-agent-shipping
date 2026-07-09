from __future__ import annotations

import importlib


def test_shopping_agent_imports_with_expected_sub_agents(monkeypatch):
    monkeypatch.setenv("POLICYMESH_OFFLINE_TOOLS", "1")

    module = importlib.import_module("shopping.agent")

    assert module.root_agent.name == "shopping_orchestrator"
    sub_agent_names = {agent.name for agent in module.root_agent.sub_agents}
    assert {"search_agent_router", "inventory_agent", "cart_agent", "product_qa_agent"} <= sub_agent_names


def test_shipping_agent_imports_with_expected_sub_agents(monkeypatch):
    monkeypatch.setenv("POLICYMESH_OFFLINE_TOOLS", "1")

    module = importlib.import_module("shipping.agent")

    assert module.root_agent.name == "shipping_orchestrator"
    sub_agent_names = {agent.name for agent in module.root_agent.sub_agents}
    assert {"shipping_agent", "shipping_inquiry_agent"} <= sub_agent_names


def test_storefront_agent_uses_configured_remote_cards(monkeypatch):
    monkeypatch.setenv("POLICYMESH_OFFLINE_TOOLS", "1")

    module = importlib.import_module("storefront.agent")

    assert module.root_agent.name == "storefront_agent"
    card_urls = {agent.agent_card for agent in module.root_agent.sub_agents}
    assert any(url.endswith("/a2a/shopping/.well-known/agent-card.json") for url in card_urls)
    assert any(url.endswith("/a2a/shipping/.well-known/agent-card.json") for url in card_urls)
