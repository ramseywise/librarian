# Langfuse Observability

This document explains how Langfuse is integrated into the Agentic RAG system and how to navigate the dashboard to inspect traces.

---

## How it works

Langfuse models every user query as a **trace** — a tree of observations that captures everything that happened to produce a response.

```
Trace: agentic-rag-query                          ← session_id, metadata={rag_path}
  └── Agent: invoke_agent agentic_rag              ← ADK auto-instrumented
        ├── Generation: call_llm                   ← ADK: model decides to call classify_query
        │     └── Generation: generate_content gemini-2.5-flash
        │           └── Tool: classify_query       ← ADK tool execution
        │                 └── Span: classify_query ← our @observe
        ├── Generation: call_llm                   ← ADK: model decides to call vector_search
        │     └── Generation: generate_content gemini-2.5-flash
        │           └── Tool: vector_search
        │                 └── Span: vector_search  ← our @observe
        │                       └── Span: embed_query
        ├── Generation: call_llm                   ← ADK: model decides to call grade_relevance
        │     └── Generation: generate_content gemini-2.5-flash
        │           └── Tool: grade_relevance
        │                 └── Span: grade_relevance ← our @observe
        │
        │   (if Corrective RAG fires — rewrite + re-retrieve + re-grade)
        │
        │
        └── Generation: call_llm                   ← ADK: final response synthesis
              └── Generation: generate_content gemini-2.5-flash
  Score: retrieval_quality                         ← overall_score from final grade_relevance
```

The tree has two layers of instrumentation:
- **ADK auto-instrumented** (via OpenTelemetry): `invoke_agent`, `call_llm`, `generate_content`, `Tool` nodes — these capture the full LLM context including system prompt, conversation history, and accurate token counts.
- **Our `@observe` decorators**: named `Span` nodes on tool functions and `embed_query` — these provide semantic grouping and custom input/output capture.

Each generation node has its own timing, input, output, token counts, and model name.

---

## Integration points in the code

### `agent.py` — root trace

```python
@observe(name="agentic-rag-query")
async def query_async(self, user_query):
    ...
    with propagate_attributes(session_id=self._session_id):
        langfuse.update_current_span(input=user_query)
        ...
        langfuse.set_current_trace_io(output=response_text)
        langfuse.update_current_span(metadata={"rag_path": rag_path})
```

The `@observe` decorator on `query_async` opens a new **trace** every time a user sends a message. The `update_current_span` call attaches the question to the root span, and `set_current_trace_io` sets the final answer on the trace, so you can see them at a glance in the traces list without opening the detail view.

Every tool call that happens inside this function automatically becomes a child of this trace — no manual linking needed. Python's `ContextVar` propagates the trace context through the async ADK runner into each tool function.

#### Session ID

The `session_id` is propagated via `propagate_attributes(session_id=...)`, which is used as a context manager wrapping the entire agentic loop. This groups all turns of a multi-turn conversation into a single session in Langfuse, so you can reconstruct conversation arcs and spot quality degradation mid-session.

#### RAG path metadata

After the agentic loop completes, the agent inspects which tools were called and records the RAG path as span metadata:

- `happy` — retrieval succeeded on the first attempt
- `corrective` — the grader rejected results and `rewrite_query` was called

```python
langfuse.update_current_span(metadata={"rag_path": rag_path})
```

#### Retrieval quality score

The `overall_score` from the final `grade_relevance` call is posted as a first-class Langfuse Score:

```python
langfuse.score_current_trace(name="retrieval_quality", value=score, data_type="NUMERIC")
```

This makes retrieval quality chartable over time and enables regression detection when the knowledge base or chunking strategy changes.

#### Error metadata

The agentic loop is wrapped in a `try/except`. If an exception occurs, the root span is marked as an error before re-raising:

```python
except Exception as e:
    langfuse.update_current_span(
        level="ERROR",
        status_message=str(e),
    )
    raise
```

Failed traces surface as error-level spans in the dashboard, showing the exception message directly.

---

### `tools.py` — child spans and generations

Each of the 6 tools is decorated independently. The `as_type` parameter tells Langfuse what kind of node to create:

#### LLM-calling tools → ADK auto-instrumented generations

The LLM-calling tools (`classify_query`, `decompose_query`, `rewrite_query`, `grade_relevance`) are each decorated with `@observe(name="...")` to create a named span for semantic grouping. They delegate the actual Gemini call to a shared `_tracked_generate` helper (a plain function with no Langfuse decorator).

LLM call details (prompt, response, model, token counts, cost) are captured automatically by ADK's OpenTelemetry instrumentation, which creates `call_llm` → `generate_content` generation nodes. These nodes see the full context including the system prompt and conversation history, so their token counts are accurate.

