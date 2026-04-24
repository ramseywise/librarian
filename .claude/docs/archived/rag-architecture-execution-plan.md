# RAG architecture — execution plan

**Purpose:** Actionable sequence to implement the **naming, layering, and optional facades** discussed alongside [`rag-architecture-refactoring-plan.md`](./rag-architecture-refactoring-plan.md) (orchestration + policy hardening) and [`rag-system-development-plan.md`](./rag-system-development-plan.md) (product phases).

**Principles:** No loss of behavior (v2 graph, dual gates, hybrid flag, context builder). Prefer **small PRs** with green tests after each phase.

**Last updated:** April 16, 2026

---

## 0. Preconditions

| Check | Action |
|-------|--------|
| Baseline | `make test` or `uv run pytest` green on current `main` / working branch |
| Scope lock | Execution here does **not** remove retrieval/rerank HITL gates or change Bedrock/API contracts unless a separate ticket says so |

---

## Phase 1 — Vocabulary and docs (no code moves)

**Status:** Done (2026-04-16) — glossary in [`rag-architecture-refactoring-plan.md`](./rag-architecture-refactoring-plan.md) §4.3; aligned logs in `qa_nodes.py`, `retrieval_nodes.py`, `routing.py` docstrings, `hybrid_policy.py`.

**Goal:** One shared glossary for code reviews and logs.

1. Add a short **“Layering glossary”** subsection (below) to this file or to [`rag-architecture-refactoring-plan.md`](./rag-architecture-refactoring-plan.md) §4.3 — whichever the team uses as the canonical architecture pointer:
   - **Candidate retrieval** — ensemble / vector fetch + fusion (RRF), produces `GradedChunk`s.
   - **Reranking** — reorder/rescore candidates (`app/rag/reranker/`), produces `RankedChunk`s.
   - **Confidence routing** — threshold-based `answer` \| `gate` \| `escalate` (`app/graph/confidence_routing.py`; `policy.py` re-exports).
   - **Context assembly** — budget, dedupe, order (`context_builder`).
2. Audit **log messages** in `qa_nodes.py`, `retrieval_nodes.py`, `routing.py` for mixed terms (“retrieval score” vs “ensemble score” vs “rerank confidence”) and align **strings only** where it clarifies dashboards (no semantic change).

**Exit:** Team agrees on terms; log lines use them consistently in touched files.

**Note:** HITL interrupt payloads (`retrieval_confidence`, `rerank_confidence`) and LLM prompt placeholders (`retrieval_score` in hybrid retrieval probe) are **unchanged** so clients and prompts stay stable; only **log line** field names and routing docstrings were updated.

---

## Phase 2 — Rename `policy.py` → `confidence_routing.py` (backward compatible)

**Status:** Done (2026-04-16) — `app/graph/confidence_routing.py` + `policy.py` shim; internal imports use `confidence_routing`.

**Goal:** Make it obvious that this module is **routing from scores**, not ML “policy” in the RL sense (and distinct from `hybrid_policy.py`).

| Step | Action |
|------|--------|
| 2.1 | Create `app/graph/confidence_routing.py` with the **full current contents** of `app/graph/policy.py`. |
| 2.2 | Replace `app/graph/policy.py` with **thin re-exports** only: `from app.graph.confidence_routing import *` plus `__all__` matching today’s public API (see list below). |
| 2.3 | Update **internal** imports to prefer `confidence_routing` in: `hybrid_policy.py`, `qa_nodes.py`, `tests/test_qa_policy.py`. |
| 2.4 | Keep **external** imports `from app.graph.policy import ...` working indefinitely (or deprecate in a later major bump). |

**Public API to preserve (from `policy.py` today):**

- `REASON_*`, `decide_after_retrieval`, `decide_after_rerank`, `decide_qa_branch`, `retrieval_signal`, `RetrievalPolicyRoute`, `RerankPolicyRoute`

**Verification:**

```bash
uv run pytest tests/test_qa_policy.py tests/test_hybrid_policy.py tests/test_routing.py -q
```

**Exit:** All tests green; grep shows no duplicate logic; `import app.graph.policy` still works.

---

## Phase 3 — Optional: `RetrievalPipeline` facade (thin wrapper)

