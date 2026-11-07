"""The agent layer: one tool registry (`tools`) and the Anthropic tool-use loop (`loop`).

`librarian.api` streams `run_agent_stream` to the chat panel; `librarian.mcp` registers the same
registry's MCP variants. See `tools` for how a tool is defined.
"""

from librarian.agent.loop import run_agent_stream
from librarian.agent.tools import TOOLS, Tool, ToolContext, tools_for

__all__ = ["TOOLS", "Tool", "ToolContext", "run_agent_stream", "tools_for"]
