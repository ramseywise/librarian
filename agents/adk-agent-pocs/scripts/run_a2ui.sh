#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# ---------------------------------------------------------------------------
# run_a2ui.sh — start agent_gateway + agents/a2ui_mcp/web_client together
#
# Individual scripts:
#   ./scripts/run_agent_gateway.sh    (port 8000, override with GATEWAY_PORT)
#   ./scripts/run_a2ui_web_client.sh  (port 5173, override with CLIENT_PORT)
# ---------------------------------------------------------------------------

cleanup() {
  echo ""
  echo "Shutting down..."
  kill "$GATEWAY_PID" "$CLIENT_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

./scripts/run_agent_gateway.sh &
GATEWAY_PID=$!

./scripts/run_a2ui_web_client.sh &
CLIENT_PID=$!

echo ""
echo "  agent_gateway → http://localhost:${GATEWAY_PORT:-8000}"
echo "  web client    → http://localhost:${CLIENT_PORT:-5173}"
echo ""
echo "Press Ctrl+C to stop both services."

wait
