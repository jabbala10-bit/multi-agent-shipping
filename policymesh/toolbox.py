from __future__ import annotations

import logging
import os
from collections.abc import Callable
from functools import lru_cache
from typing import Any

from policymesh.config import settings

LOGGER = logging.getLogger(__name__)


def offline_tool(name: str) -> Callable[..., dict[str, Any]]:
    """Return a deterministic placeholder tool for import-time smoke tests."""

    def _tool(**kwargs: Any) -> dict[str, Any]:
        return {
            "tool": name,
            "offline": True,
            "arguments": kwargs,
            "message": "Toolbox is disabled for this process.",
        }

    _tool.__name__ = name.replace("-", "_")
    _tool.__doc__ = f"Offline placeholder for the Toolbox tool '{name}'."
    return _tool


@lru_cache(maxsize=8)
def _client(toolbox_url: str) -> Any:
    from toolbox_core import ToolboxSyncClient

    LOGGER.info("Connecting to Toolbox at %s", toolbox_url)
    return ToolboxSyncClient(toolbox_url)


def load_tool(tool_name: str, toolbox_url: str | None = None) -> Callable[..., Any]:
    """Load a Toolbox tool, with an explicit offline mode for tests and docs builds."""

    offline_tools = os.environ.get("POLICYMESH_OFFLINE_TOOLS", "").lower() in {"1", "true", "yes", "on"}
    if settings.offline_tools or offline_tools:
        return offline_tool(tool_name)

    try:
        return _client(toolbox_url or settings.toolbox_url).load_tool(tool_name)
    except Exception:
        if os.environ.get("POLICYMESH_ALLOW_TOOLBOX_FALLBACK", "").lower() in {"1", "true", "yes"}:
            LOGGER.exception("Falling back to offline placeholder for Toolbox tool %s", tool_name)
            return offline_tool(tool_name)
        raise
