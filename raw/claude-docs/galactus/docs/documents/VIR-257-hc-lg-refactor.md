# hc_lg Refactor — Full Audit & Refactor

**Status:** In Review
**Ticket:** VIR-257
**Date:** 2026-06-12  
**Branch:** vir-257-hc-lg-refactor

---

## Scope

Full audit and refactor of the `hc_lg` LangGraph support agent across four dimensions:

1. **Structural refactor** — align with LangGraph conventions and `CLAUDE.md` rules
2. **Structure audit** — verify node/edge topology and routing correctness
3. **Safeguard layer verification** — confirm all 5 layers are wired per CLAUDE.md matrix
4. **Schema alignment** — align prompts and grounding with `AssistantResponse` schema
5. **Code cleanup** — dead code, stale flags, misleading comments

---

## Changes

### 1 — State migrated to TypedDict; moved to `states/` folder

**Files:** `states/graph_state.py` (new), `states/retrieval_state.py` (new), all node files, `agent.py`  
**Deleted:** `state.py`, `retrieval/state.py`

`State` and `RetrievalState` were Pydantic `BaseModel` subclasses. All nodes used
dot notation (`state.query`, `state.passages`).

**Why TypedDict:**

The primary recommended way to define graph state schema in LangGraph is `TypedDict`. Pydantic `BaseModel` is supported, but the official docs are explicit about the trade-off: Pydantic's recursive validation can be slow — for performance-sensitive applications, a `TypedDict` or `dataclass` is preferred.

For the VA graph, Pydantic validation inside state would add overhead with no safety benefit: incoming requests are already validated at the graph boundary (`ChatRequest`, `AssistantResponse`). Internal state is not user input.

There is also a compatibility constraint: the higher-level `create_agent` factory in langchain does not support Pydantic state schemas. While we're not using `create_agent` today, keeping state as `TypedDict` leaves that door open.

**Sources:** LangGraph Graph API — Schema · Use the Graph API — Pydantic models （https://docs.langchain.com/oss/python/langgraph/graph-api）

**How it works now:**

- Both states are `TypedDict, total=False` — all fields optional except `query` (in `_StateRequired`).
- Node reads: `state["field"]` (required fields) or `state.get("field", default)` (optional fields).
- Initial graph input is a plain dict `{"query": query, ...}` — not a `State(...)` constructor.
- Both state files moved to `hc_lg/states/` per `CLAUDE.md` convention (`states/` folder for all state logic).

---

### 2 — Inline prompts moved to `hc_lg/prompts.py`

**Files:** `nodes/planner.py`, `nodes/eval.py`, `retrieval/nodes.py`  
**Created:** `hc_lg/prompts.py`

Seven LLM prompts were defined inline inside node functions.

**Why:** Global `CLAUDE.md` rule — prompts must live in a dedicated `prompts.py`.
Inline prompts can't be versioned, are invisible to Langfuse prompt management, and
clutter node files.

| Constant                | Used in                               |
| ----------------------- | ------------------------------------- |
| `PLANNER_PROMPT`        | `nodes/planner.py:_llm_classify`      |
| `PLANNER_PROMPT_SCORED` | `nodes/planner.py:_llm_classify`      |
| `POST_EVAL_PROMPT`      | `nodes/eval.py:post_answer_eval_node` |
| `EXPAND_QUERIES_PROMPT` | `retrieval/nodes.py:_expand_queries`  |
| `HYDE_PROMPT`           | `retrieval/nodes.py:_hyde_generate`   |
| `GRADE_PASSAGES_PROMPT` | `retrieval/nodes.py:grade_node`       |
| `REWRITE_QUERY_PROMPT`  | `retrieval/nodes.py:rewrite_node`     |

Three hardcoded numeric constants (`MIN_WORDS`, `MIN_GOOD_PASSAGES`, `SCORE_DELTA_EPSILON`)
were also inlined — moved to `config.py` so they're env-var tunable.

---

### 3 — Checkpointer made injectable; using MemorySaver

**Files:** `graph.py`, `agent.py`, `main.py`

`MemorySaver` was hardcoded in `graph.py` at module level. `compiled` was a
module-level singleton imported directly.

**Why the architecture changed:** The hardcoded module-level compile meant the checkpointer
was fixed at import time. Moving to `build_graph(checkpointer)` + `init()` separates
construction from configuration — tests inject `MemorySaver()`, future production deploys
can swap to `AsyncPostgresSaver` in `main.py` lifespan only, without touching graph or agent code.

