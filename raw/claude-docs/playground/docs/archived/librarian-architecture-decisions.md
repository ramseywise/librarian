# Plan: Librarian Architecture — Tradeoffs and Direction

**Status:** Draft — awaiting review
**Scope:** `playground/src/` — naming, architecture, and deployment interface
**Question:** How do we structure the Librarian so it works seamlessly regardless of
             whether the Copilot goes full ADK/Bedrock, full LangGraph, or polyglot?

---

## Current State

The `playground` repo has strong retrieval and eval infrastructure but weak deployment
clarity. Two parallel orchestration approaches exist side-by-side:

| | LangGraph CRAG | ADK CustomRAGAgent |
|---|---|---|
| **Topology** | Deterministic graph (condense → analyze → retrieve → rerank → gate → generate) | LLM decides when/how to call tools |
| **Strength** | Predictable, traceable, testable | Flexible for exploratory queries |
| **Weakness** | Rigid for multi-hop reasoning | Unpredictable retry behavior |
| **Eval** | In `src/eval/` | In `src/eval/` |
| **Production** | `src/interfaces/api/` (exists but not deployed) | Not deployed |

The naming is wrong: `playground` implies throwaway experimentation. The retrieval
infrastructure (`librarian/`) is production-quality and should be treated as such.

---

## Three System Design Options

### Option A — Full ADK + Bedrock (TS-Native Stack)

**Architecture:**
```
ts_google_adk (Next.js)
  └── accountingAgent (LlmAgent)
        └── fetch_support_knowledge → AWS Bedrock KB (managed RAG)
```

No Python service. All knowledge retrieval is delegated to Bedrock Knowledge Base.
The `playground` codebase exists purely as a research artifact.

**What you give up:**
- Custom CRAG retry logic (Bedrock KB is single-shot retrieval, no confidence-gated retry)
- Caching layer (Bedrock has no retrieval cache)
- Custom reranking (Bedrock uses its own reranker, not configurable)
- Multi-query expansion (Bedrock takes one query, returns N results)
- Eval pipeline integration (Bedrock retrieval is opaque)
- Deduplication and grading (must be done in the tool function, not the pipeline)

**What you gain:**
- Zero infrastructure to operate — Bedrock is fully managed
- No Python service to deploy, monitor, or scale
- AWS-native: CloudWatch, IAM, S3 ingestion pipeline works out of the box
- Low operational burden for the Copilot team
- Simpler auth: one AWS credential, no service-to-service tokens

**Verdict:** Right for early prototyping and low-volume use. Wrong as a long-term
knowledge strategy because retrieval quality cannot be iterated on without rebuilding
the KB. The eval data you're collecting in `playground` becomes orphaned — it can't
inform Bedrock's retrieval.

**When to choose:** The Copilot team does not own knowledge quality iteration.
Domain experts feed Bedrock KB via S3. Retrieval quality is "good enough."

---

### Option B — Full LangGraph (Python-Owned Stack)

**Architecture:**
```
py_copilot (FastAPI + Google ADK)
  └── accountingAgent (LlmAgent)
        └── fetch_support_knowledge → POST /query → playground FastAPI
                                          └── build_graph() (LangGraph CRAG)
                                                └── vector store + reranker + cache
```

The Python service owns everything. The `ts_google_adk` TS prototype is retired or
becomes a UI-only thin client that calls the Python API.

**What you give up:**
- The TS ADK ecosystem (Next.js integration, `AsyncLocalStorage`, `FunctionTool` + Zod)
- Proximity to the UI (TS tools can read DOM state; Python tools cannot)
- The existing TS prototype investment (team knowledge, already-working tools)

**What you gain:**
- Single orchestration language — Python owns both knowledge retrieval and execution
- The playground eval pipeline directly measures what production uses
- LangGraph CRAG gives full control: caching, retry, grading, multi-query expansion
- Observability: OTEL traces, structlog, DuckDB trace storage all wire up naturally
- The `librarian/` agent classes (RetrieverAgent, RerankerAgent, GeneratorAgent) are
  already production-quality — they just need an HTTP interface

**The naming problem:** `playground` is the wrong name for this service. Rename:

```
playground/src/librarian/    → stays as the RAG component library
playground/src/orchestration/ → stays as the orchestration strategies
playground/src/interfaces/api/ → becomes the deployed service entry point
playground/ (root)           → rename to `librarian-service/` or keep as `cs-agent-assist/`
```

