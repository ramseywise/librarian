---
title: RAG API Design Patterns
tags: [rag, concept, pattern]
summary: Three design patterns for exposing a RAG service cleanly — multi-query surface (LLM sends 2-3 query variants), fingerprint-based global deduplication, and typed Pydantic response contract at the HTTP boundary.
updated: 2026-04-26
sources:
  - raw/claude-docs/playground/docs/research/rag/rag-api-design.md
---

# RAG API Design Patterns

## 1. Multi-Query API Surface

Don't make the retrieval service accept a single query. Let the calling LLM send 2–3 reformulations — it knows better than the service what angles are worth searching.

```python
class QueryRequest(BaseModel):
    queries: list[str] = Field(min_length=1, max_length=3,
        description="1-3 search queries covering different angles of the question")
    top_k_per_query: int = 5
    score_threshold: float = 0.3
    search_mode: str = "hybrid"  # "hybrid" | "dense" | "sparse"
    metadata_filter: dict = {}
```

Each query runs through the full retrieval graph independently in parallel. Results are merged and globally deduped before returning.

**Why:** the LLM's query variants are semantic paraphrases and vocabulary shifts — LLM-quality expansion that consistently outperforms server-side synonym expansion.

## 2. Fingerprint-Based Global Deduplication

After merging results from N parallel queries, deduplicate before returning. Sort by score first (highest wins):

```python
def dedup_global(passages: list[Passage]) -> list[Passage]:
    passages.sort(key=lambda p: p.score, reverse=True)
    seen: set[str] = set()
    unique: list[Passage] = []
    for p in passages:
        key = p.chunk_id or f"{p.url}|{p.text[:200].lower().replace(' ', '')}"
        if key not in seen:
            unique.append(p)
            seen.add(key)
    return unique
```

Without this, query variants that retrieve the same chunk produce duplicate context in the LLM's window.

This pattern is also implemented in the [[RAG Retrieval Strategies]] `EnsembleRetriever` at the library level.

## 3. Typed Response Contract

Don't let the service return "whatever the graph state contains." Enforce the contract at the HTTP boundary with a Pydantic response model:

```python
class Passage(BaseModel):
    text: str
    url: str | None
    title: str | None
    score: float
    chunk_id: str | None = None

class QueryResponse(BaseModel):
    passages: list[Passage]
    retrieval_strategy: str   # "crag" | "snippet" | "direct"
    query_count: int
    latency_ms: int
```

**Benefits:**
- Validates output at runtime — catches schema drift before it reaches the caller
- Auto-generates OpenAPI docs
- `latency_ms` and `retrieval_strategy` enable debugging without opening LangFuse

## Full Endpoint Pattern

```python
@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    start = time.monotonic()
    results = await asyncio.gather(*[
        retrieval_graph.ainvoke({"query": q, "metadata_filter": request.metadata_filter})
        for q in request.queries
    ])
    all_passages = [p for r in results for p in r["reranked_chunks"]]
    unique = dedup_global(all_passages)[:request.top_k_per_query]
    return QueryResponse(
        passages=[Passage.model_validate(p.model_dump()) for p in unique],
        retrieval_strategy=results[0].get("strategy", "crag"),
        query_count=len(request.queries),
        latency_ms=int((time.monotonic() - start) * 1000),
    )
```

## See Also
- [[RAG Retrieval Strategies]]
- [[LangGraph CRAG Pipeline]]
- [[Librarian RAG Architecture]]