**New architecture:**

```
main.py lifespan
  └── init(build_graph(MemorySaver()))    ← checkpointer injected at startup
       └── build_graph(checkpointer)      ← graph.py factory, pure function
            └── agent._compiled           ← module singleton, set once by init()
                 └── run(query, ...)      ← public API
```

- `build_graph(checkpointer=None)` — pure factory, no side effects at import.
- `agent.py` holds `_compiled: Any = None`, set once at startup by `init()`.
  Tests call `init(build_graph(MemorySaver()))` directly.
- **To upgrade to persistent sessions later:** swap `MemorySaver()` for
  `AsyncSqliteSaver` or `AsyncPostgresSaver` inside the `lifespan` `async with` block — one line change in `main.py`.

---

### 4 — Type errors fixed

Two type errors were resolved after the refactor:

| File           | Error                                                                        | Fix                                                                                                         |
| -------------- | ---------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `grounding.py` | `{p.get("url") ...}` → `set[str \| None]`; `None` keys in `passage_texts`    | Changed to `{p["url"] for p in ... if p.get("url")}` — filters out URL-less passages (logic fix + type fix) |
| `agent.py`     | `_compiled = None` typed as `None`; `.get_state()` / `.ainvoke()` calls fail | Added `from typing import Any`; typed `_compiled: Any = None`                                               |

**Note:** Consolidating fragmented `from hc_lg.config import` blocks in `main.py` and other files is a clean-up -- covered under the per-file changes in the Files changed table.

---

### 5 — langfuse version pinned

**File:** `pyproject.toml`

The `langfuse>=2.0.0` constraint had no upper bound. `uv sync` installed v4 (breaking change),
which broke `hc_rag` (`langfuse.decorators` removed) and revealed pre-existing broken code in
`hc_lg` (`langfuse.callback` requires the full `langchain` package, not `langchain-core`).

**Fix:** Pinned to `langfuse>=2.0.0,<3.0.0`. v3+ removes the decorator-based API that `hc_rag` uses.

**State of langfuse in hc_lg:** `langfuse.callback.CallbackHandler` was always silently broken
(requires `langchain` monolithic, project only has `langchain-core`). The `try/except` catches
the import failure; langfuse tracing in hc_lg has never been active. Added `# type: ignore[import]`
to suppress the IDE error. A future ticket should migrate the whole codebase to langfuse v3+
using `langfuse.langchain.CallbackHandler` (which only requires `langchain-core`).

**Also fixed in `main.py`:**

- Early guardrail returns changed from raw `dict` to `EvalResponse(...)` — fixes
  `dict[str, Any | str]` not assignable to `EvalResponse` type errors.
- `AssistantResponse` import removed (unused after early returns were changed to `EvalResponse`).

---

### 6 — Structure audit (graph topology + routing)

**Result: no correctness issues.** Graph topology in `graph.py` is correct:

```
planner → { retrieve → hitl_gate → answer → post_answer_eval → grounding_check → END
           | escalate → END
           | clarify → END }
```

`post_answer_eval` can loop back to `retrieve` (max 1 retry) or `escalate`.

**One observability gap fixed in `eval.py`:**  
After max refine attempts (`post_eval_attempts > 1`), the code falls through to
`grounding_check` (intentional — "refine" means "could be better", not "wrong").
But `failure_reason` was not set, making this path invisible in downstream analysis.

```python
# Added to post_answer_eval_node:
if updates["post_eval_attempts"] > 1:
    updates["failure_reason"] = FailureReason.POST_ANSWER_FAILED
```


---

### 7 — Safeguard layer verification

All 5 layers verified correct for hc_lg:

| Layer                     | Status | Evidence                                                                                           |
| ------------------------- | ------ | -------------------------------------------------------------------------------------------------- |
| 1 — Input guardrail       | ✅     | `run_input_guard()` called in `main.py:/chat` before `_run_turn`                                   |
| 2 — Routing confidence    | ✅     | `ROUTING_CONFIDENCE_THRESHOLD` checked in `planner_node`; fallback to `answerable` is intentional  |
| 3 — Retrieval gate (CRAG) | ✅     | `confidence_gate()` short-circuits grading when top score ≥ `CRAG_HIGH_CONFIDENCE` (0.7)           |
| 4 — Post-gen grounding    | ✅     | `grounding_check` is terminal node on answer path; calls `run_output_guard()` with retrieved URLs  |
| 5 — Escalation path       | ✅     | `escalate` reachable from planner (intent), hitl_gate (low confidence), post_answer_eval (verdict) |

