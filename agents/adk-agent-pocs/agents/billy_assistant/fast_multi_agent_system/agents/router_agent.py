from pathlib import Path

from google.adk.agents import Agent
from pydantic import BaseModel

from ..expert_registry import EXPERTS
from .orchestrator_agent import orchestrator_agent
from .receptionist_agent import receptionist_agent

# All template substitutions in one place.
# Expert agent names are injected by name so examples stay in sync with the registry.
# {{public:last_answer}} in the template is escaped so Python outputs the literal
# {public:last_answer} placeholder that ADK resolves at runtime.
_substitutions = {
    "expert_descriptions": "\n".join(
        f"  {spec.name}  — {spec.description}" for spec in EXPERTS
    ),
    "orchestrator_agent": orchestrator_agent.name,
    "receptionist_agent": receptionist_agent.name,
    **{spec.name: spec.name for spec in EXPERTS},
}

_template = (Path(__file__).parent.parent / "prompts" / "router_agent.txt").read_text()

INSTRUCTION = _template.format(**_substitutions)


class LlmRouteOutput(BaseModel):
    # str rather than Literal so the valid set stays dynamic (validated by root agent).
    selected_agent: str
    reason: str


llm_router_agent = Agent(
    name="llm_router",
    model="gemini-3.1-flash-lite-preview",
    instruction=INSTRUCTION,
    output_schema=LlmRouteOutput,
    include_contents="none",
)
