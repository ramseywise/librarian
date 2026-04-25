#!/usr/bin/env bash
# Start the Billy stub MCP server in HTTP/SSE mode.
# Required by: dynamic_skill_mcp, skill_assistant_mcp
# Listens on: http://127.0.0.1:8765/sse  (override with MCP_HOST / MCP_PORT)
set -euo pipefail
cd "$(dirname "$0")/../mcp_servers/billy"
echo "Starting Billy MCP server at http://${MCP_HOST:-127.0.0.1}:${MCP_PORT:-8765}/sse"
uv run python -m app.main_noauth --http
