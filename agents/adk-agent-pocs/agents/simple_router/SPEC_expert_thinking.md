# Expert Agent Thinking — Implementation Spec

## Problem

All expert agents (direct, helper, and orchestrator) are forced to `thinking_budget=0`
via `_NO_THINKING` in `expert_registry.py` and `orchestrator_agent.py`. The blocking
issue is not the facts injection itself — `inject_facts_callback` only appends a plain
user text message, which thinking models handle fine. The real blocker is in
`strip_tool_history_callback`.

### Why `strip_tool_history_callback` breaks thinking models

When a thinking model generates a response containing tool calls, its model turn contains
two kinds of parts:

1. A `thought` part — the model's internal reasoning (`Part.thought = True`, full text)
2. A `function_call` part — the actual tool invocation

**Pass 2** of `strip_tool_history_callback` ([`_history.py:116`](_history.py#L116-L120))
strips `function_call` and `function_response` parts from prior turns but leaves `thought`
parts intact. In subsequent turns that history is replayed to the API. The Gemini API
validates thought integrity: a `thought` part in history must carry a `thought_signature`
(a compact opaque bytes field that the API uses to verify the thought was unmodified). Our
re-serialization of stripped `types.Content` objects does not preserve `thought_signature`,
so the API rejects the request.

### Why not just inject facts into the system instruction instead?

The current design explicitly keeps the system instruction stable across turns so that
the prefix cache hits on the full `[SI + prior conversation]` prefix. Injecting facts into
the SI would invalidate that cache every turn. This trade-off was made intentionally.

---

## Solution: strip thought parts in Pass 2

Extend **Pass 2** of `strip_tool_history_callback` to also remove `thought` parts from
prior turns. A `thought` part is identified by either:

- `Part.thought is True` — the original thinking content
- `Part.thought_signature` being non-empty — the compact form the API may use in history

Since the function calls those thoughts accompanied are already being stripped, the thought
parts have no value to the model in subsequent turns. Removing them resolves the signature
validation error and allows thinking to be enabled without any API contract change.

With thought parts stripped from history, the `_NO_THINKING` constraint can be removed
from all expert agents and the orchestrator. Each agent gets a configurable
`thinking_budget` instead.

---

## Changes Required

### 1. `_history.py` — extend Pass 2 filter

Current filter (line 116–120):

```python
filtered = [
    p for p in (getattr(content, "parts", None) or [])
    if not getattr(p, "function_call", None)
    and not getattr(p, "function_response", None)
]
```

New filter:

```python
filtered = [
    p for p in (getattr(content, "parts", None) or [])
    if not getattr(p, "function_call", None)
    and not getattr(p, "function_response", None)
    and not getattr(p, "thought", None)
    and not getattr(p, "thought_signature", None)
]
```

Both `thought` and `thought_signature` must be checked: `thought=True` is present on the
original reasoning part; `thought_signature` (bytes) may appear on a compacted form of the
same part when replayed. Stripping either form prevents the validation error.

**Caveat (2026-03-22):** In Gemini thinking mode (`thinking_level="low"`), the model's final
text response after a tool call can carry `thought_signature` on the same Part as the text.
These are real model responses, not orphan thought blobs. The filter must therefore preserve
Parts that have `text` content even when `thought_signature` is also set. The corrected
filter is:

```python
filtered = [
    p for p in (getattr(content, "parts", None) or [])
    if not getattr(p, "function_call", None)
    and not getattr(p, "function_response", None)
    and not getattr(p, "thought", None)
    and (getattr(p, "text", None) or not getattr(p, "thought_signature", None))
]
```

This retains any part that has text (even if also tagged with `thought_signature`) and only
strips orphan thought_signature-only parts (compact thought form, no text).

No new imports required. No other logic in this file changes.

### 2. `expert_registry.py` — replace `_NO_THINKING` with `_THINKING_CONFIG`

Remove:

```python
_NO_THINKING = _genai_types.GenerateContentConfig(
    thinking_config=_genai_types.ThinkingConfig(thinking_budget=0)
)
```

Add:

```python
# Expert thinking budget. Thinking improves reasoning quality on complex queries.
# Prior-turn thought parts are stripped by strip_tool_history_callback so the API
# never sees orphaned thought_signature values from manipulated history.
_EXPERT_THINKING_BUDGET = 2048

_THINKING_CONFIG = _genai_types.GenerateContentConfig(
    thinking_config=_genai_types.ThinkingConfig(thinking_budget=_EXPERT_THINKING_BUDGET)
)
```

Replace both occurrences of `generate_content_config=_NO_THINKING` with
`generate_content_config=_THINKING_CONFIG` — one in `direct_agent`, one in `helper_agent`.

### 3. `orchestrator_agent.py` — same replacement

Remove the local `_NO_THINKING` definition (lines 12–14) and its import of
`_genai_types`. Replace `generate_content_config=_NO_THINKING` with an inline config
or import `_THINKING_CONFIG` from `expert_registry`.

Preferred approach — import from `expert_registry` to keep the budget in one place:

```python
from ..expert_registry import _THINKING_CONFIG
```

Then in `build_orchestrator_agent()`:

```python
generate_content_config=_THINKING_CONFIG,
```

### 4. No changes to `_facts_callbacks.py`

`inject_facts_callback` injects a plain `role="user"` text message. This is not a thought
or function part and requires no thought signature. It is unaffected by this change.

### 5. `SPEC.md` — update prefix cache design section

Two targeted edits to remove the now-superseded "thinking disabled" constraint:

**Prefix cache design table** — replace the "Thinking disabled" row with:

| Decision                     | Mechanism                                                                                                                                     | Why it preserves the cache prefix                                                       |
|------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| Prior thought parts stripped | `strip_tool_history_callback` removes `thought`/`thought_signature` parts from all prior turns alongside `function_call`/`function_response` | Prior-turn thought parts never appear in subsequent requests → stable prefix maintained |

**Rules for any new expert agent** — replace the last bullet:

Before:

```text
- **DO** keep `generate_content_config` with `thinking_budget=0` — do not enable thinking on expert agents
```

After:

```text
- **DO** set `generate_content_config` via `_THINKING_CONFIG` from `expert_registry.py` — this sets a
  thinking_budget and ensures prior-turn thought parts are stripped before any LLM call.
  Do not set thinking_budget=0 unless reverting to non-thinking mode intentionally.
```

### 6. No changes to prompts

Thinking happens silently inside the model. Agent prompts do not need to acknowledge or
instruct around thinking.

---

## Invariants Preserved

| Invariant | How preserved |
|-----------|---------------|
| Fact injection correctness | `inject_facts_callback` logic unchanged; injects plain user text |
| Prior-turn tool stripping | Pass 2 still strips `function_call` and `function_response`; thought strip is additive |
| Prefix caching on SI | System instruction still not modified by `inject_facts_callback` |
| Current-turn tool calls | Pass 2 only touches turns before `last_real_idx`; current-turn thoughts are untouched |
| Eval tool trajectory | No tool call behavior changes; trajectories are identical |
| Orchestrator helper isolation | `_HELPER_MODE_SUFFIX` and `disallow_transfer_to_peers` unchanged |

---

## Trade-offs

| Aspect | Before | After |
|--------|--------|-------|
| Reasoning quality | None (budget=0) | `thinking_budget=2048` per expert turn |
| Latency | Faster (no thinking) | Slightly higher on complex turns |
| History replay | Prior thoughts present but invalid | Prior thoughts stripped; no API error |
| Token cost | Lower | Higher (thinking tokens billed at output rate) |

The `_EXPERT_THINKING_BUDGET` constant is the single knob to tune latency vs. quality.
Set to `0` to revert to non-thinking behaviour without structural changes.

---

## What Is NOT In Scope

- Changing the thinking budget for the router agent (it uses `include_contents="none"`
  and does not accumulate tool history across turns — the original constraint does not
  apply to it)
- Storing or forwarding thought content across agent boundaries
- Enabling thinking on a per-expert basis (all experts share `_THINKING_CONFIG`;
  differentiated budgets can be added later by parameterising `Expert.__init__`)
- Removing `strip_tool_history_callback` (it strips tool noise from prior turns for
  reasons beyond just thinking; this spec only extends it)

---

## Tests Required

`strip_tool_history_callback` has no test file today. Create
`tests/test_history.py` with the following cases:

| Test | What it asserts |
|------|-----------------|
| `test_strips_thought_parts_from_prior_turns` | A prior-turn model content with `thought=True` part is removed from `llm_request.contents` after the callback runs |
| `test_strips_thought_signature_parts_from_prior_turns` | A prior-turn model content with `thought_signature=b"sig"` part is removed |
| `test_preserves_current_turn_thought_parts` | A thought part in the current turn (at or after `last_real_idx`) is NOT stripped |
| `test_strips_function_call_and_thought_together` | A prior-turn model content with both a `function_call` part and a `thought` part is fully removed (neither part survives) |
| `test_no_change_when_no_thought_parts` | Existing behaviour: a model content with only text parts in prior turns is preserved unchanged |

These tests follow the same pattern as existing tests in `tests/test_facts_callbacks.py`
(build minimal `LlmRequest` with `contents`, call the callback directly, assert on
`llm_request.contents`).

---

## Open Questions (resolved)

| # | Question | Resolution |
|---|----------|------------|
| 1 | What `thinking_budget` is right for experts? | Start at `2048`; tune via response eval quality metrics |
| 2 | Should orchestrator use the same budget as experts? | Yes — same `_THINKING_CONFIG` import; change independently later if needed |
| 3 | Does the Gemini SDK expose `Part.thought_signature` as a regular attribute? | **Confirmed** — `python -c "from google.genai import types; p = types.Part(text='x'); print([a for a in dir(p) if 'thought' in a.lower()])"` returns `['thought', 'thought_signature']`. Both `getattr` calls are safe. |
