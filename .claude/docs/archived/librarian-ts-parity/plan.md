# Plan: Librarian — Production Standard Parity

**Status:** Draft
**Scope:** `cs_agent_assist_with_rag/` — librarian stays as a RAG-only help-assistant service
**Source:** `scope/librarian-ts-parity/research.md`
**Not in scope:** copilot, polyglot orchestration, ADK rewrite (separate thread)

---

## Goal

Bring librarian to the same engineering standard as ts_google_adk in the areas where it
currently lags — specifically the API surface and retrieval input layer. In most other
dimensions (CI/CD, observability, error handling, testing) librarian already exceeds
ts_google_adk and those areas are left alone.

---

## Step 1 — `queries: List[str]` API input

**Why:** The LLM calling librarian can't currently drive multi-query retrieval. It sends one
string. ts_google_adk's pattern is the LLM sends 2-3 reformulations; the service runs them
in parallel and merges. This is the highest-value gap.

**Changes:**

`src/interfaces/api/routes.py`
```python
class QueryRequest(BaseModel):
    queries: list[str] = Field(..., min_length=1, max_length=3,
        description="1-3 search queries covering different angles of the question")
    top_k: int = Field(default=5, ge=1, le=20)
    score_threshold: float = Field(default=0.3, ge=0.0, le=1.0)

@router.post("/query", response_model=QueryResponse)
async def query_knowledge(body: QueryRequest, graph=Depends(get_graph)) -> QueryResponse:
    start = time.monotonic()
    passages = await run_multi_query(
        queries=body.queries,
        graph=graph,
        top_k=body.top_k,
        score_threshold=body.score_threshold,
    )
    return QueryResponse(
        passages=passages,
        retrieval_strategy=settings.orchestration_strategy,
        query_count=len(body.queries),
        latency_ms=int((time.monotonic() - start) * 1000),
    )
```

**Parallel execution** — run all queries concurrently:

`src/orchestration/service.py`
```python
async def run_multi_query(
    queries: list[str],
    graph: CompiledStateGraph,
    *,
    top_k: int = 5,
    score_threshold: float = 0.3,
) -> list[Passage]:
    states = await asyncio.gather(*[
        graph.ainvoke({"query": q, "standalone_query": q})
        for q in queries
    ])
    passages = [p for state in states for p in _state_to_passages(state)]
    deduped = _dedup_global(passages)
    filtered = [p for p in deduped if p.score >= score_threshold]
    return filtered[:top_k * len(queries)]  # proportional top-k
```

**Acceptance criteria:**
- `POST /query` with `{"queries": ["a", "b"]}` returns merged deduplicated passages
- `POST /query` with `{"queries": ["a"]}` is identical to current single-query behavior
- Single-query latency regression < 50ms (parallelism overhead for N=1 is zero)
- Test: parallel queries retrieve different docs that both appear in the merged result

---

## Step 2 — Global fingerprint dedup

**Why:** If query 1 and query 2 both retrieve the same chunk, it currently appears twice in
merged results. ts_google_adk handles this with a fingerprint at the merge layer.

**Changes:**

