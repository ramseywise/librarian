# Librarian Hardening Plan

> Eliminate `Any` type erosion, drop unnecessary LangChain deps, add multi-turn conversation, and improve retrieval quality.

Date: 2026-04-10
Status: Complete — 2026-04-11

---

## Problem Statement

The librarian is architecturally sound but has four categories of debt that undermine its own design principles:

1. **Type safety erosion** — `Any` types in the factory and subgraphs defeat the Protocol-based DI that the system was designed around
2. **LangChain dependency bloat** — `langchain-core` and `langchain-anthropic` are pulled in for ~3 types (`SystemMessage`, `HumanMessage`, `ChatAnthropic`) but bring a massive transitive dep tree
3. **No multi-turn conversation** — `state["messages"]` exists but there's no history-aware query reformulation, so coreference ("what about the other one?") breaks retrieval
4. **Basic retrieval scoring** — linear weighted hybrid scoring is fragile; no caching; synchronous embeddings block on multi-query

---

## Step 1: ✅ Replace `Any` types with concrete Protocols

**Scope:** `factory.py`, `orchestration/graph.py`, `orchestration/subgraphs/*.py`, `generation/generator.py`

**What:**
- Replace all `-> Any` return types in factory with their Protocol types (`Embedder`, `Retriever`, `Reranker`)
- Type `llm` parameter as a Protocol (define `LLM Protocol` with `ainvoke` method) instead of `Any`
- Type `create_librarian()` return as `CompiledGraph` (from `langgraph.graph`)
- Type `build_graph()` return as `CompiledGraph`
- Replace `Any` in subgraph constructors and `run()` return types with `dict[str, Any]` (which is the actual LangGraph state patch type)

**Files:**
```
src/agents/librarian/factory.py              # _build_* returns, create_* signatures
src/agents/librarian/orchestration/graph.py  # build_graph return, _make_* returns
src/agents/librarian/orchestration/subgraphs/retrieval.py
src/agents/librarian/orchestration/subgraphs/reranker.py
src/agents/librarian/orchestration/subgraphs/generation.py
src/agents/librarian/generation/generator.py # llm param, messages list
src/agents/librarian/retrieval/base.py       # add LLM Protocol here
```

**New Protocol:**
```python
# retrieval/base.py or a new protocols.py
@runtime_checkable
class ChatModel(Protocol):
    async def ainvoke(self, messages: list[Any]) -> Any: ...
```

**Risk:** Low. Pure type annotation changes + one new Protocol. No runtime behavior change.

**Tests:** Existing tests pass unchanged. Add pyright strict check on factory.py.

**Estimate:** ~1 hour

---

## Step 2: ✅ Drop `langchain-core` and `langchain-anthropic`

**Scope:** `generation/generator.py`, `factory.py`, `schemas/state.py`, `orchestration/subgraphs/generation.py`, `reranker/llm_listwise.py`, `eval_harness/`, `pyproject.toml`

**What:**