**Status:** Done (2026-04-16) — `app/rag/retrieval/pipeline.py` with `retrieve_graded_chunks` / `rerank_graded_chunks` and cached `get_*` factories; `retrieval_nodes.py` delegates to it.

**Goal:** One callable used by graph nodes that encodes **retrieve → rerank** order without merging `app/rag/retrieval/` and `app/rag/reranker/` packages.

| Step | Action |
|------|--------|
| 3.1 | Add `app/rag/retrieval/pipeline.py` (name flexible: `qa_runtime.py`) with a small function, e.g. `run_retrieval_and_rerank(...) -> structured result`, delegating to existing `get_ensemble_retriever()`, `get_reranker()`, same config keys. |
| 3.2 | Refactor `retriever_node` / `reranker_node` to call shared helpers **or** keep two nodes but move **shared async + error mapping** into the facade to reduce duplication. **Do not** collapse to a single LangGraph node unless product asks — v2 graph shape stays. |
| 3.3 | Unit-test the facade with mocks (no vector DB required) if logic moves. |

**Exit:** `retrieval_nodes.py` is shorter or clearer; behavior and state keys unchanged.

---

## Phase 4 — Offline vs online boundaries (documentation + light structure)

**Status:** Done (2026-04-16) — [`app/rag/preprocessing/README.md`](../../../app/rag/preprocessing/README.md); repository layout table in root [`README.md`](../../../README.md) updated.

**Goal:** No confusion between **index build** and **query-time retrieval**.

| Step | Action |
|------|--------|
| 4.1 | In `app/rag/preprocessing/README.md` (new, short) or the repo `README` **one paragraph**: state that `app/rag/preprocessing/` is the **offline / batch** path (ingest, chunk, index) and `app/rag/retrieval/runtime.py` + ensemble are **online** query paths. Link to Phase B in the development plan for Bedrock KB. |
| 4.2 | Optional rename later (separate PR): `preprocessing` → `ingestion` only if import churn is acceptable; use a compatibility shim `preprocessing/__init__.py` re-exporting from `ingestion` for one release. |

**Exit:** New contributors can answer “where do I run the crawl/index CLI?” without reading the whole tree.

---

## Phase 5 — Graph node naming (optional, higher churn)

**Goal:** Align **node names** in `graph.py` with the glossary (e.g. `confidence_routing_retrieval` instead of `qa_policy_retrieval`).

**Warning:** Renaming LangGraph node strings breaks **checkpoints**, **LangSmith traces**, and any stored graphs. Only do this with:

- explicit migration notes, or
- a new graph version / checkpoint namespace.

| If you proceed | Steps |
|----------------|--------|
| 5.1 | List every string: node names in `graph.py`, `routing.py`, tests, evals `QA_path.md`. |
| 5.2 | Rename in one PR; update `evals/experiment.py` and any trace dashboards. |
| 5.3 | Document breaking change in `app/changelog.md`. |

**Default recommendation:** **Skip Phase 5** for the POC until checkpoint compatibility is defined; Phases 1–4 deliver most clarity.

---

## Verification matrix (run before merge)

| Suite | Command |
|-------|---------|
| Policy + routing | `uv run pytest tests/test_qa_policy.py tests/test_hybrid_policy.py tests/test_routing.py -q` |
| Context | `uv run pytest tests/test_context_builder.py -q` |
| Full | `uv run pytest -q` |

---

## Suggested PR split

| PR | Contents |
|----|----------|
| PR-A | Phase 1 (glossary + log string alignment) |
| PR-B | Phase 2 (`confidence_routing` + `policy` shim) |
| PR-C | Phase 3 (facade) — optional |
| PR-D | Phase 4 (offline/online doc blurb) |
| PR-E | Phase 5 — only with checkpoint/trace strategy |

---

## Graph package taxonomy (target layout)

