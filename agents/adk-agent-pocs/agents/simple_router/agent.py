import os

from google.adk.agents import Agent
from google.genai import types as _genai_types

from ._facts_callbacks import router_force_context_callback
from .callbacks import router_before_model_callback
from agents.shared.debug import attach
from .expert_registry import load_prompt
from .sub_agents import (
    invoice_agent,
    orchestrator_agent,
    receptionist_agent,
    support_agent,
)
from .tools import get_conversation_context

_DEBUG = os.getenv("SIMPLE_ROUTER_DEBUG", "0") == "1"

_PROMPT = load_prompt("router_agent")

# ── Router agent ──────────────────────────────────────────────────────────────
# Pure classifier — never answers the user directly.
#
# Prefix caching optimizations:
#   1. Fully static instruction (no {state_key} placeholders) → Gemini caches
#      the system-prompt prefix across every routing call.
#   2. include_contents="none" → router sees only the current message, keeping
#      the cached prefix intact and routing fast.
#   3. Single tool (get_conversation_context) checks for a registered follow_up_agent
#      before routing, so signal_follow_up() works across turns.
#   4. before_model_callback=router_before_model_callback → chains two shortcuts:
#      a) follow_up_shortcut: short-circuits the LLM for clear follow-up answers
#         (bare IDs, yes/no, short fragments), saving one flash-lite call per turn.
#      b) static_route_shortcut: keyword scoring (routing.py) bypasses the LLM for
#         high-confidence single-domain messages; a re-route guard prevents loops.
#   5. after_model_callback=router_force_context_callback → intercepts any
#      direct transfer_to_agent response that skipped get_conversation_context,
#      replacing it with the context call so the trajectory is always correct.
#   6. generate_content_config(thinking_budget=0) → thinking disabled. The router
#      is a pure classifier with no multi-step reasoning requirement; thinking adds
#      latency and token cost with no quality benefit.

router_agent = attach(
    Agent(
        name="router_agent",
        model="gemini-3.1-flash-lite-preview",
        description="Routes every user message to the appropriate agent.",
        instruction=_PROMPT,
        generate_content_config=_genai_types.GenerateContentConfig(
            thinking_config=_genai_types.ThinkingConfig(thinking_budget=0)
        ),
        sub_agents=[
            attach(orchestrator_agent, debug=_DEBUG),
            # invoice_agent and support_agent are direct variants built by expert_registry.py.
            # Their *_helper counterparts (invoice_agent_helper, support_agent_helper) are
            # separate AgentTool instances used only by orchestrator_agent — they do not appear
            # in this list but will show up in debug traces.
            attach(invoice_agent, debug=_DEBUG),
            attach(support_agent, debug=_DEBUG),
            attach(receptionist_agent, debug=_DEBUG),
        ],
        tools=[get_conversation_context],
        include_contents="none",
        before_model_callback=router_before_model_callback,
        after_model_callback=router_force_context_callback,
    ),
    debug=_DEBUG,
)

root_agent = router_agent
