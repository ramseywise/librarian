---
title: Librarian Project
tags: [rag, langgraph, project]
summary: The Librarian service — a LangGraph CRAG-based RAG pipeline for knowledge retrieval, deployed as a Python FastAPI service with evaluation harness.
updated: 2026-04-24
sources:
  - raw/playground-docs/librarian-stack-audit.md
  - raw/playground-docs/librarian-architecture-decisions.md
  - raw/playground-docs/rag-tradeoffs.md
  - raw/playground-docs/librarian-ts-parity-research.md
  - raw/playground-docs/rag-core-infra-review.md
  - raw/claude-docs/playground/docs/archived/librarian-prod-hardening/plan.md
  - raw/claude-docs/playground/docs/archived/retrieval-pipeline-prod/plan.md
  - raw/claude-docs/playground/docs/archived/librarian-hardening/plan.md
  - raw/claude-docs/playground/docs/archived/librarian-rag-upgrade/plan.md
---

# Librarian Project

## What It Is

The Librarian is a RAG (Retrieval-Augmented Generation) service — a production-quality Python knowledge retrieval pipeline. It answers questions by: analyzing query intent, retrieving relevant document chunks (hybrid search), reranking with a cross-encoder, applying a CRAG confidence gate, and generating a grounded response with citations.

**Current home:** `playground/src/` (the "playground" name is misleading — this is production-quality infrastructure).

## Stack

| Layer | Technology |
|---|---|
| Orchestration | LangGraph `StateGraph` with CRAG loop |
| Embeddings | `intfloat/multilingual-e5-large` (1024-dim, local) |
| Vector store | ChromaDB (dev), OpenSearch (prod) |
| Reranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` (local) |
| Generation | Claude Sonnet 4.6 via `anthropic` SDK directly (LangChain deps dropped) |
| Storage | DuckDB (metadata + snippet FTS) |
| Observability | structlog + LangFuse (opt-in) |
| API | FastAPI (existing, not yet deployed) |
| Eval | Custom harness + ragas + deepeval |
| Package manager | uv |

## Five-Agent Architecture

See [[Librarian RAG Architecture]] for the full component breakdown. Summary:
1. **PlannerAgent** — intent classification, query expansion, retrieval mode selection (rule-based, zero LLM cost)
2. **RetrieverAgent** — multi-query hybrid search, CRAG grading
3. **RerankerAgent** — cross-encoder reranking, confidence scoring
4. **GeneratorAgent** — intent-aware prompting, Claude Sonnet, citation extraction
5. **Eval Suite** — golden datasets, regression floors, LLM-as-judge, failure clustering

## Key Architectural Decisions

| Decision | Choice | ADR |
|---|---|---|
| Orchestration framework | LangGraph (not ADK) | [[ADK vs LangGraph Decision]] |
| Production deployment | Polyglot (TS + Python service) | [[Orchestration Architecture Decision]] |
| Retrieval backend | Bedrock KB first, then LangGraph CRAG | [[Bedrock KB vs LangGraph Decision]] |
| Observability | LangFuse first, LangSmith later | [[Observability — LangFuse vs LangSmith Decision]] |

## Repository Structure

```
playground/src/
  orchestration/
    langgraph/     # LangGraph CRAG pipeline (primary)
    adk/           # ADK variants (experimental — BedrockKBAgent, CustomRAGAgent, LibrarianADKAgent)
    factory.py     # create_librarian(), create_agents()
    service.py     # run_query() — strategy-agnostic entry point (ORCHESTRATION_STRATEGY env var)
  librarian/
    retrieval/     # RetrieverAgent + backend implementations
    reranker/      # RerankerAgent + cross-encoder/LLM listwise
    generation/    # GeneratorAgent + intent-aware prompts
    history.py     # CondenserAgent (multi-turn query rewriting)
    query_understanding.py  # PlannerAgent, QueryAnalyzer, QueryRouter
  interfaces/
    api/           # FastAPI routes (/query endpoint)
    mcp/           # MCP servers for RAG, S3, Snowflake
  eval_harness/    # EvalRunner, CapabilityPipeline, RegressionPipeline
```

## Production-Readiness Status (from review 2026-04-12)

**Completed (305+ tests passing):**
- Restructure: `rag_core/` module organization
- `setup.sh` and Makefile
- OTel integration (`setup_otel()`, idempotent, soft-fail)
- Docker Compose health checks + Jaeger tracing service
- mypy config + asyncio_mode = "auto"
- Phase 1 bug fixes: broken import paths, async I/O hazards, SQL injection in DuckDB, Chroma blocking calls wrapped in `asyncio.to_thread`
- Phase 2 factory completion: `bm25_weight`/`vector_weight` forwarded, embedder strategy dispatch, chunker strategy dispatch, CORS hardened
- Hardening: HistoryCondenser (multi-turn query rewrite, Haiku), RRF scoring, query cache, async parallel embedding, LangChain deps dropped → direct `anthropic` SDK
- RAG upgrade: `EnsembleRetriever` with fingerprint dedup, `RAGResponse` Pydantic model, `BaseTool` protocol
- Prod hardening (P0): embedder warmup, persistent LangGraph checkpointer, Anthropic API retry (`max_retries=3`), escalation signal in API response
- Prod hardening (P1/P2): Chroma write guard, embedding model version pinning, `pyproject.toml` entry points corrected post-restructure

**Known gaps vs ts_google_adk parity:**
1. `/query` endpoint takes single `query: str` — LLM caller can't drive multi-query. Target: `queries: List[str]` (1-3)
2. No cross-query dedup across parallel API calls (fingerprint dedup exists within `EnsembleRetriever`)
3. HTTP contract not yet Pydantic `QueryResponse(passages, retrieval_strategy, query_count, latency_ms)`

## Development

```bash
cd playground
uv sync
uv run pytest tests/librarian/ -v          # full suite
uv run pytest tests/librarian/unit/ -v    # unit only (fast)
LANGFUSE_ENABLED=true uv run pytest ...   # with observability
```

## This Wiki Repo

The `librarian` GitHub repo (this one) is a separate knowledge base following the [[Karpathy LLM Wiki Pattern]] — not to be confused with the Librarian *service* in `playground/src/`. This wiki is the knowledge management layer; the playground codebase is the RAG service implementation.

## See Also
- [[Librarian RAG Architecture]]
- [[LangGraph CRAG Pipeline]]
- [[RAG Retrieval Strategies]]
- [[Production Hardening Patterns]]
- [[ADK vs LangGraph Decision]]
- [[Karpathy LLM Wiki Pattern]]
