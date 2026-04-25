# Domain expert modules are imported here to trigger their register() calls.
# All experts MUST be imported before build_orchestrator_agent() is called —
# it reads EXPERTS to build the helper tool list and inject {domains}.
# To add a new expert: import it here, in alphabetical order, before the factory call.
from ....simple_router.sub_agents import invoice_agent as _  # noqa: F401
from ....simple_router.sub_agents import support_agent as _  # noqa: F401

from ..expert_registry import get_direct
from .orchestrator_agent import build_orchestrator_agent
from .receptionist_agent import receptionist_agent

# Build orchestrator now that all experts are registered.
orchestrator_agent = build_orchestrator_agent()

# Named exports built from the registry — no manual assignments in expert files.
invoice_agent = get_direct("invoice_agent")
support_agent = get_direct("support_agent")

__all__ = ["invoice_agent", "orchestrator_agent", "receptionist_agent", "support_agent"]
