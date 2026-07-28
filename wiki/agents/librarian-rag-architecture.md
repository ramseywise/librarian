---
title: Librarian RAG Architecture
tags: [rag, langgraph, pattern]
summary: The five-agent Librarian pipeline — Plan, Retrieval, Reranker, Generation, and Eval agents wired by a LangGraph StateGraph with CRAG retry loop.
updated: 2026-04-24
sources:
  - raw/playground-docs/librarian-stack-audit.md
  - raw/playground-docs/librarian-architecture-decisions.md
  - raw/playground-docs/rag-tradeoffs.md
  - raw/claude-docs/playground/docs/archived/librarian-rag-upgrade/plan.md
  - raw/claude-docs/playground/docs/archived/librarian-hardening/plan.md
  - raw/claude-docs/playground/docs/archived/librarian-prod-hardening/plan.md
---

# Librarian RAG Architecture

## Overview

Five agents wired together via a single `StateGraph(LibrarianState)`. No agent calls another directly. The graph topology is the only coupling, defined in one ~240-line file.

```
START → condense → analyze → [3-way route]
                               |
         +---------------------+------------------+
         v                     v                  v
     retrieve            snippet_retrieve     generate (direct)
         |                     |                  |
         v                     +→ generate        |
      rerank                                      |
         |                                        |
         v                                        |
       gate ─── retry? ──→ retrieve               |
         |                                        |
         v                                        |
     generate ←────────────────────────────────--+
         |
        END
```

## Agent 1: PlannerAgent (Query Understanding)

**Location:** `orchestration/query_understanding.py`

| Tool | Implementation | What it does |
|---|---|---|
| Intent Classifier | `QueryAnalyzer._classify_intent()` | Keyword-match → 5 intents: LOOKUP, EXPLORE, COMPARE, CONVERSATIONAL, OUT_OF_SCOPE |
| Entity Extractor | `QueryAnalyzer._extract_entities()` | Regex for version, date, quantity, identifier |
| Sub-query Decomposer | `QueryAnalyzer._decompose()` | Splits on `?` and conjunctions |
| Complexity Scorer | `QueryAnalyzer._score_complexity()` | simple/moderate/complex |
| Term Expander | `QueryAnalyzer._expand_terms()` | Dictionary-based synonym expansion |
| Retrieval Mode Selector | `QueryAnalyzer._select_retrieval_mode()` | Maps (intent × complexity) → dense/hybrid/snippet |
| Query Router | `QueryRouter.route()` | 3-way: retrieve / direct / clarify |

**Strategy:** rule-based first (zero LLM cost, deterministic). LLM path via `planning_mode="llm"` config stub.

## Agent 2: RetrieverAgent

**Location:** `retrieval/`, `orchestration/subgraphs/retrieval.py`

- **Bi-encoder:** `multilingual-e5-large` (1024-dim), E5 prefix rule enforced at Protocol level
- **Default vector store:** ChromaDB persistent HNSW, cosine distance
- **Fusion:** RRF (Reciprocal Rank Fusion) — replaces linear weighted scoring for robustness
- **Multi-query fan-out:** `EnsembleRetriever` runs all query variants × all retrievers in parallel via `asyncio.gather`; fingerprint dedup (`sha256(url|content[:200])`) keeps highest-scored copy
- **Query cache:** LRU 256, TTL 300s, keyed on `(sha256(query), strategy)` — invalidated on corpus update
- **CRAG Grader:** marks each chunk `relevant=True/False` based on `score >= score_threshold`
- **Snippet path:** DuckDB FTS — fast keyword path for simple factual lookups, bypasses embedding + reranking

## Agent 3: RerankerAgent

**Location:** `reranker/`, `orchestration/subgraphs/reranker.py`

- **Default:** `CrossEncoderReranker` (`ms-marco-MiniLM-L-6-v2`), ~50ms for 10 pairs on CPU
- **Experimental:** `LLMListwiseReranker` (Haiku), 400–800ms, best quality
- **Confidence score:** `max(relevance_scores)` → feeds QualityGate
- **Pre-filter:** only `relevant=True` chunks pass to reranker (fallback: all if none pass)

## Agent 4: GeneratorAgent

**Location:** `generation/`, `orchestration/subgraphs/generation.py`

- **LLM:** `anthropic.AsyncAnthropic` (direct SDK — `langchain-anthropic` dependency dropped)
- **Intent-aware system prompts:** 5 prompts keyed by intent (LOOKUP: cite inline; EXPLORE: synthesize across sources; COMPARE: use tables; CONVERSATIONAL: respond naturally)
- **Structured output:** returns `RAGResponse` Pydantic model for retrieval intents; raw text for conversational/out-of-scope

```python
class Citation(BaseModel):
    url: str
    title: str
    snippet: str = ""

class RAGResponse(BaseModel):
    answer: str
    citations: list[Citation]
    confidence: Literal["high", "medium", "low"]
    follow_up: str = ""
```

