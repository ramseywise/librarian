"""Agent registry — maps agent name to ADK root_agent.

To add a new agent: add an entry to AGENT_DESCRIPTIONS and a branch in get_agent().
No other server files need to change.
"""

from __future__ import annotations

from typing import Any

AGENT_DESCRIPTIONS: dict[str, str] = {
    "a2ui_mcp": "Billy accounting assistant with A2UI-powered surfaces",
}


def get_agent(name: str) -> Any:
    """Return the root_agent for the given agent name (lazy import)."""
    if name == "a2ui_mcp":
        from agents.a2ui_mcp.app import app  # noqa: PLC0415

        return app
    raise ValueError(f"Unknown agent: {name!r}")