#### Vector search → `as_type="span"`

```python
@observe(as_type="span", name="vector_search")
def vector_search(query: str, top_k: int = 5, ...) -> str:
    ...
    langfuse_get_client().update_current_span(
        input={"query": query, "top_k": top_k, ...},
        output={"total": len(serializable), "results": serializable},
    )
```

`vector_search` does not call an LLM — it runs cosine similarity over numpy arrays — so it uses `as_type="span"` instead. The span captures the query and the retrieved documents, so you can inspect what the retriever actually returned for a given question.

#### Embedding latency → `as_type="span"` (in `vector_store.py`)

```python
@observe(as_type="span", name="embed_query")
def _embed_query(self, query):
    ...
```

The `_embed_query` method in `VectorStore` is decorated with `@observe`, making embedding latency visible as a child span of `vector_search`. This separates the Gemini embedding API call from the pgvector cosine similarity query, so you can identify where retrieval time is actually spent.

---

## Context propagation

Two instrumentation systems coexist, and both use OpenTelemetry trace context under the hood:

1. **ADK auto-instrumentation** — Google ADK v1.x emits OTEL spans for every `call_llm`, `generate_content`, tool execution, and agent invocation. Langfuse v4 registers as an OTEL exporter, so these spans appear in the Langfuse dashboard automatically.
2. **Our `@observe` decorators** — Langfuse's `@observe` also uses OTEL internally. When a decorated tool function runs inside the ADK runner, it reads the active OTEL trace context and attaches itself as a child span.

The result is a single unified trace tree containing both ADK-generated and manually-created spans. You never pass a trace ID manually anywhere.

---

## Environment variables

Langfuse reads credentials directly from the environment (loaded via `python-dotenv` in `config.py`):

```
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

---

## Viewing traces in the dashboard

### 1. Open the Traces list

Go to [cloud.langfuse.com](https://cloud.langfuse.com) → your project → **Tracing** → **Traces**.

You will see one row per user query. Each row shows:
- Trace name (`agentic-rag-query`)
- The user's question (trace input)
- Total latency
- Total cost (aggregated from all generation token counts)

![Traces list](https://langfuse.com/images/docs/tracing-overview.png)

---

### 2. Open a trace

Click any row to open the detail view. You will see the full span tree on the left and a timeline on the right.

The tree reflects the agentic loop. Look at the `Tool` nodes to identify the path taken:
- **Happy path** — `classify_query` → `vector_search` → `grade_relevance` → final `call_llm` (synthesis). Three tool calls + one synthesis LLM call.
- **Corrective path** — adds `rewrite_query` → `vector_search` → `grade_relevance` after the first grading. The grader rejected the initial results and forced a retry.

This makes it immediately obvious which queries are hard for the system. You can also check the `rag_path` metadata on the root span.

---

### 3. Inspect a generation

Click any `generate_content gemini-2.5-flash` generation node (created by ADK's auto-instrumentation) to see:
- **Input** — the exact prompt sent to Gemini, including the retrieved documents
- **Output** — the raw JSON response with individual document grades and the `overall_score`
- **Model** — `gemini-2.5-flash`
- **Token usage** — prompt tokens, completion tokens
- **Latency** — how long this specific LLM call took

---

### 4. Inspect the vector search span

Click the `vector_search` span to see:
- **Input** — the query string and `top_k`
- **Output** — the full list of retrieved chunks with their cosine similarity scores

This is useful for debugging retrieval quality: if the agent rewrote a query, you can compare what the search returned before and after the rewrite.

---

### 5. Inspect the embedding span

Expand a `vector_search` span to see the child `embed_query` span. This shows:
- **Latency** — how long the Gemini embedding API call took, separate from the pgvector query time

This is useful for diagnosing whether retrieval slowness comes from embedding generation or database search.

---

### 6. View scores

Go to **Tracing** → **Scores** to see the `retrieval_quality` score distribution over time. Each score corresponds to the `overall_score` from the final `grade_relevance` call. A declining trend signals retrieval quality regression.

You can also see the score on each individual trace in the detail view.

---

### 7. Filter and search

In the Traces list you can:
- **Filter by metadata** (`rag_path`: `happy`, `corrective`) to see which RAG path was taken
- **Filter by session** to see all turns in a multi-turn conversation
- **Filter by score** to find low-quality retrievals
- **Filter by level** to find failed traces (look for `ERROR` level spans)
- **Filter by latency** to find slow queries
- **Filter by cost** to find expensive multi-step traces
- **Search by input** to find traces for a specific question
- **Filter by date** to compare behavior before and after a code change
