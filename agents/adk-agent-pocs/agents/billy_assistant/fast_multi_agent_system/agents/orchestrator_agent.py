from pathlib import Path

from google.adk.agents import Agent
from google.adk.tools import AgentTool

from ..expert_registry import EXPERTS
from ..tools.context_tools import get_conversation_context, signal_follow_up

_instruction = (
    Path(__file__).parent.parent / "prompts" / "orchestrator_agent.txt"
).read_text()

# Helper AgentTools are built from the expert registry.
# To add a new expert helper, add an ExpertSpec to expert_registry.py.
_helper_tools = [AgentTool(agent=spec.helper_agent) for spec in EXPERTS]

orchestrator_agent = Agent(
    name="orchestrator_agent",
    model="gemini-2.5-flash",
    instruction=_instruction,
    tools=[get_conversation_context, signal_follow_up] + _helper_tools,
    output_key="public:final_answer",
)
