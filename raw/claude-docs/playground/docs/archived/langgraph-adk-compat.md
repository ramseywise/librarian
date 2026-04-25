# Plan: LangGraph ↔ ADK Compatibility

**Status:** Draft — awaiting review  
**Scope:** `src/orchestration/` — no changes to `librarian/`, `interfaces/`, or storage layers

---

## Problem Statement

There are two orchestration paradigms in the codebase, both intentionally present for A/B comparison:

| | LangGraph | ADK (`CustomRAGAgent`) |
|---|---|---|
| **Strategy** | Deterministic CRAG loop | LLM-driven tool selection |
| **Components** | `RetrieverAgent`, `RerankerAgent`, `GeneratorAgent`, `CondenserAgent` | `search_knowledge_base`, `rerank_results`, `condense_query`, `analyze_query` tools |
| **State** | `LibrarianState` TypedDict | Flat dict inputs/outputs per tool |
| **Retry logic** | Graph conditional edge (CRAG) | Gemini decides when to call again |

The problem: **the ADK tools in `tools.py` re-implement the same retrieval and reranking logic** that already exists in the LangGraph agent classes. Today:

- `search_knowledge_base` duplicates `RetrieverAgent.run()` — but is missing caching, dedup, grading, and multi-query expansion
- `rerank_results` duplicates `RerankerAgent.run()` — requires callers to reconstruct `GradedChunk` objects from raw dicts
- `condense_query` duplicates `CondenserAgent.condense()` — with its own system prompt string literal

Separately, `tools.py` still has the `from playground.src.clients.llm import LLMClient` path bug missed in the earlier cleanup pass.

---

## What We Are NOT Doing

- **Not unifying the two paradigms.** LangGraph's deterministic graph and ADK's LLM-driven tool calling are intentionally different — they exist to test different hypotheses. Keep them separate.
- **Not defining a shared `RAGContext` Pydantic model.** `LibrarianState` as a TypedDict is sufficient. Adding a parallel model adds indirection for no gain.
- **Not wrapping the LangGraph graph inside ADK or vice versa** beyond what `LibrarianADKAgent` (`hybrid_agent.py`) already does.

---

## Solution: Agent Objects as the Shared Component Layer

The LangGraph agent classes (`RetrieverAgent`, `RerankerAgent`, `CondenserAgent`) are already stateless, protocol-based, and have clean `async run(state)` methods. They are the right canonical implementations.

**The ADK tools should be thin adapters over these agent objects, not reimplementations.**

```
Before:
  tools.py  ──────────────────────────── Retriever, Embedder, Reranker (raw)
  LangGraph nodes ─────────────────────  RetrieverAgent, RerankerAgent (wrapping same raw components)

After:
  tools.py  ──── RetrieverAgent ───────┐
  LangGraph ───── RetrieverAgent ──────┤── same object, one implementation
                                        └── Retriever, Embedder (raw, owned by agent)
```

---

## Implementation Steps

### Step 0 — Fix remaining bad import in `tools.py`

**File:** `src/orchestration/adk/tools.py:15`

```python
# Before
from playground.src.clients.llm import LLMClient

# After
from clients.llm import LLMClient
```

This was missed in the cleanup pass and is a blocking import error.

---

### Step 1 — Update `ToolDeps` to hold agent objects

**File:** `src/orchestration/adk/tools.py`

