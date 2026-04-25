"""Billy MCP client factory for the native_skill_mcp LangGraph agent.

Usage (in agent.py entrypoint):

    async with build_mcp_client() as client:
        billy_tools = await load_all_billy_tools(client)
        graph = build_graph(billy_tools)
        # ... run graph
"""

from __future__ import annotations

import os
import pathlib

BILLY_MCP_DIR = pathlib.Path(__file__).parent.parent.parent / "mcp_servers" / "billy"


def build_mcp_client():
    """Return a MultiServerMCPClient configured for the Billy MCP server.

    In langchain-mcp-adapters >= 0.1.0 the client is NOT a context manager.
    Just call `await client.get_tools()` after constructing it.

    Connection strategy:
    - Set BILLY_MCP_URL (e.g. "http://127.0.0.1:8765/sse") to connect via SSE.
    - Leave unset to spawn the server as a stdio subprocess (default for local dev).
    """
    from langchain_mcp_adapters.client import MultiServerMCPClient  # noqa: PLC0415

    billy_mcp_url = os.getenv("BILLY_MCP_URL")
    if billy_mcp_url:
        transport: dict = {"url": billy_mcp_url, "transport": "sse"}
    else:
        transport = {
            "command": "uv",
            "args": ["run", "python", "-m", "app.main_noauth"],
            "cwd": str(BILLY_MCP_DIR),
            "transport": "stdio",
        }
    return MultiServerMCPClient({"billy": transport})


async def load_all_billy_tools(client) -> dict:
    """Load all Billy MCP tools and return as a dict keyed by tool name.

    In langchain-mcp-adapters >= 0.1.0, MultiServerMCPClient is NOT a context
    manager — just call get_tools() directly after constructing the client.
    """
    tools = await client.get_tools()
    return {t.name: t for t in tools}
