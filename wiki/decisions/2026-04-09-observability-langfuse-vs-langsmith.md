---
title: Observability — LangFuse vs LangSmith Decision
tags: [infra, eval, decision]
summary: Decision to use LangFuse first for RAG observability — native ragas/deepeval integrations, self-hostable, GDPR-friendly, swap later when annotation queues needed.
updated: 2026-04-24
sources:
  - raw/playground-docs/rag-agent-template-research.md
  - raw/playground-docs/adk-orchestration-research.md
---

# Observability — LangFuse vs LangSmith Decision

**Date:** 2026-04-09  
**Status:** Decided — LangFuse first, revisit LangSmith when annotation queues are needed

## The Decision

**LangFuse for MVP.** Revisit LangSmith when:
- A team is doing iterative prompt engineering in the UI
- The feedback loop (thumbs up/down → label → gold dataset) is operational
- GDPR is not a constraint (or enterprise plan is justified)

## Comparison

| Feature | LangFuse | LangSmith |
|---|---|---|
| RAG retrieval span tracing | ✓ `@observe()` or manual spans | ✓ first-class |
| Score API (log hit@k, MRR per trace) | ✓ `langfuse.score()` | ✓ |
| ragas native integration | ✓ `ragas.integrations.langfuse` | ✗ needs custom evaluator |
| deepeval native integration | ✓ `DeepEvalCallbackHandler` | ✗ needs custom evaluator |
| LangGraph tracing | Via callback handler | First-class (graph state transitions) |
| Annotation queues (human review) | ✗ | ✓ |
| Self-hostable | ✓ Docker Compose (~30 min) | ✗ Cloud only (enterprise for on-prem) |
| GDPR / data residency | ✓ | ✗ (no self-host without enterprise) |
| Cost | Free (self-hosted) | Per-trace pricing at scale |
| Playground replay from UI | ✗ | ✓ |
| Prompt hub / versioning | ✓ Prompt Management | ✓ Hub |

## Why Not LangSmith First

1. **ragas + deepeval** have native LangFuse integrations. Wiring LangSmith requires custom evaluator functions for both — non-trivial extra work upfront.
2. **Self-hosting LangFuse** takes ~30 minutes with Docker Compose. LangSmith cloud costs money from day one; on-prem needs enterprise contract.
3. **LangSmith advantages** (annotation queues, playground) only pay off when there's a feedback loop to operate and a team using the UI. That's Phase 2, not MVP.
4. **Switching from LangFuse → LangSmith** later is straightforward: replace `CallbackHandler` import, update env vars. The `get_langfuse_handler()` pattern isolates the dependency cleanly.

## Implementation Pattern

LangFuse must be optional — not everyone self-hosts it, and tests must pass without it:

```python
# src/utils/tracing.py
def get_tracing_handler(session_id: str) -> CallbackHandler | None:
    """Return LangFuse handler if LANGFUSE_ENABLED=true, else None."""
    if not settings.langfuse_enabled:
        return None
    return CallbackHandler(...)
```

Activated by `LANGFUSE_ENABLED=true` env var. LangGraph `config["callbacks"]` accepts `None` gracefully.

**structlog as baseline** (always on): each node logs its operation + key metrics as structured JSON. Observability without LangFuse for dev and CI.

## Observability Stack by Framework

| Framework | Stack | Notes |
|---|---|---|
| ADK agents (Agent Engine) | Cloud Trace + Cloud Logging + BigQuery | Native; zero config |
| LangGraph / LangChain | LangSmith (traces + datasets) or LangFuse | Both require explicit instrumentation |
| rag_poc + playground | LangSmith (configured, not always active) | Add `LANGSMITH_API_KEY` to `.env` |

**ADK key span names** (Cloud Trace):
- `agent_run` — full turn
- `llm_call` — model invocation with token counts
- `tool_call_{name}` — individual tool execution

## LangSmith When Ready

When annotation queues are needed:
- Replace `langfuse.CallbackHandler` import with `langsmith.LangChainTracer`
- Update `LANGCHAIN_TRACING_V2=true`, `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT` env vars
- Use `langsmith.evaluate()` for dataset-based evaluation runs

## See Also
- [[RAG Evaluation]]
- [[Librarian RAG Architecture]]
- [[ADK Context Engineering]]
