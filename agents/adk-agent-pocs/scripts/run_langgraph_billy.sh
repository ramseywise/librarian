#!/usr/bin/env bash
# Run the Billy LangGraph agent (native_skill_mcp) as an interactive REPL.
# Requires: GOOGLE_API_KEY set in .env or environment.
# Billy MCP:  set BILLY_MCP_URL to connect to a running server (SSE),
#             or leave unset to spawn the stdio subprocess automatically.
set -euo pipefail
cd "$(dirname "$0")/.."
uv run python -m langgraph_agents.native_skill_mcp.agent
