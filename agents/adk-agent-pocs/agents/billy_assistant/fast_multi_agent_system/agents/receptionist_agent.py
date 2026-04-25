from pathlib import Path

from google.adk.agents import Agent

from ..expert_registry import EXPERTS
from ..state import REROUTE_ALL
from ..tools.context_tools import request_reroute, signal_follow_up

# One routing line per expert, using reroute_reason as the exact value the model must emit.
_expert_routing_lines = "\n".join(
    f'  "{spec.reroute_reason}"  — {spec.description}' for spec in EXPERTS
)

_template = (
    Path(__file__).parent.parent / "prompts" / "receptionist_agent.txt"
).read_text()

INSTRUCTION = _template.format(
    **REROUTE_ALL, expert_routing_lines=_expert_routing_lines
)

receptionist_agent = Agent(
    name="receptionist_agent",
    model="gemini-2.5-flash",
    instruction=INSTRUCTION,
    tools=[signal_follow_up, request_reroute],
    output_key="public:last_agent_summary",
    # include_contents='default' — needs conversation history for natural greetings
)
