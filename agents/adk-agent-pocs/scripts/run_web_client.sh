#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
# Free port 3000 if a stale process is holding it
if lsof -ti :3000 &>/dev/null; then
  echo "Freeing port 3000 (stale process: $(lsof -ti :3000))"
  kill "$(lsof -ti :3000)" 2>/dev/null || true
  sleep 0.5
fi
echo "Open http://localhost:3000 in your browser (not 0.0.0.0 — microphone requires localhost)"
echo "Starting ADK web client at http://localhost:3000"
uv run web_client/server.py
