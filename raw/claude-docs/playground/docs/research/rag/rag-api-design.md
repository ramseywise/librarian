# RAG API Design Patterns

**Source:** librarian-ts-parity-research  
**Relevance:** How to expose a RAG service cleanly — multi-query surface, deduplication, typed response contract

---

## Three Patterns Worth Adopting

### 1. Multi-Query API Surface (LLM controls query count)

Don't make the retrieval service accept a single query. Let the calling LLM send 2-3 reformulations — it knows better than the service what angles are worth searching.

```python
class QueryRequest(BaseModel):
    queries: list[str] = Field(min_length=1, max_length=3,
        description="1-3 search queries covering different angles of the question")
    top_k_per_query: int = 5
    score_threshold: float = 0.3
    search_mode: str = "hybrid"  # "hybrid" | "dense" | "sparse"
    metadata_filter: dict = {}
```

Each query runs through the full CRAG graph (or retrieval subgraph) independently in parallel. Results are merged and globally deduped before returning.

**Why:** the LLM's query variants are LLM-quality (semantic paraphrases, vocabulary shifts) vs rule-based synonyms. This consistently outperforms server-side expansion in practice.

### 2. Fingerprint-Based Global Deduplication

After merging results from N parallel queries, deduplicate before returning. Sort by score first (highest wins):

```python
def dedup_global(passages: list[Passage]) -> list[Passage]:
    passages.sort(key=lambda p: p.score, reverse=True)
    seen: set[str] = set()
    unique: list[Passage] = []
    for p in passages:
        # chunk_id is stable; fallback to content fingerprint
        key = p.chunk_id or f"{p.url}|{p.text[:200].lower().replace(' ', '')}"
        if key not in seen:
            unique.append(p)
            seen.add(key)
    return unique
```

Without this, query variants that retrieve the same chunk produce duplicate context in the LLM's window.

### 3. Typed Response Contract at the HTTP Layer

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
- Makes the calling agent's type alignment trivial — the `Passage` type in TS/Python mirrors this model exactly
- `latency_ms` and `retrieval_strategy` in the response enable debugging without opening LangFuse

---

## Full Endpoint Pattern

```python
@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    start = time.monotonic()
    
    # Run all queries in parallel
    results = await asyncio.gather(*[
        retrieval_graph.ainvoke({"query": q, "metadata_filter": request.metadata_filter})
        for q in request.queries
    ])
    
    # Merge + dedup + rerank
    all_passages = [p for r in results for p in r["reranked_chunks"]]
    unique = dedup_global(all_passages)[:request.top_k_per_query]
    
    return QueryResponse(
        passages=[Passage.model_validate(p.model_dump()) for p in unique],
        retrieval_strategy=results[0].get("strategy", "crag"),
        query_count=len(request.queries),
        latency_ms=int((time.monotonic() - start) * 1000),
    )
```

---

## See Also
- [rag-component-tradeoffs.md](rag-component-tradeoffs.md) — component decisions feeding this service
- [agentic-rag-patterns.md](agentic-rag-patterns.md) — Self-RAG, multi-query, dedup patterns
- [rag-integration-strategy.md](rag-integration-strategy.md) — RAG as service vs subgraph trade-off
