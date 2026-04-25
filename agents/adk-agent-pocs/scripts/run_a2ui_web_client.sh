#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

PORT=${CLIENT_PORT:-5173}

if lsof -ti :"$PORT" &>/dev/null; then
  echo "Freeing port $PORT (stale process: $(lsof -ti :"$PORT"))"
  kill "$(lsof -ti :"$PORT")" 2>/dev/null || true
  sleep 0.3
fi

if [[ ! -d agents/a2ui_mcp/web_client/node_modules ]]; then
  echo "node_modules not found — running npm install in agents/a2ui_mcp/web_client/"
  (cd agents/a2ui_mcp/web_client && npm install)
fi

echo "Starting a2ui_web_client on http://localhost:$PORT"
cd agents/a2ui_mcp/web_client && npm run dev -- --port "$PORT"
