# Context Prefetch Optimization — Implementation Spec

## Problem

When both `follow_up_shortcut` and `static_route_shortcut` miss, the router falls through to the LLM. This currently costs **2 LLM calls** per turn:

```
Call 1: [SI] | [User: msg]
        → LLM decides: "I must call get_conversation_context"
        → real tool executes, trajectory recorded

Call 2: [SI] | [User: msg] | [Model: gc_call()] | [Tool: gc_result({...})]
        → LLM classifies and routes → transfer_to_agent(...)
```

Call 1 is deterministic — the router prompt mandates `get_conversation_context` at STEP 0
every single time. There is no reason to spend an LLM call on a decision the system already
knows it must make.

---

## Solution: `context_prefetch_shortcut`

Add a final step to `router_before_model_callback`. When no earlier shortcut has fired,
**return a synthetic `LlmResponse` containing `function_call(get_conversation_context, {})`**
from the callback instead of calling the LLM.

ADK processes this synthetic response identically to a real model output:

1. Executes the real `get_conversation_context` function → result written, `_CTX_LOADED_KEY`
   stamped, `follow_up_agent` consumed, tool trajectory entry recorded.
2. Appends `[Model: gc_call]` + `[Tool: gc_result]` to `llm_request.contents`.
3. Fires `before_model_callback` again (second pass).
4. All shortcuts no-op on the second pass:
   - `follow_up_shortcut`: `follow_up_agent` already cleared by the tool → `None`
   - `static_route_shortcut`: `_CTX_LOADED_KEY == inv_id` guard (see § Changes, item 2) → `None`
   - `context_prefetch_shortcut`: `_CTX_LOADED_KEY == inv_id` guard → `None`
5. **Single real LLM call** with context already in contents → router classifies and routes.

Resulting flow per turn (LLM path):

```
Callback:  [SI] | [User: msg]
           → context_prefetch_shortcut returns LlmResponse(gc_call) — no LLM

Tool runs: get_conversation_context() → trajectory recorded, state stamped

LLM call:  [SI] | [User: msg] | [Model: gc_call()] | [Tool: gc_result({...})]
           → routes → transfer_to_agent(...)
```

---

## Prefix Caching Impact

### Router agent (`include_contents="none"`)

The real LLM call sees a **structurally identical request** to today's call 2:

| | Today — call 2 | After — single call |
|--|--|--|
| Contents | `[SI][User][Model: gc_call][Tool: gc_result]` | `[SI][User][Model: gc_call][Tool: gc_result]` |
| SI prefix cached | ✅ | ✅ identical |

We eliminate call 1 (which cached only `[SI][User]`) and keep the more useful cache hit on
the fuller prefix. Zero caching regression.

### Expert agents

Completely unaffected. Expert agents are invoked after the router transfers and have no
dependency on anything changed here.

---

## Changes Required

### 1. `callbacks.py` — new function `context_prefetch_shortcut`

```python
def context_prefetch_shortcut(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> LlmResponse | None:
    """Pre-execute get_conversation_context before the router LLM call.

    Returns a synthetic LlmResponse(function_call=get_conversation_context) so ADK
    executes the real tool and records it in the trajectory. The LLM is then called
    once with context already in contents, reducing the LLM path from 2 calls to 1.

    Guard: no-ops if get_conversation_context was already called this invocation
    (_CTX_LOADED_KEY == inv_id), preventing double-prefetch in multi-step sequences.
    """
    inv_id = getattr(callback_context, "invocation_id", None)
    if inv_id is not None and callback_context.state.get(_CTX_LOADED_KEY) == inv_id:
        return None  # Already loaded this invocation — let LLM proceed.

    _log_bypass("prefetch_context", invocation_id=inv_id)
    _route_print("ROUTE:prefetch ▶", "pre-executing get_conversation_context → saving one LLM call")
    return LlmResponse(
        content=types.Content(
            role="model",
            parts=[types.Part(
                function_call=types.FunctionCall(
                    name="get_conversation_context",
                    args={},
                )
            )],
        )
    )
```

New imports required in `callbacks.py`:

```python
from .tools.context_tools import PUBLIC_FOLLOW_UP_AGENT, _CTX_LOADED_KEY
```

(`PUBLIC_FOLLOW_UP_AGENT` is already imported; `_CTX_LOADED_KEY` is the addition.)

`router_before_model_callback` updated chain:

```python
def router_before_model_callback(callback_context, llm_request):
    # Priority order — first non-None wins:
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
```

### 2. `callbacks.py` — guard `static_route_shortcut` against pass 2

**Bug without this fix:** When the re-route guard (`_STATIC_BYPASS_KEY`) was active in
pass 1, `static_route_shortcut` clears it and returns `None` (correctly deferring to the
LLM). But in pass 2 — after `context_prefetch_shortcut` has run the tool — the guard is
gone and the same high-confidence message causes `static_route_shortcut` to fire, silently
bypassing the LLM the guard was meant to protect.

Add one early-return to `static_route_shortcut`, immediately after the existing re-route
guard check:

```python
# After the existing _STATIC_BYPASS_KEY guard block:
inv_id = getattr(callback_context, "invocation_id", None)
if inv_id is not None and callback_context.state.get(_CTX_LOADED_KEY) == inv_id:
    return None  # Prefetch pass 2 — context already loaded, let LLM run.
```

