---
title: Librarian Project
tags: [rag, langgraph, project]
summary: The Librarian service — a LangGraph CRAG-based RAG pipeline for knowledge retrieval, deployed as a Python FastAPI service with evaluation harness.
updated: 2026-07-06
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
  - raw/sessions/claude-2026-04-11-can-we-transfer-the-code-from-cs-agent-a-deb81c96.md
  - raw/sessions/claude-2026-04-11-resolving-deltas-100-72-72-completed-wit-fe1c0bd1.md
  - raw/sessions/claude-2026-04-11-shhould-src-agents-infra-live-under-src-f5cfe1b3.md
  - raw/sessions/claude-2026-04-14-i-want-librarian-to-remain-as-solely-a-h-48cd8a0e.md
  - raw/sessions/claude-2026-04-14-what-is-the-difference-between-playgroun-3def7093.md
  - raw/sessions/claude-2026-04-15-how-does-rag-poc-master-compare-to-playg-b269ccf1.md
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

## Scope Constraint (2026-04-14)

**Librarian is a help-assistant RAG-only service.** It is not a multi-agent copilot, not a task-execution agent, and not a general-purpose assistant. The scope was explicitly locked in session `48cd8a0e` to prevent feature creep — the copilot and polyglot agent work lives in a separate development thread.

This matters because the architecture optimises for one thing: retrieving and synthesising knowledge from a corpus to answer help queries. The five-agent pipeline is deterministic; no agent decides "should I retrieve?" — it always retrieves.

## Key Architectural Decisions

| Decision | Choice | ADR |
|---|---|---|
| Orchestration framework | LangGraph (not ADK) | [[ADK vs LangGraph Decision]] |
| Production deployment | Polyglot (TS + Python service) | [[Orchestration Architecture Decision]] |
| Retrieval backend | Bedrock KB first, then LangGraph CRAG | [[Bedrock KB vs LangGraph Decision]] |
| Observability | LangFuse first, LangSmith later | [[Observability — LangFuse vs LangSmith Decision]] |
| Local dev vs production | Vercel UI + LangGraph BE (dev); Fargate monolith (prod) | Session `fe1c0bd1` |

## Repository Structure

```
playground/src/
  core/            # Shared types only — breaks circular dep between storage and librarian (session deb81c96)
  orchestration/
    langgraph/     # LangGraph CRAG pipeline (primary)
    adk/           # ADK variants (experimental — BedrockKBAgent, CustomRAGAgent, LibrarianADKAgent)
    factory.py     # create_librarian(), create_agents()
    service.py     # run_query() — strategy-agnostic entry point (ORCHESTRATION_STRATEGY env var)
  librarian/
    rag_core/      # eval_harness, generation, ingestion, reranker, retrieval, schemas (session f5cfe1b3)
    history.py     # CondenserAgent (multi-turn query rewriting)
    query_understanding.py  # PlannerAgent, QueryAnalyzer, QueryRouter
  storage/         # Persistence layer — shares types with librarian via core/
  clients/         # External API wrappers: OpenSearch, Anthropic, DuckDB, S3 (session 3def7093)
  interfaces/
    api/           # FastAPI routes (/query endpoint)
    mcp/           # MCP servers for RAG, S3, Snowflake
  eval_harness/    # EvalRunner, CapabilityPipeline, RegressionPipeline
  infra/           # Shared infra (not under librarian/) — config, logging, otel (session f5cfe1b3)
```

**`clients/` vs `interfaces/` distinction** (session `3def7093`):
- `clients/` = external API wrappers that the pipeline calls (OpenSearch client, Anthropic SDK wrapper, DuckDB connection). Stateful, may hold connection pools.
- `interfaces/` = internal contracts between modules — protocol classes, TypedDicts, Pydantic models. Stateless, no I/O. Both layers are needed; collapsing them creates hidden coupling.

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
- [[Librarian Graph Explorer]]
- [[Librarian RAG Architecture]]
- [[LangGraph CRAG Pipeline]]
- [[RAG Retrieval Strategies]]
- [[Production Hardening Patterns]]
- [[ADK vs LangGraph Decision]]
- [[Karpathy LLM Wiki Pattern]]