**Intent:** Keep **`app/graph/`** focused on **orchestration** (LangGraph wiring, routing, state contract). Retrieval/reranking stay **tools** under `app/rag/`; graph nodes only invoke them. Optional future moves are **incremental** — no LangGraph node renames until [Phase 5](#phase-5--graph-node-naming-optional-higher-churn) is approved.

### Orchestration (graph root)

| File / area | Role |
|-------------|------|
| `graph.py` | `StateGraph` — `add_node` / edges / compile / checkpointer |
| `routing.py` | Conditional edges + HITL resume parsers |
| `runner.py` | CLI entry: build `GraphState`, `invoke`, interrupt handling |

### Schemas, state, assembly (contracts — not “wiring”)

| File / area | Role |
|-------------|------|
| `state.py` | Pydantic `GraphState` |
| `schemas.py` | Citations, locale, `format_graded_context`, etc. |
| `context_builder.py` | Token budget, dedupe, citation order for the answer path |

*Optional later:* subpackage `app/graph/schemas/` (or `state/`) if these files grow.

### Policies

| File / area | Role |
|-------------|------|
| `policies/confidence_routing.py` | Threshold routes after ensemble / rerank |
| `policies/hybrid_policy.py` | Optional LLM probes on borderline bands |
| `policy.py`, `confidence_routing.py`, `hybrid_policy.py` (root) | Back-compat shims |

### Chains (prompts + Runnable factories)

| File / area | Role |
|-------------|------|
| `prompts.py` | Chat prompt templates for graph-facing chains |
| `app/rag/generator/llm.py` | Chain factories (`get_answer_chain`, planner, hybrid probes, query transform) |

*Optional later:* `app/graph/chains/` as thin re-exports or co-location with prompts — **not** required if `llm.py` remains the single factory module.

### Nodes (`app/graph/nodes/`)

One LangGraph step per module; **retriever** / **reranker** nodes call `app/rag/retrieval/` and `app/rag/reranker/` as **tools**, not as graph-owned logic.

### Utilities

| File | Role |
|------|------|
| `utils.py` | `run_coro`, latency aggregation — runtime helpers for nodes |

### Memory (clarification)

| What exists | Where |
|-------------|--------|
| **Thread / checkpoint state** | `MemorySaver` + `thread_id` in `runner.py` — resume interrupts, graph state |

| Often still “missing” for product | Notes |
|----------------------------------|--------|
| **Session / long-term memory** (summaries, prefs) | Not first-class on `GraphState` beyond `messages` / current fields; add fields + optional summarization chain when product + privacy sign off (see refactoring plan Phase C). |

### Checklist (optional refactors — no node ID changes)

- [x] Move `schemas.py` / `state.py` / `context_builder.py` under `app/graph/schemas/` — **done** (April 2026); root `state.py` / `context_builder.py` are shims; import `app.graph.schemas` for new code.
- [x] Document or thin-wrap **chains** (`prompts.py` ↔ `llm.py`) — **`app/graph/chains/`** re-exports `get_answer_chain`, `get_planner_agent` from `llm.py`.
- [ ] Relocate `runner.py` to `app/cli/` if HTTP API becomes primary entrypoint.
- [x] **Session memory** — `session_memory: Dict[str, Any]` on `GraphState` (`schemas/state.py`) with a short description; product can populate when scope is clear.

---

## Layering glossary (canonical)

| Layer | Responsibility | Primary locations |
|-------|------------------|---------------------|
| **Orchestration** | LangGraph, planner, gates, escalation | `app/graph/graph.py`, `routing.py`, `nodes/` |
| **Candidate retrieval** | Fetch + fuse (RRF), graded scores | `app/rag/retrieval/ensemble.py`, `rrf.py` |
| **Reranking** | Rescore/reorder candidates | `app/rag/reranker/` |
| **Confidence routing** | Threshold-based routes after retrieval / rerank | `app/graph/confidence_routing.py` (`policy.py` shim), `hybrid_policy.py` for borderline probes |
| **Context assembly** | Budget, dedupe, citations alignment | `app/graph/context_builder.py` |
| **Offline index pipeline** | Ingest, chunk, index build | `app/rag/preprocessing/` |

**Ranking vs retrieval:** Treat **reranking as stage 2 of the retrieval stack** in docs; keep **separate Python packages** unless a facade proves enough for your team.

---

## Traceability

| Execution phase | Ties to |
|-----------------|---------|
| 1–2 | Refactoring plan §3 Phase A–B (observability, policy clarity) |
| 3 | Refactoring plan §3 “context explicit” + slimmer nodes |
| 4 | Development plan Phase B (ingestion/index) |
| 5 | Product/checkpoint policy — not in core hardening scope |
