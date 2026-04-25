import sys
from pathlib import Path

# Ensure simple_router is importable regardless of how ADK modifies sys.path.
# ADK adds the parent of this directory (eval_apps/) to sys.path when running
# `adk eval eval_apps/invoice_agent`, but we need the agents/ directory.
_agents_dir = Path(__file__).parent.parent.parent.parent
if str(_agents_dir) not in sys.path:
    sys.path.insert(0, str(_agents_dir))

from simple_router.sub_agents import invoice_agent as _agent  # noqa: E402

root_agent = _agent
