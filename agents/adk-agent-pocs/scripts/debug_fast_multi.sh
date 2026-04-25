#!/usr/bin/env bash
# Run fast_multi_agent_system with debugpy listening on port 5678.
# In VSCode: start this script, then attach with "Debug Fast Multi Agent (attach)".
set -euo pipefail
LOGLEVEL=DEBUG uv run python -m debugpy --listen 5678 --wait-for-client \
  -m google.adk.cli run agents/fast_multi_agent_system