Replace the raw component fields with agent objects. Keep `condenser_llm` removed (it's now encapsulated inside `CondenserAgent`).

```python
# Before
@dataclass
class ToolDeps:
    retriever: Retriever
    embedder: Embedder
    reranker: Reranker
    condenser_llm: LLMClient | None = None
    analyzer: QueryAnalyzer | None = None

# After
@dataclass
class ToolDeps:
    retriever_agent: RetrieverAgent
    reranker_agent: RerankerAgent
    condenser_agent: CondenserAgent
    analyzer: QueryAnalyzer
```

Update `configure_tools()` signature to match:

```python
def configure_tools(
    retriever_agent: RetrieverAgent,
    reranker_agent: RerankerAgent,
    condenser_agent: CondenserAgent,
    *,
    analyzer: QueryAnalyzer | None = None,
) -> ToolDeps: ...
```

Remove `_check_configured` backward-compat alias (line 87 — nothing external uses it).

---

### Step 2 — Delegate tool functions to agent objects

**File:** `src/orchestration/adk/tools.py`

Each tool becomes a thin adapter:

**`search_knowledge_base`** — delegates to `RetrieverAgent.run()`:
```python
async def search_knowledge_base(query: str, num_results: int = 10) -> dict[str, Any]:
    deps = _get_deps()
    state: LibrarianState = {"query": query, "standalone_query": query}
    result = await deps.retriever_agent.run(state)
    graded = result["graded_chunks"]
    return {
        "results": [
            {
                "text": g.chunk.text,
                "url": g.chunk.metadata.url,
                "title": g.chunk.metadata.title,
                "score": round(g.score, 4),
                "chunk_id": g.chunk.id,
            }
            for g in graded[:num_results]
        ],
        "total": len(graded),
    }
```

Side effect: gains caching, dedup, and relevance grading for free.

**`rerank_results`** — delegates to `RerankerAgent.run()`:
```python
async def rerank_results(
    query: str, passages: list[dict[str, Any]], top_k: int = 3
) -> dict[str, Any]:
    deps = _get_deps()
    graded_chunks = _passages_to_graded_chunks(passages)  # local helper, keep as-is
    state: LibrarianState = {
        "query": query,
        "graded_chunks": graded_chunks,
    }
    result = await deps.reranker_agent.run(state)
    reranked = result["reranked_chunks"]
    return {
        "results": [
            {
                "text": r.chunk.text,
                "url": r.chunk.metadata.url,
                "title": r.chunk.metadata.title,
                "relevance_score": round(r.relevance_score, 4),
                "rank": r.rank,
                "chunk_id": r.chunk.id,
            }
            for r in reranked
        ],
        "confidence": round(result["confidence_score"], 4),
    }
```

**`condense_query`** — delegates to `CondenserAgent.condense()`:
```python
async def condense_query(
    query: str, conversation_history: list[dict[str, str]]
) -> dict[str, Any]:
    deps = _get_deps()
    if not conversation_history or len(conversation_history) < 2:
        return {"standalone_query": query, "was_rewritten": False}
    state: LibrarianState = {"query": query, "messages": conversation_history}
    result = await deps.condenser_agent.condense(state)
    standalone = result["standalone_query"]
    return {"standalone_query": standalone, "was_rewritten": standalone != query}
```

**`analyze_query`** — already calls `QueryAnalyzer` directly, which is the canonical implementation. No change needed.

**`escalate`** — pure logic, no component dependency. No change needed.

---

### Step 3 — Update `custom_rag_agent.py` to build and pass agent objects

**File:** `src/orchestration/adk/custom_rag_agent.py`

The `CustomRAGAgent.__init__` currently receives raw `Retriever`, `Embedder`, `Reranker`, `LLMClient` and calls `configure_tools(retriever=..., embedder=..., reranker=...)`. Update it to build agent objects and pass them:

```python
def __init__(
    self,
    retriever: Retriever,
    embedder: Embedder,
    reranker: Reranker,
    llm: LLMClient,
    *,
    top_k: int = 10,
    reranker_top_k: int = 3,
    ...
) -> None:
    retriever_agent = RetrieverAgent(retriever=retriever, embedder=embedder, top_k=top_k)
    reranker_agent = RerankerAgent(reranker=reranker, top_k=reranker_top_k)
    condenser_agent = CondenserAgent(llm=llm)
    configure_tools(
        retriever_agent=retriever_agent,
        reranker_agent=reranker_agent,
        condenser_agent=condenser_agent,
    )
    ...
```

**ADR**: `top_k` and `reranker_top_k` params are added to `CustomRAGAgent.__init__` so the caller can tune them consistently with `build_graph()`. Previously these were hardcoded to the defaults inside `RetrieverAgent`/`RerankerAgent`.

---

### Step 4 — Update `factory.py` to share agent objects

**File:** `src/orchestration/factory.py`

Currently `create_librarian()` calls `build_graph()` which internally instantiates agent objects. There's no way to extract those agents for reuse in `CustomRAGAgent`.

Add a `create_agents()` builder that returns the agent objects, then have both `build_graph()` and `CustomRAGAgent` use it:

```python
def create_agents(cfg: LibrarySettings | None = None) -> tuple[
    RetrieverAgent, RerankerAgent, GeneratorAgent, CondenserAgent
]:
    """Build the canonical set of RAG agents from config.

    Returns a tuple of (retriever_agent, reranker_agent, generator_agent, condenser_agent).
    Use this to share agent objects across LangGraph and ADK orchestration.
    """
    ...
```

Then `create_librarian()` calls `create_agents()` and passes the results to `build_graph()`, and `create_custom_rag_agent()` calls `create_agents()` and passes the results to `CustomRAGAgent`.

This means both orchestrators use **the same instantiated agent objects** (same cache, same reranker model, same condenser LLM) when built from the same config — no divergence.

---

### Step 5 — Update tests

**File:** `tests/orchestration/adk/test_tools.py` (~20 call sites)

`configure_tools` calls change from raw components to agent objects:

```python
# Before
configure_tools(retriever=MagicMock(), embedder=MagicMock(), reranker=MagicMock())

# After
configure_tools(
    retriever_agent=RetrieverAgent(retriever=MagicMock(), embedder=MagicMock()),
    reranker_agent=RerankerAgent(reranker=MagicMock()),
    condenser_agent=CondenserAgent(llm=MagicMock()),
)
```

Tests that previously mocked `deps.embedder.aembed_query` or `deps.retriever.search` should now mock at the agent level: `deps.retriever_agent._retriever.search`. Most test assertions (tool return shape, logging) remain unchanged.

**File:** `tests/orchestration/adk/test_custom_rag_agent.py`

Update the `configure_tools` mock assertion to match the new signature.

---

## File Change Summary

| File | Change |
|---|---|
| `src/orchestration/adk/tools.py` | Fix import path; update `ToolDeps` + `configure_tools`; delegate tool functions to agents |
| `src/orchestration/adk/custom_rag_agent.py` | Build agent objects; pass to `configure_tools`; add `top_k` / `reranker_top_k` params |
| `src/orchestration/factory.py` | Add `create_agents()` builder; refactor `create_librarian()` and new `create_custom_rag_agent()` to use it |
| `tests/orchestration/adk/test_tools.py` | Update `configure_tools` call sites (~20) to pass agent objects |
| `tests/orchestration/adk/test_custom_rag_agent.py` | Update mock assertions |

**No changes to:**
- `src/orchestration/langgraph/` — graph, nodes, history all stay as-is
- `src/orchestration/adk/hybrid_agent.py` — already delegates to `create_librarian()`
- `src/interfaces/` — API layer unchanged
- `librarian/` — all agent logic stays in place

---

## What This Buys

| Problem | Before | After |
|---|---|---|
| Logic duplication | `search_knowledge_base` reimplements embed+search | Delegates to `RetrieverAgent.run()` |
| Missing features | Tool missing caching, dedup, grading | Gets them for free from the agent |
| Condenser system prompt drift | Separate string literal in tools.py | `CondenserAgent._SYSTEM_PROMPT` is the source of truth |
| Component instantiation | Raw Retriever/Embedder/Reranker duplicated across tools + graph | Built once via `create_agents()`, shared |
| `top_k` tuning | Hardcoded inside agent defaults | Configurable from `CustomRAGAgent` caller |

---

## Out of Scope (follow-on work)

- **`BedrockKBAgent`** — wraps Bedrock entirely, no overlap with the agent classes. Leave as-is.
- **`LibrarianADKAgent` / `hybrid_agent.py`** — already correct. Leave as-is.
- **Multi-query expansion in ADK tools** — `search_knowledge_base` will now call `RetrieverAgent.run()` with `query_variants=[]`, so it still does single-query retrieval. The ADK LLM can call the tool multiple times for different variants. This is intentional — it's the hypothesis under test.
- **Streaming via ADK** — not addressed here; `CustomRAGAgent` doesn't stream today.