`_CTX_LOADED_KEY` is already imported in `callbacks.py` for `context_prefetch_shortcut`
(see item 1 above), so no new import is needed.

This guard is also correct in the normal (non-re-route) case: if static returned `None`
in pass 1 due to low confidence, it will return `None` again in pass 2 for the same
reason — so the guard is a no-op there. It only matters when the re-route guard cleared
`_STATIC_BYPASS_KEY` in pass 1.

### 3. `_facts_callbacks.py` — `router_force_context_callback` becomes pure safety net

**No code change.** With `context_prefetch_shortcut` always firing when the LLM runs,
`_CTX_LOADED_KEY` is always stamped before the real LLM call → `router_force_context_callback`
always no-ops on the normal path. It remains unchanged as a safety net for edge cases
(e.g., if the prefetch is somehow disabled or bypassed).

### 3. `prompts/router_agent.txt` — no change

The LLM receives the `get_conversation_context` result already in context. STEP 0
("Call get_conversation_context() first") is now inert — the LLM sees the tool was
already called and routes immediately. If the LLM attempts a redundant call, the
idempotency guard in `get_conversation_context` returns `{"error": "already_called_this_turn"}`
and the LLM proceeds to route, which is correct.

### 4. `SPEC.md` — three targeted updates

**Performance Priorities → LLM call minimization table** — add row:

| Mechanism | Location | Savings vs baseline |
|-----------|----------|---------------------|
| `context_prefetch_shortcut` | `callbacks.py` | −1: eliminates the tool-decision LLM call on all LLM-path turns |

**Performance Model table** — update two rows:

| Path | Before | After |
|------|--------|-------|
| Single domain (normal) | 2 | **1** |
| Follow-up shortcut skips (new request) | 2 | **1** |

**Observability section** — add `prefetch_context` log event:

```json
{
  "event": "prefetch_context",
  "ts": 1234567890.123,
  "invocation_id": "..."
}
```

**Combined effect on prefix caching table** — update router row:

| Agent | Facts delivery | Cache fingerprint |
|-------|----------------|-------------------|
| `router_agent` | via `context_prefetch_shortcut` (pre-executed before LLM) + result in contents | SI always cached; real LLM call sees `[SI][User][Model: gc_call][Tool: gc_result]` — identical to today's call 2 |

### 5. `CLAUDE.md` — add note under Static routing section

```markdown
## Context prefetch

`context_prefetch_shortcut` is always active and fires as the last step in
`router_before_model_callback` when no other shortcut fires. It pre-executes
`get_conversation_context` via a synthetic LlmResponse, reducing the LLM-path
from 2 calls to 1. Disable by returning `None` early (no env var gate).
```

---

## Invariants Preserved

| Invariant | How preserved |
|-----------|---------------|
| `get_conversation_context` in tool trajectory | ADK executes the real function from the synthetic response — recorded identically to any other tool call |
| `follow_up_agent` consumed exactly once | `get_conversation_context` still runs and clears it |
| `_CTX_LOADED_KEY` idempotency | Tool still stamps it; prefetch guard reads it on the second `before_model_callback` pass |
| `router_force_context_callback` safety net | Unchanged — still guards against any path that skips context loading |
| Expert agent behavior | Zero changes — no code outside `callbacks.py` and documentation |
| Eval tool trajectory (`tool_trajectory_avg_score = 1.0`) | `get_conversation_context` still appears as a real tool execution in every non-shortcut turn |

---

## What Is NOT In Scope

- Removing or weakening `router_force_context_callback`
- Rewriting the router prompt STEP 0 (inert but harmless; changing it risks eval regression)
- Feature-flag gating (the prefetch is always correct; no A/B testing value)
- Any eval case changes (trajectory is identical to today)
- Any expert agent changes

---

## Open Questions (resolved before implementation)

| # | Question | Decision |
|---|----------|----------|
| 1 | Log event name: `prefetch_context` (descriptive) vs `bypass_prefetch` (follows existing `bypass_*` convention)? | `prefetch_context` — it is not a bypass (LLM still runs); a distinct name avoids confusion in dashboards |
| 2 | Feature flag? | No — the optimization is always correct and always beneficial; a flag adds complexity with no upside |

---

## `thought_signature` — Resolution

**Status: IMPLEMENTED (2026-03-20).**

Early attempts (2026-03-19) failed because a synthetic `LlmResponse(function_call=...)` injected via `before_model_callback` lacks the cryptographic `thought_signature` the Gemini API requires on model-role function_call blocks in conversation history. Setting `thought_signature=b""` (empty bytes) and setting `thinking_budget=0` both failed to satisfy the validator.

**Resolution.** The Gemini API accepts `thought_signature=b"skip_thought_signature_validator"` as a bypass for injecting synthetic tool calls into conversation history (intended for migration from stateless models and synthetic-context use cases). This is safe here because we inject `get_conversation_context` at the very start of the router's turn — there is no prior reasoning state to lose.

The implementation sets this value on the synthetic `Part` in `context_prefetch_shortcut` in `callbacks.py`.
