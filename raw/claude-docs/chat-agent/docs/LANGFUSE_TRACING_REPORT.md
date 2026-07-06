# Langfuse Tracing Report — Agentic RAG

## 1. Current Traces

### Root Trace

| Name | File | Type | Captures |
|---|---|---|---|
| `agentic-rag-query` | `src/agentic_rag/agent.py:113` | trace | Raw user input, final response text, full pipeline duration |

**Purpose:** One trace per user query. Acts as the parent container for all child spans and generations. Input/output set explicitly via `update_current_span()` at lines 127 and 167.

---

### Child Observations (automatically nested under root)

| Name | File | Type | Captures |
|---|---|---|---|
| `classify_query` | `src/agentic_rag/tools.py:44` | generation | Planning prompt, model output (complexity/intent/needs_retrieval), token counts |
| `decompose_query` | `src/agentic_rag/tools.py:101` | generation | Decomposition prompt, sub-queries list, token counts |
| `vector_search` | `src/agentic_rag/tools.py:153` | span | Query string, top_k, category_filter, all returned docs with text/metadata/similarity scores |
| `grade_relevance` | `src/agentic_rag/tools.py:281` | generation | Grading prompt, per-document relevance labels, overall_score, needs_refinement flag, token counts |
| `rewrite_query` | `src/agentic_rag/tools.py:192` | generation | Original query, grader feedback, rewritten query, token counts |

**How nesting works:** All tools are decorated with `@observe`. Langfuse automatically propagates trace context through the call stack, so every tool call appears as a child of `agentic-rag-query` with no manual context threading required.

---

### What Is Not Captured

| Gap | Location |
|---|---|
| Session grouping | `self._session_id` exists in agent but never sent to Langfuse |
| User identity | Hardcoded as `"user"` at `agent.py:77`; no user ID is passed to Langfuse |
| Embedding latency | `_embed_query()` at `vector_store.py:70` is invisible — only its results surface inside `vector_search` |
| Database query latency | PostgreSQL/pgvector cosine search has no span |
| Error visibility | Exceptions are not caught or flagged in Langfuse |
| RAG path taken | No tag indicating which branch ran (happy / corrective) |
| Retrieval quality metric | `overall_score` exists in generation metadata but not posted as a first-class Langfuse Score |
| Chunks above threshold | Not computed or recorded anywhere |

---

## 2. Possible Additions

### A. Session ID on the trace
**Where:** `agent.py:124`, after `_ensure_session()`
```python
langfuse_get_client().update_current_trace(session_id=self._session_id)
```
**Benefit:** Groups all turns of a multi-turn conversation into a single session in Langfuse. Without this, every query is an orphaned trace — you cannot reconstruct a conversation arc or see whether quality degraded mid-session.

---

### B. User ID on the trace
**Where:** Add `user_id: str = "anonymous"` to `query_async()` at `agent.py:114`; pass `req.session_id` as `user_id` from `api/main.py:119` (best available proxy until real user identities exist)
```python
langfuse_get_client().update_current_trace(user_id=user_id)
```
**Benefit:** Enables per-user analytics. You can filter traces by user to debug specific support conversations or spot users asking out-of-scope questions.

---

### C. Embedding latency span
**Where:** `src/agentic_rag/vector_store.py:70`
```python
from langfuse import observe

@observe(as_type="span", name="embed_query")
def _embed_query(self, query):
    ...
```
**Benefit:** Makes embedding latency visible as a child of each `vector_search` span. Currently the span shows total retrieval time with no breakdown. Separating the Gemini embedding call from the pgvector similarity search lets you identify where retrieval time is actually spent — critical if you're considering embedding caching or model changes.

---

### D. RAG path tag
**Where:** `agent.py:query_async` — derive from `self.trace` (which already records `TOOL_CALL` steps) before the final `set_current_trace_io` call
```python
tool_names = {s["details"].get("function") for s in self.trace if s["step"] == "TOOL_CALL"}
if "rewrite_query" in tool_names:
    rag_path = "corrective"
else:
    rag_path = "happy"
langfuse_get_client().update_current_trace(tags=[rag_path])
```
**Benefit:** The single most useful filter for operational monitoring. Answers: *How often does retrieval succeed first try?* A rising `corrective` rate signals retrieval quality issues. Without this tag, you'd need to count child spans to infer the path taken.

---

### E. Chunks above relevance threshold
**Where:** `src/agentic_rag/tools.py:335`, inside `grade_relevance`, added to `update_current_generation()`
```python
chunks_above_threshold = sum(1 for d in graded_docs if d["score"] >= 0.7)
langfuse_get_client().update_current_generation(
    metadata={"chunks_above_threshold": chunks_above_threshold}
)
```
**Benefit:** Summarises retrieval health in a single number. Consistently returning 0–1 relevant chunks suggests embedding model, chunk size, or knowledge base coverage needs attention. Consistently returning 5/5 may indicate the relevance threshold is too permissive. Visible per-trace without reading full result payloads.

---

### F. Final grader score as a Langfuse Score
**Where:** `agent.py:query_async`, after the loop — extract `overall_score` from `self.trace`
```python
for step in reversed(self.trace):
    if step["step"] == "TOOL_RESPONSE" and step["details"].get("function") == "grade_relevance":
        score = step["details"].get("content", {}).get("overall_score")
        if score is not None:
            langfuse_get_client().score_current_trace(
                name="retrieval_quality",
                value=score,
            )
        break
```
**Benefit:** Langfuse Scores are first-class objects — they can be charted as distributions, averaged over time, and filtered by range in the dashboard. Using a metadata field (current approach) does none of this. Posting `overall_score` as a Score makes retrieval quality chartable over time, enabling regression detection when the knowledge base or chunking strategy changes.

---

### G. Error metadata on failed traces
**Where:** `agent.py:132`, wrapping the `async for` loop
```python
try:
    async for event in self._runner.run_async(...):
        ...
except Exception as e:
    langfuse_get_client().update_current_trace(
        metadata={"error": str(e), "error_type": type(e).__name__}
    )
    raise
```
**Benefit:** Currently exceptions produce no Langfuse signal — the trace either doesn't flush or appears to succeed. This makes silent failures completely invisible in the dashboard. With this change, failed traces are filterable and show the exception type and message.

---

## Summary

### Current Coverage

The pipeline has solid **LLM observability**: all generation steps (classify, decompose, grade, rewrite) are traced with full prompt/response/token data, and the vector retrieval step captures query inputs and document results with similarity scores. This is enough to audit what the model did on any given query.

### Critical Gaps

What's missing is **operational and session-level observability**:

- **No conversation grouping** — session_id exists in the agent but never reaches Langfuse
- **No user identity** — all queries appear as the same `"user"`
- **No pipeline branch visibility** — cannot tell happy path from corrective without reading child spans
- **No quality metric** — `overall_score` is buried in generation metadata, not surfaced as a chartable Score
- **No error signal** — failed queries are invisible

### Recommended Priority

| Addition | Effort | Value | Decision |
|---|---|---|---|
| RAG path tag (D) | Low | Highest operational insight | Add |
| Final score as Langfuse Score (F) | Low | Unlocks quality monitoring over time | Add |
| Session ID (A) | Low | Enables conversation-level analysis | Add |
| User ID (B) | Low | Enables per-user filtering | Keep out for now |
| Chunks above threshold (E) | Low | Retrieval health signal | Keep out for now |
| Error metadata (G) | Low | Failure visibility | Add |
| Embedding span (C) | Medium | Latency breakdown | Add |