System prompt instructs Claude to respond in JSON matching the schema. Fallback: if JSON parsing fails, wraps raw text in `RAGResponse(confidence="low")`.

- **CRAG gate:** `confidence_score < threshold (0.3)` → `fallback_requested=True` → retry. After `max_crag_retries` (default 1), generates from whatever is available
- **Escalation signal:** `escalate = not confident or fallback_requested` surfaces in API response for frontend handoff

## Agent 5: Eval Suite

**Location:** `eval_harness/`, `tests/librarian/evalsuite/`

- **Golden dataset:** 5 hand-curated samples with validation_level (gold/silver/bronze/synthetic) and difficulty
- **Three tiers:** unit tests (mocks), regression tests (InMemory + floors: hit_rate@5 ≥ 0.6, MRR ≥ 0.4), capability tests (end-to-end + LLM judge, cost-gated)
- **Failure clusterer:** 11 failure types, pattern detection, actionable fix suggestions
- **LangFuse score push:** opt-in, logs hit_rate and MRR as trace scores

See [[RAG Evaluation]] for full detail.

## Component Choice Summary

| Stage | Active | Swap path |
|---|---|---|
| Chunking | `HtmlAwareChunker` (heading-boundary) | `ParentDocChunker` for long docs |
| Embeddings | `multilingual-e5-large` (1024-dim) | `e5-large-v2` (English-only), Voyage API |
| Vector store | ChromaDB (HNSW, local) | OpenSearch (prod), DuckDB (SQL joins) |
| Hybrid retrieval | term-overlap + cosine (0.3/0.7) | Native BM25+kNN (OpenSearch) |
| Reranking | `ms-marco-MiniLM-L-6-v2` | `bge-reranker-large`, Cohere API |
| Generation | Claude Sonnet 4.6 (LangChain) | Haiku (cheap), Ollama (free) |
| Query planner | Rule-based regex | LLM classifier (`planning_mode=llm`) |
| Orchestration | LangGraph CRAG | ADK hybrid wrapper (see [[Orchestration Architecture Decision]]) |
| Observability | structlog + LangFuse (opt-in) | LangSmith, OTel |

## ADK Vocabulary Alignment

SubGraph classes were renamed to `*Agent` naming (RetrieverAgent, RerankerAgent, etc.) for readability to engineers familiar with ADK/CrewAI. Each class has:
- `name: str` and `description: str` class attributes
- `as_node()` method for LangGraph wiring
- `instruction` property (where applicable)

See [[ADK vs LangGraph Comparison]] for the research behind this decision.

## BaseTool Protocol — Framework-Agnostic Tools

A minimal tool abstraction that both LangGraph and ADK can consume without reimplementation:

```python
class BaseTool(Protocol):
    name: str
    description: str
    input_schema: type[ToolInput]
    output_schema: type[ToolOutput]

    async def run(self, input: ToolInput) -> ToolOutput: ...
```

`RetrieverTool` wraps `EnsembleRetriever` and exposes explicit I/O schema:

```python
class RetrieverToolInput(ToolInput):
    queries: list[str] = Field(min_length=1, max_length=3)
    num_results: int = Field(default=10, ge=1, le=50)
```

ADK adapter: `search_knowledge_base()` builds `RetrieverToolInput` from args → calls `RetrieverTool.run()` → returns `.model_dump()`.
LangGraph adapter: `RetrieverAgent.__init__` accepts a `RetrieverTool` directly.

This makes it trivial to wrap retrieval for any new framework (LangGraph ToolNode, ADK FunctionTool, future Python Agent SDK).

## Production Readiness Notes

**Completed (305+ tests passing):**
- Phase 1 bug fixes: broken import paths, async I/O hazards, SQL injection in DuckDB, Chroma blocking calls
- Phase 2 factory completion: `bm25_weight`/`vector_weight` forwarded, embedder strategy dispatch, chunker strategy dispatch, CORS hardened
- Hardening: HistoryCondenser, RRF scoring, query cache, async embedding, LangChain deps dropped
- Prod hardening: embedder warmup, persistent checkpointer, API retry, escalation signal, model version pinning

**Remaining gaps vs ts_google_adk:**
1. **Multi-query API surface** — `/query` endpoint takes single `query: str`; the LLM caller can't drive multi-query. Should accept `queries: List[str]` (1-3).
2. **Global dedup** — fingerprint dedup exists within `EnsembleRetriever`; no cross-query dedup across parallel API calls.
3. **Pydantic response schema** — HTTP contract should be explicit `QueryResponse(passages, retrieval_strategy, query_count, latency_ms)`.

## See Also
- [[LangGraph CRAG Pipeline]]
- [[RAG Retrieval Strategies]]
- [[RAG Reranking]]
- [[RAG Evaluation]]
- [[Production Hardening Patterns]]
- [[ADK vs LangGraph Comparison]]
- [[Librarian Project]]
- [[Orchestration Architecture Decision]]
