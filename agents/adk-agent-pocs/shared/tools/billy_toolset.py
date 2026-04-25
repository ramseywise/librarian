"""Shared lazy-init accessor for the Billy MCP toolset.

Agents that talk to the Billy MCP server import `get_billy_toolset` and pass
it as the `get_toolset` argument to `make_skill_tools`, or use it directly
wherever a `McpToolset` reference is needed.

Connection strategy (controlled by the BILLY_MCP_URL env var):
- Set BILLY_MCP_URL (e.g. "http://127.0.0.1:8765/sse") to connect to an
  already-running server via SSE — useful during local development / debugging.
- Leave it unset to spawn the server as a stdio subprocess automatically.
"""

import os
import pathlib

from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    SseConnectionParams,
    StdioConnectionParams,
)
from mcp import StdioServerParameters

_BILLY_MCP_DIR = str(
    pathlib.Path(__file__).parent.parent.parent / "mcp_servers" / "billy"
)

_billy_toolset: McpToolset | None = None


def create_billy_toolset(tool_filter: list[str] | None = None) -> McpToolset:
    """Create a new Billy McpToolset, optionally filtered to specific tool names."""
    billy_mcp_url = os.getenv("BILLY_MCP_URL")
    if billy_mcp_url:
        return McpToolset(
            connection_params=SseConnectionParams(url=billy_mcp_url),
            tool_filter=tool_filter,
        )
    return McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="uv",
                args=["run", "python", "-m", "app.main_noauth"],
                cwd=_BILLY_MCP_DIR,
            ),
        ),
        tool_filter=tool_filter,
    )


def get_billy_toolset() -> McpToolset:
    """Return the shared Billy McpToolset (all tools), creating it on first call."""
    global _billy_toolset
    if _billy_toolset is None:
        _billy_toolset = create_billy_toolset()
    return _billy_toolset
