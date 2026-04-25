# _facts_callbacks.py
# Expert-agent callbacks for the fact lifecycle.
#
#   inject_facts_callback           — before_model_callback on all expert agents.
#                                     Reads public:session_facts, handles early persistence
#                                     (persist_now=True), and appends a "[session facts: {...}]"
#                                     user text message after the last real user message so
#                                     the LLM always sees the current facts.  The system
#                                     instruction is NOT modified — keeping it stable for
#                                     prefix caching.  No invocation guard needed —
#                                     strip_tool_history_callback removes prior injections.
#
#   persist_facts_callback          — after_agent_callback on all expert agents.
#                                     Moves 'draft' facts from public:session_facts
#                                     into public:fact_history and marks them 'persisted'.
#
#   router_force_context_callback   — after_model_callback on the router agent.
#                                     Intercepts direct transfer_to_agent responses that
#                                     bypassed get_conversation_context, replacing them
#                                     with a get_conversation_context call so the tool is
#                                     always executed before routing.

from __future__ import annotations

import json
import uuid

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.genai import types

try:
    from google.adk.models import LlmRequest
except ImportError:
    from google.adk.models.llm_request import LlmRequest

from .tools.context_tools import (
    PRIOR_FOLLOW_UP_KEY,
    PUBLIC_FACT_HISTORY,
    PUBLIC_SESSION_FACTS,
    _CTX_LOADED_KEY,
    _flat_facts,
)


# ── Shared helpers ─────────────────────────────────────────────────────────────


def _persist_drafts(callback_context: CallbackContext) -> None:
    """Move all draft facts into history and mark them persisted."""
    session_facts = dict(callback_context.state.get(PUBLIC_SESSION_FACTS, {}))
    history = list(callback_context.state.get(PUBLIC_FACT_HISTORY, []))
    changed = False

    for key, entry in session_facts.items():
        if not isinstance(entry, dict) or entry.get("status") != "draft":
            continue
        new_fact_id = str(uuid.uuid4())
        old_fact_id = entry.get("fact_id")
        history.append(
            {
                "fact_id": new_fact_id,
                "supersedes_fact_id": old_fact_id,
                "key": key,
                "description": entry.get("description", key),
                "fact": entry.get("value"),
            }
        )
        entry["status"] = "persisted"
        entry["fact_id"] = new_fact_id
        changed = True

    if changed:
        callback_context.state[PUBLIC_SESSION_FACTS] = session_facts
        callback_context.state[PUBLIC_FACT_HISTORY] = history