The deployed artifact is `librarian-service` (or `support-agent-service`), not `playground`.

**Verdict:** Highest retrieval quality ceiling. Best observability. Most operational
complexity. Right when the Copilot team owns knowledge quality and has Python infra capacity.

**When to choose:** Eval shows LangGraph CRAG meaningfully outperforms Bedrock KB on
the key metrics (faithfulness, answer_relevance, escalation precision).

---

### Option C — Polyglot (TS Copilot + Python Knowledge Service)

**Architecture:**
```
ts_google_adk (Next.js — remains the Copilot frontend)
  └── accountingAgent (LlmAgent)
        └── fetch_support_knowledge → HTTP → Python librarian-service (FastAPI)
                                                └── LangGraph CRAG pipeline
```

The TS service handles all execution tools (invoices, customers, etc.) and UI
embedding. The Python service handles all knowledge retrieval. Clear boundary.

**What you give up:**
- Single-service simplicity — now two services to deploy, monitor, auth
- One additional network hop on every knowledge query (~20-50ms)
- Operational parity: TS team must understand when Python service is degraded

**What you gain:**
- TS handles what it's good at: UI integration, async context, Zod schemas
- Python handles what it's good at: ML tooling, numpy/scipy, LangGraph, eval pipeline
- Bedrock KB and LangGraph CRAG can be A/B tested by changing one env var in TS
- The Python service can serve multiple clients (TS Copilot, future mobile, analytics)
- Language-appropriate tooling: ruff/pyright for Python, tsc/eslint for TS
- Teams can evolve independently — Python team iterates on retrieval without TS deploys

**The contract between services:**

```
POST /query
Authorization: Bearer <internal-service-token>
Content-Type: application/json

{
  "queries": ["string"],          // 1-3 search queries from the LLM
  "session_id": "optional",       // for future personalization
  "org_id": "optional"            // for future org-scoped knowledge
}

Response:
{
  "passages": [
    {
      "text": "...",
      "url": "https://...",
      "title": "Article title",
      "score": 0.87
    }
  ],
  "retrieval_strategy": "crag|bedrock|hybrid",
  "query_count": 3,
  "latency_ms": 142
}
```

This contract is stable regardless of what the Python service uses internally —
the TS tool doesn't know if it's talking to LangGraph CRAG, Bedrock KB, or a hybrid.
The strategy field enables debugging without coupling the systems.

**Verdict:** Best long-term architecture. Matches the Copilot doc's "Copilot team
owns orchestration, domain teams own execution" model. The Python knowledge service
is the Copilot team's owned infrastructure; TS execution tools are domain team owned.

**When to choose:** You want to iterate on retrieval quality independently of the
Copilot UI. The Python team has deployment capacity for a second service.

---

## Recommendation

**Start with Option A (Bedrock) for the TS prototype, migrate to Option C (polyglot)
once eval validates LangGraph CRAG quality.**

The migration path is:
1. Build the Python `librarian-service` POST /query endpoint (playground already has
   most of this in `src/interfaces/api/`)
2. Change `fetch_support_knowledge` in `ts_google_adk` from Bedrock SDK to HTTP call
3. Keep the Bedrock call behind an env flag for rollback

This is one function change in one file. The rest of the system does not change.

---

## Librarian Naming and Architecture Updates

Regardless of which option is chosen, these changes make the codebase clearer.

### Rename: `playground/` → `librarian-service/`

The root directory name `playground` is misleading — it signals "throw this away."
`librarian-service` signals "this is the deployed service that answers questions."

Internal package names do not change — `src/librarian/`, `src/orchestration/` etc.
remain unchanged. Only the repo/directory name changes.

### New: `src/interfaces/api/routes.py` — `/query` endpoint

Currently `src/interfaces/api/routes.py` exposes endpoints for the full RAG workflow.
Add a clean `/query` endpoint with the contract defined above:

