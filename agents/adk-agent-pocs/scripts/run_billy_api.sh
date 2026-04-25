#!/usr/bin/env bash
# Start the Billy stub REST API server.
# Required by: a2ui_mcp (browser fetches customer/product/invoice data directly)
# Listens on: http://127.0.0.1:8766  (override with API_HOST / API_PORT)
# Docs at:    http://127.0.0.1:8766/docs
set -euo pipefail
cd "$(dirname "$0")/../mcp_servers/billy"
echo "Starting Billy REST API at http://${API_HOST:-127.0.0.1}:${API_PORT:-8766}"
uv run python -m app.main