def _is_real_user_text(content) -> bool:
    """True only for genuine user text messages.

    Excludes:
      - Non-user-role contents
      - Contents without any text parts (e.g. function_response user turns)
      - ADK 'For context:' router context messages
      - Previously injected '[session facts:' messages
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
    if first == "For context:" or first.startswith("[session facts:"):
        return False
    return True


def _inject_facts_as_content(llm_request: LlmRequest, flat: dict) -> None:
    """Append a [session facts: {...}] user message at the end of contents.

    The system instruction is NOT modified, keeping it stable for prefix caching.

    Placement: always at the end of contents — after any current-turn tool-call /
    tool-response pairs — so the model sees facts as the last context item before
    it generates its next response.

    Injecting after the last user message but before a model thought+function_call
    block (the previous approach) broke Gemini's thought_signature validation when
    inject ran on the second LLM call of a multi-step tool sequence, because the
    Gemini API requires that no user message appears between a user turn and the
    model's thought+function_call that answered it.
    """
    contents = list(llm_request.contents or [])
    facts_note = types.Content(
        role="user",
        parts=[types.Part(text=f"[session facts: {json.dumps(flat)}]")],
    )
    contents.append(facts_note)
    llm_request.contents = contents


# ── Public callbacks ───────────────────────────────────────────────────────────


def inject_facts_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> LlmResponse | None:
    """Inject current session facts into the conversation as a plain text message.

    Steps:
      1. Persist any session facts flagged with persist_now=True (early persistence).
      2. Build a flat facts dict and append it as a '[session facts: {...}]' user
         message after the last real user message.  The system instruction is NOT
         modified so the LLM request prefix is stable for caching.

    No invocation guard: strip_tool_history_callback (which runs first in _direct_cb)
    already removes any prior [session facts:] injection before each LLM call, so
    inject always re-injects fresh facts without accumulation.

    Note: PUBLIC_FOLLOW_UP_AGENT is intentionally NOT cleared here.  Clearing it
    here would erase a signal_follow_up call made earlier in the same invocation
    (e.g., invoice_agent calls signal_follow_up in LLM call 1, then inject runs
    before LLM call 2 and would clear it before the router ever reads it).
    The router's get_conversation_context and follow_up_shortcut are the only
    places that consume follow_up state, both of which run at the start of the
    NEXT router invocation.

    Returns None in all cases (the LLM call always proceeds).
    """
    # 1. Early persistence for facts with persist_now=True.
    session_facts = callback_context.state.get(PUBLIC_SESSION_FACTS, {})
    if any(
        isinstance(v, dict) and v.get("persist_now") for v in session_facts.values()
    ):
        pending = dict(session_facts)
        for v in pending.values():
            if isinstance(v, dict) and v.get("persist_now"):
                v["status"] = "draft"
                del v["persist_now"]
        callback_context.state[PUBLIC_SESSION_FACTS] = pending
        _persist_drafts(callback_context)
        session_facts = callback_context.state.get(PUBLIC_SESSION_FACTS, {})

    # 2. Build flat view (with previous values) and inject as content.
    history = callback_context.state.get(PUBLIC_FACT_HISTORY, [])
    flat = _flat_facts(session_facts, history)

    # 3. If a PREVIOUS invocation registered a follow-up, consume the key and add
    #    a _context_note so the agent applies MANDATORY DISAMBIGUATION CHECK before
    #    acting on the current message.
    #    Guard: only fire when the invocation that set PRIOR_FOLLOW_UP_KEY is
    #    DIFFERENT from the current one.  signal_follow_up also writes
    #    "router:prior_follow_up_inv" so we can compare.  Without this guard,
    #    inject_facts_callback would consume the key and inject the note between
    #    LLM calls of the SAME agent invocation (e.g., LLM call 1 calls
    #    signal_follow_up → sets PRIOR_FOLLOW_UP_KEY → LLM call 2 fires inject
    #    and adds _context_note → model loops).
    prior_follow_up = callback_context.state.get(PRIOR_FOLLOW_UP_KEY)
    if prior_follow_up:
        current_inv = getattr(callback_context, "invocation_id", None)
        prior_inv = callback_context.state.get("router:prior_follow_up_inv")
        if prior_inv is None or current_inv != prior_inv:
            # Different invocation — safe to consume and inject.
            callback_context.state[PRIOR_FOLLOW_UP_KEY] = None
            flat["_context_note"] = (
                "The previous turn registered a follow-up (agent asked a clarifying question). "
                "If the current message is a generic action request without a specific ID "
                'or clear back-reference ("it", "that", "this"), apply the '
                "MANDATORY DISAMBIGUATION CHECK immediately — do NOT reuse cached data."
            )

    _inject_facts_as_content(llm_request, flat)

    return None


def router_force_context_callback(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> LlmResponse | None:
    """After-model callback that guarantees get_conversation_context is called.

    When the router LLM skips get_conversation_context and issues a direct
    transfer_to_agent, this callback intercepts and replaces the response with
    a get_conversation_context call.  ADK then executes the tool, adds the
    result to the conversation, and calls the LLM a second time — at which
    point the router has the context it needs and the tool trajectory includes
    the mandatory get_conversation_context entry.

    No-ops if:
      - get_conversation_context was already called this invocation (checked
        via _CTX_LOADED_KEY in session state), or
      - the model response is not a direct transfer_to_agent.
    """
    inv_id = getattr(callback_context, "invocation_id", None)
    ctx_loaded = callback_context.state.get(_CTX_LOADED_KEY)

    if inv_id is not None and ctx_loaded == inv_id:
        return None  # Context was already loaded this invocation.

    content = getattr(llm_response, "content", None)
    if content is None:
        return None
    has_direct_transfer = any(
        getattr(p, "function_call", None) is not None
        and getattr(p.function_call, "name", None) == "transfer_to_agent"
        for p in (getattr(content, "parts", None) or [])
    )
    if not has_direct_transfer:
        return None

    # Intercept: replace the direct transfer with a get_conversation_context call.
    return LlmResponse(
        content=types.Content(
            role="model",
            parts=[
                types.Part(
                    function_call=types.FunctionCall(
                        name="get_conversation_context",
                        args={},
                    )
                )
            ],
        )
    )


def persist_facts_callback(
    callback_context: CallbackContext,
) -> types.Content | None:
    """Move draft session facts into history after the agent turn completes.

    Called as after_agent_callback on every expert agent. Moves all facts with
    status='draft' to public:fact_history, updates their status to 'persisted',
    and stamps a new fact_id. If a fact already had a fact_id (was previously
    persisted and then updated via set_fact), the new history entry records
    supersedes_fact_id so the chain is queryable.

    Returns None to preserve the agent's original response.
    """
    _persist_drafts(callback_context)
    return None
