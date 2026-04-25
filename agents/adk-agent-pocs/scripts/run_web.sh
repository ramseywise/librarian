#!/usr/bin/env bash
set -euo pipefail
# PYTHONPATH=. ensures the workspace root is on sys.path before ADK inserts
# agents/ — preventing agents/shared/ from shadowing the top-level shared/ package.
LOGLEVEL=${LOGLEVEL:-WARNING} PYTHONPATH=. uv run adk web agents/ --port 8000
