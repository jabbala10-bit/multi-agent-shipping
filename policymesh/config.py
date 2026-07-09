from __future__ import annotations

import os
from dataclasses import dataclass


def _env(name: str, default: str) -> str:
    value = os.environ.get(name)
    return value if value not in (None, "") else default


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value in (None, ""):
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    model: str = _env("POLICYMESH_MODEL", "gemini-2.5-flash")
    adk_host: str = _env("POLICYMESH_ADK_HOST", "127.0.0.1")
    adk_port: str = _env("POLICYMESH_ADK_PORT", "8000")
    toolbox_url: str = _env("TOOLBOX_URL", "http://127.0.0.1:5000")
    shopping_toolbox_url: str = _env("SHOPPING_TOOLBOX_URL", _env("TOOLBOX_URL", "http://127.0.0.1:5001"))
    shipping_toolbox_url: str = _env("SHIPPING_TOOLBOX_URL", _env("TOOLBOX_URL", "http://127.0.0.1:5000"))
    shopping_a2a_url: str = _env(
        "POLICYMESH_SHOPPING_A2A_URL",
        f"http://{_env('POLICYMESH_ADK_HOST', '127.0.0.1')}:{_env('POLICYMESH_ADK_PORT', '8000')}/a2a/shopping",
    )
    shipping_a2a_url: str = _env(
        "POLICYMESH_SHIPPING_A2A_URL",
        f"http://{_env('POLICYMESH_ADK_HOST', '127.0.0.1')}:{_env('POLICYMESH_ADK_PORT', '8000')}/a2a/shipping",
    )
    offline_tools: bool = _env_bool("POLICYMESH_OFFLINE_TOOLS", False)


settings = Settings()
