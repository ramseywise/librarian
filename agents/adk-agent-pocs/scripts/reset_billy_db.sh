#!/usr/bin/env bash
# Reset billy.db and reseed it with mock data.
# Usage: ./reset_billy_db.sh [--db PATH]
set -euo pipefail
cd "$(dirname "$0")/../mcp_servers/billy"
uv run python reset_db.py "$@"
