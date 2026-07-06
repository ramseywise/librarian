---
title: Langfuse ADK Tracing Patterns
tags: [infra, eval, adk, pattern]
summary: Two-layer Langfuse instrumentation for ADK agents — OpenTelemetry auto-instrumentation plus manual @observe decorators produce a single unified trace tree; session grouping, RAG path tagging, and first-class Scores are the critical operational additions.
updated: 2026-07-06
sources:
  - raw/claude-docs/chat-agent/docs/LANGFUSE.md
  - raw/claude-docs/chat-agent/docs/LANGFUSE_TRACING_REPORT.md
---

# Langfuse ADK Tracing Patterns

When Google ADK v1.x and Langfuse v4 are used together, two instrumentation layers coexist. Understanding how they interact — and what they miss — is the key to useful observability.

---

## Two-Layer Architecture

### Layer 1 — ADK OpenTelemetry Auto-Instrumentation

ADK v1.x emits OTel spans automatically for:
- `invoke_agent` — top-level agent invocation
- `call_llm` — model decision step
- `generate_content gemini-*` — actual Gemini API call with full prompt, response, token counts, cost
- `Tool` — tool execution node

Langfuse v4 registers as an OTel exporter. These spans appear in Langfuse without any SDK calls in application code. Token counts and cost here are **accurate** because the OTel span has visibility into the full system prompt + conversation history.

### Layer 2 — Manual `@observe` Decorators

Langfuse's `@observe` decorator creates named `Span` or `Generation` nodes. When a decorated function runs inside the ADK runner, it reads the active OTel trace context and **attaches itself as a child span automatically** — no manual context threading required.

```python
from langfuse.decorators import observe

@observe(name="vector_search", as_type="span")
def vector_search(query: str, top_k: int = 5) -> str:
    ...
    langfuse_get_client().update_current_span(
        input={"query": query, "top_k": top_k},
        output={"total": len(results), "results": results},
    )
```

Use `as_type="span"` for non-LLM steps (retrieval, embedding). Use the default (`generation`) for LLM-calling tools — though in ADK the actual LLM call detail lives in the auto-instrumented `generate_content` child node.

### Resulting Trace Tree

```
Trace: agentic-rag-query                          ← @observe root
  └── Agent: invoke_agent                          ← ADK auto
        ├── Generation: call_llm                   ← ADK auto
        │     └── Generation: generate_content     ← ADK auto (full prompt + tokens)
        │           └── Tool: classify_query       ← ADK auto
        │                 └── Span: classify_query ← @observe
        ├── ...
        └── Span: vector_search                    ← @observe
              └── Span: embed_query                ← @observe (child span)
```

The two layers combine into a single tree. You never pass a trace ID manually anywhere.

---

## Root Trace Pattern

Open one trace per user query. Attach the raw input and final output directly to it so the traces list is scannable without opening each detail view:

```python
@observe(name="agentic-rag-query")
async def query_async(self, user_query: str):
    langfuse.update_current_span(input=user_query)
    with propagate_attributes(session_id=self._session_id):
        # ... agentic loop ...
        langfuse.set_current_trace_io(output=response_text)
        langfuse.update_current_span(metadata={"rag_path": rag_path})
```

---

## Session Grouping

Without session ID, every query appears as an orphaned trace — you cannot reconstruct a conversation arc or detect quality degradation mid-session.

```python
# After _ensure_session():
langfuse_get_client().update_current_trace(session_id=self._session_id)
```

`propagate_attributes(session_id=...)` as a context manager also works — passes session context through async ADK runner into tool functions.

---

## RAG Path Tagging

The single most useful filter for operational monitoring. Answers: *how often does retrieval succeed on the first attempt?*

```python
tool_names = {s["details"].get("function") for s in self.trace if s["step"] == "TOOL_CALL"}
rag_path = "corrective" if "rewrite_query" in tool_names else "happy"
langfuse_get_client().update_current_span(metadata={"rag_path": rag_path})
```

A rising `corrective` rate signals retrieval quality issues — embedding drift, knowledge base coverage gaps, or poor chunking.

---

## Retrieval Quality as a First-Class Score

Burying `overall_score` in generation metadata makes it invisible to Langfuse's scoring dashboards. Post it as a proper Score:

```python
for step in reversed(self.trace):
    if step["step"] == "TOOL_RESPONSE" and step["details"].get("function") == "grade_relevance":
        score = step["details"].get("content", {}).get("overall_score")
        if score is not None:
            langfuse_get_client().score_current_trace(
                name="retrieval_quality",
                value=score,
                data_type="NUMERIC",
            )
        break
```

First-class Scores are chartable as distributions over time — the primary mechanism for detecting retrieval regression after knowledge base or chunking changes.

---

## Error Visibility

Without explicit error marking, failed traces either don't flush or appear successful in the dashboard.

```python
try:
    async for event in self._runner.run_async(...):
        ...
except Exception as e:
    langfuse_get_client().update_current_span(
        level="ERROR",
        status_message=str(e),
    )
    raise
```

Failed traces become filterable by level `ERROR` and show the exception type and message directly.

---

## Embedding Latency Isolation

Without a dedicated span, retrieval time is reported as one lump — you cannot tell whether slowness comes from the embedding API call or the vector database query.

```python
# In vector_store.py
@observe(as_type="span", name="embed_query")
def _embed_query(self, query: str) -> list[float]:
    ...
```

This adds an `embed_query` child span under `vector_search`, separating Gemini embedding latency from pgvector cosine search time.

---

## Operational Priority Matrix

| Addition | Effort | Operational value |
|---|---|---|
| RAG path tag | Low | Highest — primary monitoring filter |
| Retrieval quality as Score | Low | Quality regression detection over time |
| Session ID | Low | Conversation-arc analysis |
| Error visibility | Low | Silent failure detection |
| Embedding latency span | Medium | Latency breakdown for optimization |
| User ID | Low | Per-user analytics (add when identity is available) |

---

## See Also
- [[Langfuse Platform]]
- [[ADK Observability]]
- [[CRAG Retry Logic]]
- [[Observability — LangFuse vs LangSmith Decision]]
- [[Input Guardrails Pipeline]]
