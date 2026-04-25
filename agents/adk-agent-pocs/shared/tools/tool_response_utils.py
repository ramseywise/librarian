from __future__ import annotations

from typing import Any


def extract_structured_content(tool_response: Any) -> Any | None:
    """Return structuredContent from a tool response when present."""
    if not isinstance(tool_response, dict):
        return None
    structured = tool_response.get("structuredContent")
    return structured if structured is not None else None


def prefer_structured_tool_response(
    tool: Any,
    args: dict,
    tool_context: Any,
    tool_response: Any,
) -> Any | None:
    """ADK after_tool_callback that prefers typed structuredContent output."""
    del tool, args, tool_context
    return extract_structured_content(tool_response)
