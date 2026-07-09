from __future__ import annotations

import sys
import types


class _FakeAgent:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    async def run_async(self, context):
        if False:
            yield context


def _install_fake_google_adk() -> None:
    if "google.adk.agents" in sys.modules:
        return

    google = sys.modules.setdefault("google", types.ModuleType("google"))
    adk = types.ModuleType("google.adk")
    agents = types.ModuleType("google.adk.agents")
    events = types.ModuleType("google.adk.events")
    tools = types.ModuleType("google.adk.tools")
    tool_context = types.ModuleType("google.adk.tools.tool_context")
    remote = types.ModuleType("google.adk.agents.remote_a2a_agent")

    class ToolContext:
        def __init__(self):
            self.state = {}
            self.session = types.SimpleNamespace(user_id="test-user")

    class RemoteA2aAgent(_FakeAgent):
        pass

    agents.Agent = _FakeAgent
    agents.LlmAgent = _FakeAgent
    agents.BaseAgent = _FakeAgent
    agents.SequentialAgent = _FakeAgent
    agents.ParallelAgent = _FakeAgent
    agents.InvocationContext = object
    events.Event = object
    tools.ToolContext = ToolContext
    tool_context.ToolContext = ToolContext
    remote.RemoteA2aAgent = RemoteA2aAgent
    remote.AGENT_CARD_WELL_KNOWN_PATH = "/.well-known/agent-card.json"

    google.adk = adk
    adk.agents = agents
    adk.events = events
    adk.tools = tools

    sys.modules["google.adk"] = adk
    sys.modules["google.adk.agents"] = agents
    sys.modules["google.adk.events"] = events
    sys.modules["google.adk.tools"] = tools
    sys.modules["google.adk.tools.tool_context"] = tool_context
    sys.modules["google.adk.agents.remote_a2a_agent"] = remote


def pytest_configure():
    _install_fake_google_adk()