```python
@router.post("/query", response_model=QueryResponse)
async def query_knowledge(
    body: QueryRequest,
    graph: CompiledStateGraph = Depends(get_graph),
) -> QueryResponse:
    """Multi-query knowledge retrieval with CRAG pipeline.

    Accepts 1-3 queries, runs them through the LangGraph CRAG graph,
    returns deduplicated, reranked passages.
    """
    start = time.monotonic()
    passages = []
    for q in body.queries:
        state = await graph.ainvoke({"query": q, "standalone_query": q})
        passages.extend(_state_to_passages(state))

    deduped = _dedup(passages)
    return QueryResponse(
        passages=deduped[:10],
        retrieval_strategy="crag",
        query_count=len(body.queries),
        latency_ms=int((time.monotonic() - start) * 1000),
    )
```

### Clarify: `src/orchestration/` naming

The two subdirectories are confusing to new engineers:

| Current | Proposed | Reason |
|---|---|---|
| `src/orchestration/langgraph/` | `src/orchestration/langgraph/` | Keep — clear |
| `src/orchestration/adk/` | `src/orchestration/adk/` | Keep — but add `README.md` |
| `src/orchestration/factory.py` | `src/orchestration/factory.py` | Keep — but update after Step 4 of `langgraph-adk-compatibility.md` |

Add `src/orchestration/README.md`:
```
Two orchestration strategies exist intentionally for A/B comparison:
- langgraph/: Deterministic CRAG graph. Use this for predictable, auditable retrieval.
- adk/: LLM-driven tool calling. Use this to test whether Gemini makes better decisions.
Both use the same agent objects from src/librarian/ as the shared component layer.
```

### New: `src/orchestration/service.py` — unified entry point

Today `factory.py` builds the graph for LangGraph. There is no equivalent factory
for "run a query against whichever orchestration strategy is configured." Add one:

```python
# src/orchestration/service.py
from core.config.settings import settings

async def run_query(
    query: str,
    *,
    session_id: str | None = None,
) -> list[Passage]:
    """Run a query through the configured orchestration strategy.

    The strategy is selected by `settings.orchestration_strategy`:
    - "langgraph": LangGraph CRAG graph
    - "adk": ADK CustomRAGAgent
    - "bedrock": Direct Bedrock KB (for comparison baseline)
    """
    if settings.orchestration_strategy == "langgraph":
        return await _run_langgraph(query)
    elif settings.orchestration_strategy == "adk":
        return await _run_adk(query)
    elif settings.orchestration_strategy == "bedrock":
        return await _run_bedrock(query)
    raise ValueError(f"Unknown strategy: {settings.orchestration_strategy}")
```

This is the single abstraction that makes the system "strategy-agnostic." The `/query`
FastAPI endpoint calls `run_query()`. Switching strategies is one env var change.

---

## Tradeoff Matrix

| Dimension | Full Bedrock (A) | Full LangGraph (B) | Polyglot (C) |
|---|---|---|---|
| **Retrieval quality** | Fixed (Bedrock default) | Configurable CRAG | Configurable CRAG |
| **Latency** | ~100-200ms | ~150-300ms | ~200-400ms (extra hop) |
| **Operational complexity** | Low | Medium | Medium-High |
| **Eval pipeline usability** | None | Full | Full |
| **Knowledge iteration speed** | Slow (S3 sync + KB rebuild) | Fast (vector store update) | Fast |
| **Observability** | CloudWatch only | Full OTEL | Full OTEL |
| **Infrastructure to operate** | Zero | One service | Two services |
| **Language flexibility** | TS only | Python only | Best of both |
| **Migration risk** | Low | Medium | Low (A→C is one function change) |
| **Long-term scalability** | Constrained by Bedrock | High | High |
| **Auth surface** | AWS IAM | Internal token | Both |

---

## Immediate Actions (independent of option chosen)

These should happen regardless of which direction is selected:

1. **Add `/query` endpoint to playground** — lets the Python service be callable from TS
   even if you stay on Bedrock by default. Low effort, high optionality.

2. **Add `ORCHESTRATION_STRATEGY` env var** — makes the strategy switchable without code
   changes. Implement `service.py` stub.

3. **Add `BedrockRetriever` adapter to eval** — so the eval pipeline can benchmark Bedrock
   KB against LangGraph CRAG on the same test set. This is the missing data point that
   should drive the Option A vs C decision.

4. **Write `src/orchestration/README.md`** — 10-line explanation of why two strategies
   exist. Saves the next engineer 2 hours of confusion.

5. **Update `src/librarian/ARCHITECTURE.md`** — record that agent objects are the shared
   component layer (per the `langgraph-adk-compatibility.md` plan). Remove any references
   to "playground" as the service name.
