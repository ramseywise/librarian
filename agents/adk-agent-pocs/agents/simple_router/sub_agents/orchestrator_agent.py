from google.adk.agents import Agent
from google.adk.tools import AgentTool

from .._facts_callbacks import inject_facts_callback, persist_facts_callback
from .._history import strip_tool_history_callback
from ..expert_registry import (
    _THINKING_CONFIG,
    EXPERTS,
    build_domains_summary,
    load_prompt,
)
from ..tools import signal_follow_up


def _orchestrator_before_model_cb(
    callback_context,
    llm_request,
    _strip=strip_tool_history_callback,
    _inject=inject_facts_callback,
):
    # strip first (removes noise + stale facts), then inject fresh facts at end.
    result = _strip(callback_context, llm_request)
    if result is not None:
        return result
    return _inject(callback_context, llm_request)


def build_orchestrator_agent() -> Agent:
    """Build the orchestrator agent after all experts have been registered.

    Called from sub_agents/__init__.py once all register() calls are complete,
    so EXPERTS is fully populated and {domains} reflects every expert.
    """
    assert EXPERTS, (
        "No experts registered — check import order in sub_agents/__init__.py"
    )
    prompt = load_prompt("orchestrator_agent").replace(
        "{domains}", build_domains_summary()
    )
    return Agent(
        name="orchestrator_agent",
        model="gemini-3-flash-preview",
        description="Handles requests that span both invoice data and support/how-to guidance.",
        instruction=prompt,
        tools=[
            signal_follow_up,
            *[AgentTool(agent=spec.helper_agent) for spec in EXPERTS],
        ],
        generate_content_config=_THINKING_CONFIG,
        before_model_callback=_orchestrator_before_model_cb,
        after_agent_callback=persist_facts_callback,
        disallow_transfer_to_parent=True,
    )
