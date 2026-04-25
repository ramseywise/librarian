import sys
from pathlib import Path

_agents_dir = Path(__file__).parent.parent.parent.parent
if str(_agents_dir) not in sys.path:
    sys.path.insert(0, str(_agents_dir))

from simple_router.sub_agents import orchestrator_agent as _agent  # noqa: E402

root_agent = _agent
