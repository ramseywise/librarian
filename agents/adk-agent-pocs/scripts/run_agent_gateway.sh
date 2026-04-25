#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

PORT=${GATEWAY_PORT:-8000}
BILLY_MCP_URL=${BILLY_MCP_URL:-http://127.0.0.1:8765/sse}
export BILLY_MCP_URL

if lsof -ti :"$PORT" &>/dev/null; then
  echo "Freeing port $PORT (stale process: $(lsof -ti :"$PORT"))"
  kill "$(lsof -ti :"$PORT")" 2>/dev/null || true
  sleep 0.3
fi

echo "Starting agent_gateway on http://localhost:$PORT"
uv run uvicorn agent_gateway.main:app --reload --port "$PORT"