Replace `ChatAnthropic` + `SystemMessage`/`HumanMessage`/`AIMessage` with the `anthropic` SDK directly. Keep `langgraph` (it's the real value).

**Substeps:**

### 2a: Define thin message types (or use dicts)

LangGraph's `add_messages` reducer expects objects with a `type` attribute. Options:
- **Option A (recommended):** Define minimal `Message` dataclasses matching LangGraph's expected interface
- **Option B:** Use `langgraph`'s built-in message support if it ships independently of `langchain-core`

> **Decision needed:** Check if `langgraph>=0.4` still requires `langchain-core` as a transitive dependency. If yes, we can't fully drop it but can stop importing from it directly. If no, we define our own.

### 2b: Replace `ChatAnthropic` with `anthropic.AsyncAnthropic`

```python
# generation/generator.py — before
from langchain_anthropic import ChatAnthropic
response = await llm.ainvoke(full_messages)

# after
from anthropic import AsyncAnthropic
response = await client.messages.create(
    model=cfg.anthropic_model_sonnet,
    system=system_prompt,
    messages=[{"role": m.role, "content": m.content} for m in history],
    max_tokens=4096,
)
```

### 2c: Update `LLMListwiseReranker`

Currently calls `self._llm.ainvoke()` with LangChain message format. Switch to anthropic SDK `messages.create()`.

### 2d: Update factory

`_build_llm()` currently returns `ChatAnthropic`. Change to return `anthropic.AsyncAnthropic` client (or a thin wrapper that satisfies the `ChatModel` Protocol from Step 1).

### 2e: Remove from `pyproject.toml`

```diff
- "langchain-core>=0.3.0",
- "langchain-anthropic>=0.3.0",
```

**Risk:** Medium. LangGraph may still require `langchain-core` transitively, so the practical goal is no direct imports and no unnecessary app-level dependency pinning.

**Dependency check command:**
```bash
uv pip show langgraph | grep Requires
```

**Tests:** All unit tests must pass. The `mock_llm` fixture in conftest needs updating (currently mocks `ainvoke` with LangChain `AIMessage` return).

**Estimate:** ~3 hours

---

## Step 3: ✅ Add multi-turn conversation handling

**Scope:** New `HistoryCondenser` node in the graph, between `START` and `analyze`

**What:**

Add a node that rewrites the current query to be self-contained given prior conversation turns. This resolves coreference ("that one", "the other method"), ellipsis ("and for Python?"), and topic shifts.

### 3a: Build `HistoryCondenser`

```
src/agents/librarian/orchestration/history.py
```

**Interface:**
```python
class HistoryCondenser:
    """Rewrites the latest user query to be standalone given conversation history.

    Only fires when len(messages) > 1. For single-turn queries, passes through unchanged.
    Uses Haiku for cost efficiency (~$0.001 per rewrite).
    """
    async def condense(self, state: LibrarianState) -> dict[str, Any]:
        # If single-turn, no-op
        # If multi-turn, call Haiku with:
        #   system: "Rewrite the user's latest message as a standalone query..."
        #   messages: conversation history
        # Return {"standalone_query": rewritten_query}
```

### 3b: Wire into graph

```python
# graph.py
_CONDENSE = "condense"
graph.add_edge(START, _CONDENSE)
graph.add_edge(_CONDENSE, _ANALYZE)
# (previously: graph.add_edge(START, _ANALYZE))
```

### 3c: Add skip logic

When `len(state["messages"]) <= 1`, the condenser writes `standalone_query = query` (no LLM call). This means single-turn queries have zero added latency.

### 3d: Add `conversation_id` to state

```python
class LibrarianState(TypedDict, total=False):
    ...
    conversation_id: str  # groups multi-turn exchanges
    standalone_query: str  # already exists — condenser populates it
```

**Risk:** Low-medium. Adds one LLM call (Haiku, fast + cheap) on multi-turn queries only. No impact on single-turn performance.

**Tests:**
- Unit test: condenser rewrites "what about the other one?" given prior context
- Unit test: condenser passes through single-turn queries unchanged
- Graph test: multi-turn state propagates correctly through the pipeline

**Estimate:** ~2 hours

---

## Step 4: ✅ Retrieval quality improvements

Three independent sub-steps. Can be done in any order.

### 4a: Reciprocal Rank Fusion (RRF) scoring

**Scope:** `retrieval/scoring.py`, `retrieval/infra/chroma.py`, `retrieval/infra/inmemory.py`

**What:**

Replace linear weighted scoring (`0.3 * bm25 + 0.7 * vector`) with Reciprocal Rank Fusion:

```python
def rrf_score(bm25_rank: int, vector_rank: int, k: int = 60) -> float:
    """Reciprocal Rank Fusion: 1/(k+rank_bm25) + 1/(k+rank_vector)"""
    return 1.0 / (k + bm25_rank) + 1.0 / (k + vector_rank)
```

**Why:** Linear combination is sensitive to score distribution differences between BM25 and vector search. RRF is rank-based, so it's robust to this. Typically bumps hit_rate by 3-8% in benchmarks.

**Implementation:**
- In `InMemoryRetriever.search()`: compute BM25 scores and vector scores separately, rank each, apply RRF
- In `ChromaRetriever.search()`: Chroma returns vector distances; compute term_overlap separately; rank each; apply RRF
- Keep linear scoring as a fallback option via config: `HYBRID_SCORING=rrf|linear`

**Tests:** Regression tests must still pass (floors may go up). Add unit test for `rrf_score()`.

**Estimate:** ~1.5 hours

### 4b: Async embedding support

**Scope:** `retrieval/base.py`, `preprocessing/embedding/embedders.py`, `orchestration/subgraphs/retrieval.py`

**What:**

Add async embedding methods to the `Embedder` Protocol:

```python
@runtime_checkable
class Embedder(Protocol):
    def embed_query(self, text: str) -> list[float]: ...
    def embed_passage(self, text: str) -> list[float]: ...
    def embed_passages(self, texts: list[str]) -> list[list[float]]: ...

    # New — async variants for cloud embedding APIs
    async def aembed_query(self, text: str) -> list[float]: ...
    async def aembed_passages(self, texts: list[str]) -> list[list[float]]: ...
```

Update `RetrievalSubgraph.run()` to use `aembed_query` and parallelize multi-query expansion with `asyncio.gather`:

```python
# Before (sequential, blocking)
for variant in variants:
    query_vector = self._embedder.embed_query(variant)
    results = await self._retriever.search(...)

# After (parallel)
vectors = await asyncio.gather(
    *(self._embedder.aembed_query(v) for v in variants)
)
results_lists = await asyncio.gather(
    *(self._retriever.search(v, vec, k=self._top_k)
      for v, vec in zip(variants, vectors))
)
```

For `MultilingualEmbedder` (local SentenceTransformer), `aembed_query` just wraps sync in `asyncio.to_thread()`. For future cloud embedders (Voyage, Cohere), it would be native async httpx.

**Tests:** Update retrieval subgraph tests to verify parallel execution.

**Estimate:** ~2 hours

### 4c: Query result cache

**Scope:** New `retrieval/cache.py`, wire into `RetrievalSubgraph`

**What:**

LRU cache keyed on `(query_hash, retrieval_strategy)` -> `list[RetrievalResult]` with configurable TTL.

```python
class RetrievalCache:
    """Thread-safe LRU cache for retrieval results.

    Keyed on (sha256(query), retrieval_strategy).
    Default: 256 entries, 5-minute TTL.
    """
    def __init__(self, max_size: int = 256, ttl_seconds: int = 300): ...
    def get(self, query: str, strategy: str) -> list[RetrievalResult] | None: ...
    def put(self, query: str, strategy: str, results: list[RetrievalResult]) -> None: ...
```

Wire into `RetrievalSubgraph.run()`:
```python
cached = self._cache.get(variant, cfg.retrieval_strategy) if self._cache else None
if cached:
    all_results.extend(cached)
else:
    results = await self._retriever.search(...)
    if self._cache:
        self._cache.put(variant, cfg.retrieval_strategy, results)
    all_results.extend(results)
```

Cache is optional — injected via factory, disabled in tests.

**Config:**
```python
# LibrarySettings
cache_enabled: bool = True
cache_max_size: int = 256
cache_ttl_seconds: int = 300
```

**Tests:** Unit test cache hit/miss/expiry. Regression tests unaffected (cache disabled in test fixtures).

**Estimate:** ~1.5 hours

---

## Execution Order

| Step | Depends on | Est. | Risk |
|---|---|---|---|
| 1. Replace `Any` types | None | 1h | Low |
| 2. Drop LangChain deps | Step 1 (needs `ChatModel` Protocol) | 3h | Medium |
| 3. Multi-turn condenser | Step 2 (uses new LLM interface) | 2h | Low-medium |
| 4a. RRF scoring | None | 1.5h | Low |
| 4b. Async embeddings | None | 2h | Low |
| 4c. Query cache | None | 1.5h | Low |

**Total estimate:** ~11 hours

Steps 4a/4b/4c are independent of each other and of steps 1-3. Recommended execution:

```
Step 1 -> Step 2 -> Step 3  (serial — each builds on the previous)
Step 4a \
Step 4b  > (parallel — independent, can interleave with above)
Step 4c /
```

---

## Verification

After all steps:

1. `uv run pytest tests/librarian/unit/` — all green
2. `uv run pytest tests/librarian/evalsuite/regression/` — floors maintained or improved
3. `uv run pyright src/agents/librarian/factory.py` — no `Any` in public signatures
4. `uv pip show langgraph | grep Requires` — no `langchain-core` (if achievable)
5. New tests for: `HistoryCondenser`, `rrf_score`, `RetrievalCache`, async embedding paths

---

## Open Questions

1. **LangGraph x LangChain coupling:** Does `langgraph>=0.4` still pull `langchain-core` transitively? If yes, Step 2 becomes "stop importing from it directly" rather than "remove it entirely." Need to check.
2. **RRF k parameter:** Standard is `k=60` (from the original paper). Should we make it configurable or hardcode? Recommend: named constant, configurable later if needed.
3. **Cache invalidation on corpus update:** When new documents are ingested, should the cache be flushed? Recommend: yes, `IngestionPipeline` calls `cache.clear()` after successful ingestion.
4. **Condenser model:** Haiku for cost, or Sonnet for quality? Recommend: Haiku — the rewrite task is simple and latency matters here.