`src/orchestration/service.py` (extend Step 1's `_dedup_global`):

```python
def _dedup_global(passages: list[Passage]) -> list[Passage]:
    # Sort by score descending — highest-scoring copy wins on collision
    passages.sort(key=lambda p: p.score, reverse=True)
    seen: set[str] = set()
    unique: list[Passage] = []
    for p in passages:
        # Prefer stable chunk ID; fall back to content fingerprint
        key = (
            p.chunk_id
            if p.chunk_id
            else f"{p.url or ''}|{p.text[:200].lower().split()}"
        )
        if key not in seen:
            unique.append(p)
            seen.add(key)
    return unique
```

**Acceptance criteria:**
- Two queries that retrieve the same chunk ID produce one passage in the output
- The passage kept is the one with the higher score (sort-before-dedup)
- Test: construct two result lists with overlapping chunk IDs, assert output has no duplicates

---

## Step 3 — Pydantic response schema at HTTP layer

**Why:** The `/query` response contract is currently implicit (whatever LangGraph state
contains). ts_google_adk enforces its agent output schema via Zod. The Python equivalent
is a Pydantic response model — it validates the contract and auto-generates OpenAPI docs.

**Changes:**

`src/interfaces/api/schemas.py` (new file):

```python
from pydantic import BaseModel

class Passage(BaseModel):
    text: str
    url: str | None = None
    title: str | None = None
    score: float
    chunk_id: str | None = None  # internal, for dedup — optional in response

class QueryResponse(BaseModel):
    passages: list[Passage]
    retrieval_strategy: str   # "crag" | "snippet" | "bedrock"
    query_count: int
    latency_ms: int
```

Wire `response_model=QueryResponse` on the `/query` route (shown in Step 1).

Add `_state_to_passages(state) -> list[Passage]` converter in `service.py` that maps
LangGraph state keys → `Passage` objects.

**Acceptance criteria:**
- `/docs` (FastAPI OpenAPI) shows the `QueryResponse` schema
- Malformed LangGraph state raises a Pydantic `ValidationError`, not an untyped 500
- Test: mock state with missing fields, assert validation error is caught and re-raised
  as a 422 before reaching the client

---

## Step 4 — Align config conventions with ts_google_adk

These are small quality-of-life items to make the two codebases easy to read side-by-side.

| Item | Change |
|---|---|
| `SCORE_THRESHOLD` | Move from CRAG gate hardcode to `LibrarySettings.score_threshold` (default 0.3). CRAG gate reads `settings.score_threshold`; `/query` endpoint exposes as overridable request param. |
| `ORCHESTRATION_STRATEGY` | Already in `build/librarian-architecture/plan.md` — confirm it's wired in `service.py` |
| Response `retrieval_strategy` | Return `settings.orchestration_strategy` in every `QueryResponse` |
| Response `latency_ms` | Add to every `QueryResponse` (measured in route handler, not service) |

**Acceptance criteria:**
- `SCORE_THRESHOLD` set in `.env` is reflected in default behavior without code change
- Integration test: set `SCORE_THRESHOLD=0.9`, confirm low-score results are filtered

---

## Step 5 — Update system prompt for multi-query usage

The LLM calling librarian needs to know it can send 2-3 queries. This is a system prompt
update in whatever agent is the caller (ts_google_adk's `fetchSupportKnowledge` tool or
the future py_copilot equivalent).

**For ts_google_adk** — update the `fetch_support_knowledge` tool description:

```typescript
description: `Search the support knowledge base. Send 1-3 queries covering different
  angles of the user's question (e.g. the exact term, a synonym, and a conceptual
  rephrasing). The service deduplicates and reranks results across all queries.`
```

**For py_copilot** (when built) — same pattern in the tool's `description` field.

**Acceptance criteria:**
- Tool description explicitly instructs multi-query usage
- Agent evals show average `query_count > 1.0` for complex questions

---

## Execution order

| # | Step | Effort | Value |
|---|---|---|---|
| 1 | `queries: List[str]` API input + parallel execution | Medium | High — core feature |
| 2 | Global fingerprint dedup | Small | High — correctness |
| 3 | Pydantic response schema | Small | Medium — contract clarity |
| 4 | Config alignment | Small | Low — polish |
| 5 | System prompt update | Trivial | High — enables the feature |

Steps 1 + 2 are coupled (dedup is only useful with multi-query). Do them together.
Steps 3 + 4 are independent polish — can be done in any order or batched.
Step 5 is a caller change — do last, after the service is validated.

---

## Files touched

| File | Change |
|---|---|
| `src/interfaces/api/routes.py` | Extend `QueryRequest`, wire `response_model=QueryResponse` |
| `src/interfaces/api/schemas.py` | New — `Passage`, `QueryResponse` |
| `src/orchestration/service.py` | New — `run_multi_query`, `_dedup_global`, `_state_to_passages` |
| `src/core/config/settings.py` | Add `score_threshold: float = 0.3` |
| `src/orchestration/langgraph/graph.py` | CRAG gate reads `settings.score_threshold` |
| `tests/unit/test_service.py` | New — dedup, multi-query merge tests |
| `tests/integration/test_query_endpoint.py` | Extend — multi-query happy path, dedup, threshold |

No changes to retrieval, reranker, generator, or eval — those are already production-quality.
