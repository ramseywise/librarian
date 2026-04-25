from google.adk.agents import Agent

from ..callbacks import receptionist_before_model_callback
from ..expert_registry import load_prompt
from ..tools import signal_follow_up

_PROMPT = load_prompt("receptionist_agent")

receptionist_agent = Agent(
    name="receptionist_agent",
    model="gemini-3.1-flash-lite-preview",
    description=(
        "Handles greetings, general questions, onboarding, and any topic not "
        "covered by invoice_agent or support_agent."
    ),
    instruction=_PROMPT,
    tools=[signal_follow_up],
    include_contents="none",
    before_model_callback=receptionist_before_model_callback,
    # Prevent ADK from resuming this agent on the next user turn.
    # All router sub-agents must set this so _find_agent_to_run always
    # falls back to the router (root_agent) between turns.
    disallow_transfer_to_parent=True,
)