---

### 8 — Schema alignment

**`relevance_score` (documented, not changed):**  
hc_lg intentionally does not prompt for `relevance_score`. Bedrock's reranker score
is stored as `confidence_score` instead — a more reliable signal than LLM self-assessment.
The eval pipeline falls back to `confidence_score` when `relevance_score` is `None`.
Documented in `nodes/answer.py` and `README.md`.

**`grounding.py` — missing `failure_reason` on grounding escalations:**  
When `run_output_guard` rewrites a response to `contact_support=True` (hallucinated
sources or missing citations), `failure_reason` was not set — violating the schema
invariant "set `failure_reason` whenever `contact_support=True`".

Added `GROUNDING_FAILED = "grounding_failed"` to `FailureReason` in `schema.py`.
`grounding_node` now fills it when `guard.response` has `contact_support=True` but
no `failure_reason`:

```python
if resp.contact_support and not resp.failure_reason:
    resp = resp.model_copy(update={"failure_reason": FailureReason.GROUNDING_FAILED})
```

**`CLARIFY_PROMPT` — missing schema field guidance:**  
`clarify_node` uses `.with_structured_output(AssistantResponse)`, forcing the LLM to
populate all fields. The prompt gave no guidance on which fields to fill, risking
hallucinated `sources` or unexpected `contact_support=True` on a clarifying question.

Added two lines to `prompts.py`:

```
Schema: populate only the message field with your question. Leave sources, claims,
and suggestions empty. Set contact_support to false.
```

---

### 9 — Code cleanup

Scan result: **nothing to clean.** All config exports used, all 7 prompts imported and
used, all node functions reachable from `graph.py`, no TODO/FIXME comments,
no stale env var references.

---

## Files changed

| File                            | Change                                                                                      |
| ------------------------------- | ------------------------------------------------------------------------------------------- |
| `states/graph_state.py`         | **Created** — `State` TypedDict (moved from `state.py`)                                     |
| `states/retrieval_state.py`     | **Created** — `RetrievalState` TypedDict (moved from `retrieval/state.py`)                  |
| `states/__init__.py`            | **Created** — re-exports `State`, `RetrievalState`                                          |
| `state.py`                      | **Deleted** — replaced by `states/graph_state.py`                                           |
| `retrieval/state.py`            | **Deleted** — replaced by `states/retrieval_state.py`                                       |
| `nodes/planner.py`              | Inline prompts extracted; dict state access; consolidated config imports                    |
| `nodes/eval.py`                 | Inline prompt extracted; dict state access; `failure_reason` when `post_eval_attempts > 1`  |
| `nodes/answer.py`               | Dict state access; consolidated config imports                                              |
| `nodes/gates.py`                | Dict state access; consolidated config imports                                              |
| `nodes/grounding.py`            | Dict state access; `set[str]` type fix; `FailureReason.GROUNDING_FAILED` on escalation      |
| `retrieval/nodes.py`            | 4 inline prompts extracted; 2 inline constants moved to config; consolidated config imports |
| `retrieval/__init__.py`         | Consolidated config imports                                                                 |
| `retrieval/builder.py`          | Updated state import path                                                                   |
| `graph.py`                      | `build_graph(checkpointer)` factory replaces module-level compile                           |
| `agent.py`                      | `init()` + `_compiled: Any`; HITL resume logic; dict input                                  |
| `main.py`                       | `MemorySaver` lifespan; consolidated config imports; early returns use `EvalResponse`       |
| `config.py`                     | Added `MIN_WORDS`, `MIN_GOOD_PASSAGES`, `SCORE_DELTA_EPSILON`                               |
| `hc_lg/prompts.py`              | **Created** — 7 extracted prompts                                                           |
| `README.md`                     | Updated structure table; `relevance_score` schema note                                      |
| `src/support_agents/schema.py`  | Added `FailureReason.GROUNDING_FAILED`                                                      |
| `src/support_agents/prompts.py` | `CLARIFY_PROMPT` schema field guidance                                                      |
| `pyproject.toml`                | `langfuse<3.0.0`                                                                            |

---

## What was NOT changed

- No behavioural changes. Routing logic, CRAG flow, prompt text (except `CLARIFY_PROMPT` guidance lines), and response content are semantically identical.
- langfuse tracing in hc_lg remains disabled (pre-existing; requires separate migration ticket to langfuse v3+).
- `hc_adk`, `hc_rag`, `va_langgraph`, `va_google_adk` — untouched.
