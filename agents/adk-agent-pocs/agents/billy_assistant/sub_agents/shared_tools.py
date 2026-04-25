"""Shared tools and config included in every Billy subagent."""

from google.adk.tools import ToolContext
from google.genai import types

THINKING_CONFIG = types.GenerateContentConfig(
    temperature=0,
    thinking_config=types.ThinkingConfig(thinking_budget=-1, include_thoughts=True),
)

# SUPPORT_THINKING_CONFIG = types.GenerateContentConfig(
#     temperature=0.2,
#     thinking_config=types.ThinkingConfig(thinking_budget=1024, include_thoughts=True),
# )

SUPPORT_THINKING_CONFIG = types.GenerateContentConfig(
    temperature=0.2,
    thinking_config=types.ThinkingConfig(thinking_budget=0),
)


def report_out_of_domain(tool_context: ToolContext) -> str:
    """Call this when the request is outside your domain. Registers this agent
    as already tried so the router does not route back to it, then transfers
    control to billy_assistant."""
    agent_name = tool_context._invocation_context.agent.name
    tried = tool_context.state.get("tried_agents", [])
    if agent_name not in tried:
        tried = tried + [agent_name]
        tool_context.state["tried_agents"] = tried
    tool_context.actions.transfer_to_agent = "billy_assistant"
    return f"Registered {agent_name} as out-of-domain. Transferring to billy_assistant."
