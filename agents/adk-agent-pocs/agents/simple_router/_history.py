# _history.py
# Standalone callback — no imports from local modules, so it can be imported
# by expert_registry.py and orchestrator_agent.py without circular deps.

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.genai import types

# LlmRequest is in google.adk.models alongside LlmResponse
try:
    from google.adk.models import LlmRequest
except ImportError:
    from google.adk.models.llm_request import LlmRequest


def _is_router_context_msg(content) -> bool:
    """Return True for ADK 'For context:' messages injected by the parent router.

    When the router transfers to a sub-agent, ADK inserts the router's tool call
    history as plain-text user messages whose first part is literally 'For context:'.
    These are noise for the expert LLM and should always be stripped.
    """
    if getattr(content, "role", None) != "user":
        return False
    parts = getattr(content, "parts", None) or []
    texts = [getattr(p, "text", None) for p in parts if getattr(p, "text", None)]
    return bool(texts) and texts[0] == "For context:"


def _is_session_facts_msg(content) -> bool:
    """Return True for injected '[session facts: ...]' user messages.

    These are added by inject_facts_callback each turn and must be stripped from
    prior turns before a fresh injection is appended for the current turn.
    """
    if getattr(content, "role", None) != "user":
        return False
    parts = getattr(content, "parts", None) or []
    texts = [getattr(p, "text", None) for p in parts if getattr(p, "text", None)]
    return bool(texts) and texts[0].startswith("[session facts:")


def _is_real_user_text(content) -> bool:
    """True only for genuine user text messages.

    Excludes 'For context:' router noise and '[session facts:' injections so
    that strip_tool_history_callback can reliably identify the current turn
    boundary without being confused by synthetic content.
    """
    if getattr(content, "role", None) != "user":
        return False
    texts = [
        getattr(p, "text", None)
        for p in (getattr(content, "parts", None) or [])
        if getattr(p, "text", None)
    ]
    if not texts:
        return False
    first = texts[0]
    return first != "For context:" and not first.startswith("[session facts:")


def strip_tool_history_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> LlmResponse | None:
    """Clean the LLM request contents before each expert agent LLM call.

    Two passes (runs BEFORE inject_facts_callback in the callback chain):

    Pass 1 — remove noise from any position:
      - ADK 'For context:' router messages (injected when parent router transfers)
      - Stale '[session facts:]' messages from prior turns
        (a fresh one will be appended by inject_facts_callback after this runs)

    Pass 2 — strip tool call artefacts from prior turns:
      - Finds the last *real* user text message (ignoring 'For context:' and
        '[session facts:' items) to establish the current-turn boundary.
      - Removes function_call and function_response parts from all prior turns.
      - Stale '[session facts:]' items in prior turns are also dropped here
        (belt-and-suspenders, in case Pass 1 misses edge cases).

    Current-turn items (at and after last_real_user_idx) are preserved so
    multi-step tool-call sequences within one turn continue to work.
    """
    contents = llm_request.contents
    if not contents:
        return None

    # Pass 1: remove 'For context:' noise and stale '[session facts:]' items.
    # These are always safe to drop from any position:
    #   - 'For context:' messages are router implementation details.
    #   - '[session facts:]' items from prior turns are superseded; a fresh
    #     injection will be appended by inject_facts_callback momentarily.
    contents = [
        c
        for c in contents
        if not _is_router_context_msg(c) and not _is_session_facts_msg(c)
    ]

    # Find the last real user text message to establish the turn boundary.
    last_real_idx = next(
        (
            i
            for i in range(len(contents) - 1, -1, -1)
            if _is_real_user_text(contents[i])
        ),
        -1,
    )
    if last_real_idx <= 0:
        # Nothing in prior turns to process; save Pass 1 changes and return.
        llm_request.contents = contents
        return None

    # Pass 2: strip function_call/function_response parts from prior turns.
    cleaned = []
    for i, content in enumerate(contents):
        if i >= last_real_idx:
            cleaned.append(content)
            continue
        filtered = [
            p
            for p in (getattr(content, "parts", None) or [])
            if not getattr(p, "function_call", None)
            and not getattr(p, "function_response", None)
            and not getattr(p, "thought", None)
            and (getattr(p, "text", None) or not getattr(p, "thought_signature", None))
        ]
        if filtered:
            cleaned.append(types.Content(role=content.role, parts=filtered))

    llm_request.contents = cleaned
    return None
