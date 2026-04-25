# callbacks.py
# Router-level callbacks. Provides two LLM-bypass fast paths:
#
#   follow_up_shortcut   — saves one LLM call per follow-up turn by detecting
#                          obvious answer messages (bare IDs, yes/no, short
#                          non-command fragments) and routing directly.
#
#   static_route_shortcut — saves one LLM call for high-confidence single-domain
#                           messages by keyword scoring (routing.py). Falls through
#                           to the LLM when confidence is low or multi-domain.
#                           A re-route guard (_STATIC_BYPASS_KEY) prevents a loop
#                           if an expert escape-hatches back through the router.
#
# router_before_model_callback chains both shortcuts: follow-up first, then static.
#
# receptionist_before_model_callback — intercepts out-of-scope requests (expense,
#   payroll, etc.) before the LLM runs, returning a consistent decline message.

from __future__ import annotations

import json
import os
import sys
import time

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.genai import types

from .follow_up_detection import is_follow_up_answer
from .oos_detection import apply_out_of_scope_instruction, detect_out_of_scope
from .routing import RoutingDecision, decide_route
from .tools.context_tools import (
    PUBLIC_FOLLOW_UP_AGENT,
    PUBLIC_REROUTE_KEY,
    _CTX_LOADED_KEY,
)

_DEBUG = os.getenv("SIMPLE_ROUTER_DEBUG", "0") == "1"

# Magenta — distinct from AGENT (cyan), TOOL→ (yellow), TOOL← (green), DBG (yellow).
_MAGENTA = "\033[35m"
_RESET = "\033[0m"


def _route_print(label: str, msg: str) -> None:
    """Colored stderr print for routing callback events (active when SIMPLE_ROUTER_DEBUG=1)."""
    if _DEBUG:
        print(f"{_MAGENTA}[{label}]{_RESET} {msg}", file=sys.stderr, flush=True)


def _log_bypass(event: str, **fields) -> None:
    """Emit a Cloud Logging-compatible JSON line for a routing bypass event.

    Always emitted (not gated on SIMPLE_ROUTER_DEBUG) so bypass-rate metrics
    are available in production without needing debug mode on.
    """
    print(
        json.dumps({"event": event, "ts": time.time(), **fields}, default=str),
        file=sys.stderr,
        flush=True,
    )


# Set SIMPLE_ROUTER_STATIC=0 to disable keyword-based routing and always use the LLM.
# Useful for A/B testing or debugging incorrect routing decisions.
_STATIC_ROUTING_DEFAULT = "0"
_STATIC_ROUTING_ENABLED = (
    os.getenv("SIMPLE_ROUTER_STATIC", _STATIC_ROUTING_DEFAULT) != "0"
)

# Session-state key set when the static router fires. Consumed (cleared) on the
# very next router invocation so the LLM can handle expert escape-hatch re-routes
# without retriggering the static bypass — preventing an infinite loop.
_STATIC_BYPASS_KEY = "router:static_bypass"


def _last_user_text(llm_request: LlmRequest) -> str:
    """Extract text from the most recent genuine user message in the request.

    Skips injected '[session facts:]' messages added by inject_facts_callback
    so callers always see the real user input, not the facts injection.
    """
    for content in reversed(llm_request.contents or []):
        if getattr(content, "role", None) == "user":
            for part in getattr(content, "parts", None) or []:
                text = getattr(part, "text", None)
                if text and not text.startswith("[session facts:"):
                    return text.strip()
    return ""


def _transfer(agent_name: str) -> LlmResponse:
    """Return a synthetic transfer_to_agent LlmResponse, bypassing the LLM."""
    return LlmResponse(
        content=types.Content(
            role="model",
            parts=[
                types.Part(
                    function_call=types.FunctionCall(
                        name="transfer_to_agent",
                        args={"agent_name": agent_name},
                    )
                )
            ],
        )
    )


_FOLLOW_UP_LAST_FIRED = (
    "router:follow_up_last_fired"  # agent name from previous shortcut fire
)

