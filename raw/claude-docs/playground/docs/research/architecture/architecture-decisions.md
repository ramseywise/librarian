# Architecture Decisions — VA Knowledge Service

Date: 2026-04-14

The central question: how do we structure the knowledge retrieval service so it works
seamlessly regardless of whether the Copilot goes full ADK/Bedrock, full LangGraph, or
polyglot?

---

## The Starting Point

Two parallel orchestration approaches existed side-by-side in the same codebase:

| | LangGraph CRAG | ADK CustomRAGAgent |
|---|---|---|
| **Topology** | Deterministic graph (condense → analyze → retrieve → rerank → gate → generate) | LLM decides when/how to call tools |
| **Strength** | Predictable, traceable, testable | Flexible for exploratory queries |
| **Weakness** | Rigid for multi-hop reasoning | Unpredictable retry behavior |
| **Eval** | Full eval harness in `src/eval/` | In `src/eval/` |
| **Production** | FastAPI interface, deployable | Not deployed |

---

## Three Design Options

### Option A — Full ADK + Bedrock (TS-Native Stack)

```
ts_google_adk (Next.js)
  └── accountingAgent (LlmAgent)
        └── fetch_support_knowledge → AWS Bedrock KB (managed RAG)
```

No Python service. All knowledge retrieval is delegated to Bedrock Knowledge Base.
The Python codebase exists purely as a research artifact.

**What you give up:**
- Custom CRAG retry logic (Bedrock KB is single-shot retrieval, no confidence-gated retry)
- Caching layer (Bedrock has no retrieval cache)
- Custom reranking (Bedrock uses its own reranker, not configurable)
- Multi-query expansion (Bedrock takes one query, returns N results)
- Eval pipeline integration (Bedrock retrieval is opaque — the eval data becomes orphaned)
- Deduplication and grading

**What you gain:**
- Zero infrastructure to operate — fully managed
- AWS-native: CloudWatch, IAM, S3 ingestion pipeline out of the box
- Low operational burden for the Copilot team
- Simpler auth: one AWS credential, no service-to-service tokens

**Verdict:** Right for early prototyping and low-volume use. Wrong as a long-term knowledge
strategy because retrieval quality cannot be iterated on without rebuilding the KB.

**When to choose:** The Copilot team does not own knowledge quality iteration. Domain experts
feed Bedrock KB via S3. Retrieval quality is "good enough."

---

### Option B — Full LangGraph (Python-Owned Stack)

```
py_copilot (FastAPI + Google ADK)
  └── accountingAgent (LlmAgent)
        └── fetch_support_knowledge → POST /query → Python FastAPI
                                          └── LangGraph CRAG graph
                                                └── vector store + reranker + cache
```

The Python service owns everything. The TS prototype is retired or becomes a UI-only thin
client.

**What you give up:**
- The TS ADK ecosystem (Next.js integration, `AsyncLocalStorage`, `FunctionTool` + Zod)
- Proximity to the UI (TS tools can read DOM state; Python tools cannot)
- The existing TS prototype investment

**What you gain:**
- Single orchestration language — Python owns both knowledge retrieval and execution
- The eval pipeline directly measures what production uses
- LangGraph CRAG: full control over caching, retry, grading, multi-query expansion
- Observability: OTEL traces, structlog, DuckDB trace storage
- The `librarian/` agent classes are production-quality — they just need an HTTP interface

**Verdict:** Highest retrieval quality ceiling. Best observability. Most operational
complexity.

**When to choose:** Eval shows LangGraph CRAG meaningfully outperforms Bedrock KB on key
metrics (faithfulness, answer_relevance, escalation precision).

---

### Option C — Polyglot (TS Copilot + Python Knowledge Service)

```
ts_google_adk (Next.js — Copilot frontend)
  └── accountingAgent (LlmAgent)
        └── fetch_support_knowledge → HTTP → Python librarian-service (FastAPI)
                                                └── LangGraph CRAG pipeline
```

TS handles all execution tools (invoices, customers, etc.) and UI embedding. Python handles
all knowledge retrieval. Clear boundary.

**What you give up:**
- Single-service simplicity — two services to deploy, monitor, and auth
- One additional network hop on every knowledge query (~20–50ms)

**What you gain:**
- TS handles what it's good at: UI integration, async context, Zod schemas
- Python handles what it's good at: ML tooling, numpy/scipy, LangGraph, eval pipeline
- Bedrock KB and LangGraph CRAG can be A/B tested by changing one env var in TS
- The Python service can serve multiple clients (TS Copilot, future mobile, analytics)
- Teams can evolve independently

**The contract between services:**

```json
POST /query
{
  "queries": ["string"],
  "session_id": "optional",
  "org_id": "optional"
}

Response:
{
  "passages": [{"text": "...", "url": "...", "title": "...", "score": 0.87}],
  "retrieval_strategy": "crag|bedrock|hybrid",
  "query_count": 3,
  "latency_ms": 142
}
```

This contract is stable regardless of what the Python service uses internally.
The strategy field enables debugging without coupling the systems.

**Verdict:** Best long-term architecture. Matches the "Copilot team owns orchestration,
domain teams own execution" model.

**When to choose:** You want to iterate on retrieval quality independently of the Copilot
UI. The Python team has deployment capacity for a second service.

---

## Recommendation

**Start with Option A (Bedrock) for the TS prototype, migrate to Option C (polyglot) once
eval validates LangGraph CRAG quality.**

The migration path is:
1. Build the Python `librarian-service` POST `/query` endpoint (the FastAPI service already
   has most of this)
2. Change `fetch_support_knowledge` in TS from Bedrock SDK to HTTP call
3. Keep the Bedrock call behind an env flag for rollback

That's one function change in one file. The rest of the system does not change.

---

## Tradeoff Matrix

| Dimension | Full Bedrock (A) | Full LangGraph (B) | Polyglot (C) |
|---|---|---|---|
| **Retrieval quality** | Fixed (Bedrock default) | Configurable CRAG | Configurable CRAG |
| **Latency** | ~100–200ms | ~150–300ms | ~200–400ms (extra hop) |
| **Operational complexity** | Low | Medium | Medium-High |
| **Eval pipeline usability** | None | Full | Full |
| **Knowledge iteration speed** | Slow (S3 sync + KB rebuild) | Fast (vector store update) | Fast |
| **Observability** | CloudWatch only | Full OTEL | Full OTEL |
| **Infrastructure to operate** | Zero | One service | Two services |
| **Language flexibility** | TS only | Python only | Best of both |
| **Migration risk** | Low | Medium | Low (A→C is one function change) |
| **Long-term scalability** | Constrained by Bedrock | High | High |

---

## Strategy-agnostic service abstraction

Regardless of option chosen, this implementation pattern makes the system future-proof:

```python
# src/orchestration/service.py
async def run_query(
    query: str,
    *,
    session_id: str | None = None,
) -> list[Passage]:
    """Run a query through the configured orchestration strategy.

    Strategy selected by settings.orchestration_strategy:
    - "langgraph": LangGraph CRAG graph
    - "adk": ADK CustomRAGAgent
    - "bedrock": Direct Bedrock KB (comparison baseline)
    """
    if settings.orchestration_strategy == "langgraph":
        return await _run_langgraph(query)
    elif settings.orchestration_strategy == "adk":
        return await _run_adk(query)
    elif settings.orchestration_strategy == "bedrock":
        return await _run_bedrock(query)
    raise ValueError(f"Unknown strategy: {settings.orchestration_strategy}")
```

Switching strategies is one env var change. The `/query` FastAPI endpoint calls
`run_query()` and is unaware of the underlying implementation.