# ── Router circuit breaker ─────────────────────────────────────────────────────
# Counts router_before_model_callback activations per user turn.
# If more than _ROUTER_MAX_CALLS_PER_TURN fire within the same user turn, the
# router returns a synthetic apology instead of spinning forever.
#
# Reset key: number of user events in session.events, not invocation_id.
# Each agent transfer (router→expert, expert→router) creates a new invocation_id
# in ADK, so an invocation_id-based counter resets on every transfer and never
# accumulates across a transfer loop — making it useless for loop detection.
# The user-event count is stable across all agent transfers within one turn and
# increments exactly once per new user message, giving the correct turn boundary.
_ROUTER_LOOP_TURN = "router:loop_turn"  # user-event count when counter was last reset
_ROUTER_LOOP_COUNT = (
    "router:loop_count"  # how many times the router has activated this turn
)
_ROUTER_MAX_CALLS_PER_TURN = 5


def follow_up_shortcut(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> LlmResponse | None:
    """Skip the router LLM for clear follow-up turns.

    When signal_follow_up() registered a follow-up agent and the next user
    message looks like a direct answer (bare ID, "yes", "no", a short fragment
    without question/command words), this callback returns a synthetic
    transfer_to_agent response — saving one flash-lite LLM call per follow-up
    turn.

    Falls through to the LLM (returns None) for anything that looks like a
    new request: questions, action verbs, or messages longer than
    _MAX_FOLLOW_UP_WORDS words.

    Loop detection: if the shortcut fired last turn for agent X and X re-registered
    itself (couldn't handle the message), the shortcut breaks the loop by falling
    through to the LLM so it can re-route to the correct agent.
    """
    follow_up = callback_context.state.get(PUBLIC_FOLLOW_UP_AGENT)
    if not follow_up:
        callback_context.state[_FOLLOW_UP_LAST_FIRED] = None  # reset on clean turns
        return None

    msg = _last_user_text(llm_request)
    inv_id = getattr(callback_context, "invocation_id", None)

    if not is_follow_up_answer(msg):
        callback_context.state[_FOLLOW_UP_LAST_FIRED] = (
            None  # new request resets tracking
        )
        _route_print(
            "ROUTE:follow_up skip",
            f"new request detected → LLM | agent={follow_up!r} msg={msg[:60]!r}",
        )
        return None  # Let the LLM classify — could be a domain change

    # Loop detection: same agent re-registered after the shortcut already fired for it.
    # This means the agent couldn't handle the message and asked again → let LLM re-route.
    if callback_context.state.get(_FOLLOW_UP_LAST_FIRED) == follow_up:
        callback_context.state[_FOLLOW_UP_LAST_FIRED] = None
        callback_context.state[PUBLIC_FOLLOW_UP_AGENT] = None
        _route_print(
            "ROUTE:follow_up loop-break",
            f"agent {follow_up!r} re-registered → LLM re-routes",
        )
        return None

    # Consume the follow-up state exactly as get_conversation_context does,
    # since we're bypassing the router's tool call this turn.
    callback_context.state[PUBLIC_FOLLOW_UP_AGENT] = None
    callback_context.state[_FOLLOW_UP_LAST_FIRED] = follow_up

    _route_print(
        "ROUTE:follow_up ▶", f"skipping router LLM → {follow_up}  msg={msg[:60]!r}"
    )
    _log_bypass(
        "bypass_follow_up",
        invocation_id=inv_id,
        target_agent=follow_up,
        msg_preview=msg[:60],
    )

    return _transfer(follow_up)


def static_route_shortcut(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> LlmResponse | None:
    """Skip the router LLM when keyword scoring gives a high-confidence single-domain match.

    Uses decide_route() from routing.py (no LLM call) to score the message.
    Returns a synthetic transfer_to_agent response when confidence >= CONFIDENCE_THRESHOLD.

    Re-route guard: if an expert escape-hatches back through the router (e.g.
    invoice_agent transfers to support_agent), the router will be reinvoked with the
    same message. Without a guard the static router would fire again, looping forever.
    The _STATIC_BYPASS_KEY flag is set when this callback fires; on the very next
    invocation it is consumed and the LLM router handles the message normally.
    """
    if not _STATIC_ROUTING_ENABLED:
        return None

    inv_id = getattr(callback_context, "invocation_id", None)

    # Re-route guard: LLM handled a reroute last turn — let it handle this turn too.
    if callback_context.state.get(_STATIC_BYPASS_KEY):
        callback_context.state[_STATIC_BYPASS_KEY] = None
        _route_print("ROUTE:static guard", "bypass guard active → deferring to LLM")
        return None

    # Prefetch pass-2 guard: context already loaded this invocation — let LLM run.
    if inv_id is not None and callback_context.state.get(_CTX_LOADED_KEY) == inv_id:
        return None

    msg = _last_user_text(llm_request)
    if not msg:
        return None

    decision: RoutingDecision = decide_route(msg)
    if decision.mode == "no_signal":
        return None

    # High-confidence match — set the guard before returning so the next router
    # invocation (if any) falls through to the LLM.
    callback_context.state[_STATIC_BYPASS_KEY] = True

    _route_print(
        "ROUTE:static ▶",
        f"skipping router LLM → {decision.selected_agent}"
        f"  reason={decision.reason}"
        f"  conf={round(decision.confidence, 2)}"
        f"  scores={decision.scores}",
    )
    _log_bypass(
        "bypass_static",
        invocation_id=inv_id,
        target_agent=decision.selected_agent,
        confidence=round(decision.confidence, 3),
        scores=decision.scores,
        reason=decision.reason,
        msg_preview=msg[:60],
    )

    return _transfer(decision.selected_agent)


def _user_text_from_context(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> str:
    """Read the current user message.

    Tries three sources in order:
    1. llm_request.contents  — works when include_contents='default'
    2. callback_context.session.events — latest user event; works for all agents
       including those with include_contents='none' where contents is empty
    3. callback_context.user_content  — declared in ADK but never populated (future-proof)
    """
    msg = _last_user_text(llm_request)
    if msg:
        return msg

    # Fallback: walk session events backwards to find the latest user turn.
    session = getattr(callback_context, "session", None)
    events = getattr(session, "events", None) or []
    for event in reversed(events):
        if getattr(event, "author", None) == "user":
            content = getattr(event, "content", None)
            for part in getattr(content, "parts", None) or []:
                text = getattr(part, "text", None)
                if text:
                    return text.strip()
            break

    return ""


def out_of_scope_shortcut(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> LlmResponse | None:
    """Steer the router LLM toward a decline response for out-of-scope requests.

    When an out-of-scope keyword is detected, overrides the system instruction so
    the LLM generates a polite decline in the user's own language, and clears tools
    to prevent any routing or tool calls. Returns None so the (modified) LLM request
    proceeds normally.
    """
    msg = _user_text_from_context(callback_context, llm_request)
    if not msg:
        return None
    matched = detect_out_of_scope(msg)
    if matched is None:
        return None

    _route_print(
        "ROUTE:oos ▶", f"steering LLM to decline  keyword={matched!r}  msg={msg[:60]!r}"
    )

    apply_out_of_scope_instruction(matched, llm_request)
    return None


_PREFETCH_THOUGHT_SIG = b"skip_thought_signature_validator"


def _patch_prefetch_thought_signature(llm_request: LlmRequest) -> None:
    """Inject thought_signature into the synthetic get_conversation_context Part.

    Called on the second before_model_callback pass, after the tool has executed.
    At that point llm_request.contents contains the synthetic Part recorded by ADK
    — without a thought_signature, so session events stay binary-free (no [attachment]
    labels in ADK web UI). We patch it here, in the LLM request only, so the Gemini
    API accepts the Part in history.
    """
    for content in llm_request.contents or []:
        if getattr(content, "role", None) != "model":
            continue
        parts = list(getattr(content, "parts", None) or [])
        for idx, part in enumerate(parts):
            fc = getattr(part, "function_call", None)
            if fc and getattr(fc, "name", None) == "get_conversation_context":
                if not getattr(part, "thought_signature", None):
                    parts[idx] = types.Part(
                        function_call=part.function_call,
                        thought_signature=_PREFETCH_THOUGHT_SIG,
                    )
                    content.parts = parts
                return


def _emit_prefetch_label_span(inv_id: str | None, llm_request: LlmRequest) -> None:
    """Emit a trace span that prevents [attachment] labels in the ADK web Trace tab.

    The Trace tab's findUserMsgFromInvocGroup picks the FIRST span per trace that has
    gcp.vertex.agent.invocation_id + gcp.vertex.agent.llm_request, then reads the last
    role="user" content's text. Without this span, the only such span per invocation is
    the pass-2 LLM call — its contents end with function_response (no text) →
    "[attachment]". This span is emitted in pass 1 (earlier start_time), so find()
    picks it and shows the user's actual text instead.
    """
    if inv_id is None:
        return
    try:
        user_text: str | None = None
        for content in reversed(list(llm_request.contents or [])):
            if getattr(content, "role", None) != "user":
                continue
            for part in getattr(content, "parts", None) or []:
                text = getattr(part, "text", None)
                if text and not text.startswith("[session facts:"):
                    user_text = text
                    break
            if user_text:
                break
        if not user_text:
            return
        import json
        from opentelemetry import trace as _otel_trace

        tracer = _otel_trace.get_tracer(__name__)
        fake_req = json.dumps(
            {"contents": [{"role": "user", "parts": [{"text": user_text}]}]}
        )
        with tracer.start_as_current_span("context_prefetch_label") as span:
            span.set_attribute("gcp.vertex.agent.invocation_id", inv_id)
            span.set_attribute("gcp.vertex.agent.llm_request", fake_req)
    except Exception:  # never fail routing due to a tracing issue
        pass


def context_prefetch_shortcut(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> LlmResponse | None:
    """Pre-execute get_conversation_context before the router LLM call.

    Returns a synthetic LlmResponse(function_call=get_conversation_context) so ADK
    executes the real tool and records it in the trajectory. The LLM is then called
    once with context already in contents, reducing the LLM path from 2 calls to 1.

    Two-pass design:
      Pass 1: emit a label span (so Trace tab shows user text, not [attachment]),
              then return synthetic LlmResponse WITHOUT thought_signature.
      Pass 2: _patch_prefetch_thought_signature injects the bypass string into
              llm_request.contents before the real LLM call → Gemini API accepts
              the synthetic Part in history.

    Guard: no-ops (pass 2) if get_conversation_context was already called this
    invocation (_CTX_LOADED_KEY == inv_id).
    """
    inv_id = getattr(callback_context, "invocation_id", None)
    if inv_id is not None and callback_context.state.get(_CTX_LOADED_KEY) == inv_id:
        # Second pass — patch thought_signature into the request, then let LLM run.
        _patch_prefetch_thought_signature(llm_request)
        return None

    _emit_prefetch_label_span(inv_id, llm_request)
    _log_bypass("prefetch_context", invocation_id=inv_id)
    _route_print(
        "ROUTE:prefetch ▶",
        "pre-executing get_conversation_context → saving one LLM call",
    )
    return LlmResponse(
        content=types.Content(
            role="model",
            parts=[
                types.Part(
                    function_call=types.FunctionCall(
                        name="get_conversation_context",
                        args={},
                    ),
                    # thought_signature intentionally absent here — keeps session events
                    # free of binary data. Injected by _patch_prefetch_thought_signature
                    # on the second pass directly into llm_request.contents.
                )
            ],
        )
    )


def _router_circuit_breaker(
    callback_context: CallbackContext,
) -> LlmResponse | None:
    """Return a synthetic error response if the router has been called too many times this turn.

    Prevents infinite routing loops (e.g. expert→router→expert→...) from
    running until the AFC hard limit. After _ROUTER_MAX_CALLS_PER_TURN
    router callback firings within one ADK invocation the circuit opens and
    returns a polite apology so the user sees a response rather than a hang.

    Reset key: number of user events in session.events, not invocation_id.
    Each agent transfer (router→expert or expert→router) creates a new
    invocation_id in ADK, so an invocation_id-based counter resets on every
    transfer and can never accumulate across a transfer loop.  The user-event
    count stays constant for all agent transfers within one user turn and only
    increments when the user sends a new message — giving the correct boundary.

    Scope: router activations only.  Loops confined to an expert agent's own
    LLM reasoning (tool-call loops inside invoice_agent, etc.) never touch this
    counter; those must be fixed at the prompt level.
    """
    inv_id = getattr(callback_context, "invocation_id", None)  # for logging only

    # Derive the current user-turn index from the number of user events in the
    # session.  This is stable for the lifetime of one user turn and increments
    # exactly once when the next user message arrives.
    session = getattr(callback_context, "session", None)
    events = getattr(session, "events", None) or []
    turn = sum(1 for e in events if getattr(e, "author", None) == "user")

    # Reset counter when a new user turn starts.
    if callback_context.state.get(_ROUTER_LOOP_TURN) != turn:
        callback_context.state[_ROUTER_LOOP_TURN] = turn
        callback_context.state[_ROUTER_LOOP_COUNT] = 0

    count = callback_context.state.get(_ROUTER_LOOP_COUNT, 0) + 1
    callback_context.state[_ROUTER_LOOP_COUNT] = count

    if count > _ROUTER_MAX_CALLS_PER_TURN:
        _route_print(
            "ROUTE:circuit_breaker ▶",
            f"router called {count} times this turn — breaking loop",
        )
        _log_bypass("circuit_breaker_fired", invocation_id=inv_id, call_count=count)
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[
                    types.Part(
                        text=(
                            "I encountered an issue processing your request. "
                            "Please try again or rephrase your question."
                        )
                    )
                ],
            )
        )
    return None


def router_before_model_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> LlmResponse | None:
    """Chain shortcuts before each router LLM call (checked in priority order):
    0. circuit breaker            — abort if router called too many times this turn
    1. reroute guard              — expert called signal_reroute(); skip all shortcuts, let LLM classify
    2. out_of_scope_shortcut      — return decline text for out-of-scope keywords (beats follow-up state)
    3. follow_up_shortcut         — honour explicit follow-up state
    4. static_route_shortcut      — keyword scoring for high-confidence single-domain msgs
    5. context_prefetch_shortcut  — pre-execute get_conversation_context, saving one LLM call
    """
    result = _router_circuit_breaker(callback_context)
    if result is not None:
        return result

    if callback_context.state.get(PUBLIC_REROUTE_KEY):
        callback_context.state[PUBLIC_REROUTE_KEY] = None
        _route_print(
            "ROUTE:reroute ▶",
            "expert requested reroute → bypassing all shortcuts → LLM",
        )
        return context_prefetch_shortcut(callback_context, llm_request)

    result = out_of_scope_shortcut(callback_context, llm_request)
    if result is not None:
        return result
    result = follow_up_shortcut(callback_context, llm_request)
    if result is not None:
        return result
    result = static_route_shortcut(callback_context, llm_request)
    if result is not None:
        return result
    return context_prefetch_shortcut(callback_context, llm_request)


def receptionist_before_model_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> LlmResponse | None:
    """Steer the agent LLM toward a decline response for out-of-scope requests.

    When an out-of-scope keyword is detected, overrides the system instruction so
    the LLM generates a polite decline in the user's own language. Returns None so
    the (modified) LLM request proceeds normally.

    Reads the user message via _user_text_from_context because agents with
    include_contents="none" have empty llm_request.contents.
    """
    msg = _user_text_from_context(callback_context, llm_request)
    if not msg:
        return None

    matched = detect_out_of_scope(msg)
    if matched is None:
        return None

    _route_print(
        "ROUTE:oos ▶", f"steering LLM to decline  keyword={matched!r}  msg={msg[:60]!r}"
    )

    apply_out_of_scope_instruction(matched, llm_request)
    return None
