---
title: Listen-Wiseer Project
tags: [langgraph, rag, memory, eval, project]
summary: Spotify recommendation agent with ENOA taste-map personalisation — LangGraph ReAct + Chainlit UI, LightGBM classifiers, DuckDB vss RAG, and three-tier eval harness.
updated: 2026-04-24
sources:
  - raw/claude-docs/listen-wiseer/memory/project_listen_wiseer.md
  - raw/claude-docs/listen-wiseer/docs/plans/phase4a_agent_chainlit.md
  - raw/claude-docs/listen-wiseer/docs/plans/phase4b_memory.md
  - raw/claude-docs/listen-wiseer/docs/plans/phase5a_rag.md
  - raw/claude-docs/listen-wiseer/docs/research/eval-harness.md
  - raw/claude-docs/listen-wiseer/docs/research/infra_support.md
  - raw/claude-docs/listen-wiseer/docs/research/peer-repos.md
---

# Listen-Wiseer Project

Personal Spotify recommendation agent personalised to the user's own ENOA taste map — not a generic Spotify wrapper. ENOA (top/left) coordinates encode a 2D emotional/sonic space derived from the user's playlist curation behaviour.

## Stack

| Layer | Technology |
|---|---|
| Orchestration | LangGraph (ReAct agent) |
| UI | Chainlit |
| ML | LightGBM (32 per-playlist classifiers) + GMM (8 components) |
| RAG | DuckDB vss (`rag_chunks` table, `all-MiniLM-L6-v2`, 384-dim) |
| Vector cache | ChromaDB (`artist_info` collection, lazy ingestion) |
| Memory | LangGraph `InMemoryStore` + langmem (episodic/semantic/procedural) |
| Checkpointer | MemorySaver (dev) / AsyncRedisSaver (prod) |
| Data | 595k-row corpus, 2182 tracks, 291 genre mappings |
| Tools | MCP server (8 tools) + StructuredTool wrappers (10 tools) |
| Observability | LangFuse (tracing + scoring) |

## Phase Status (as of 2026-04-06)

| Phase | Status |
|---|---|
| 1 — structlog, Pydantic v2, Polars loader, Spotify OAuth | ✓ Done |
| 2 — GMM + LightGBM; 4 pipelines; 8 MCP tools; 222 tests | ✓ Done |
| 3a–3d — ETL hardening, feature engineering, EDA | ✓ Done |
| 4a — LangGraph ReAct agent + Chainlit UI | ✓ Done |
| 4b — Episodic, semantic, procedural memory (MemorySaver) | ✓ Done |
| 5a — RAG core: DuckDB vss, MiniLM, Wikipedia/Tavily, 93 tests | ✓ Done |
| 5b — Intent routing: 6 nodes, 5 intents, clarification, 10 tools, 97 tests | ✓ Done |
| **5c — Eval harness (LangFuse + golden dataset + intent/tool metrics)** | **UP NEXT** |
| 6a — Playwright UI smoke tests | Planned |
| 6b — Observability dashboard | Planned |

## Graph Topology (post-5b)

```
START → trim_history → classify_intent → [route_after_classify]
    → low confidence  → clarify_or_proceed → END (wait for user)
    → high confidence → rewrite_query (coreference-gated, Haiku) → agent → [route]
        → has tool_calls → call_tools → validate_tool_output → agent (loop)
        → no tool_calls  → END
```

**AgentState:** `messages`, `intent`, `intent_confidence`, `entities`, `query_variants`, `tool_validation_retries`

**5 intents:** `artist_info`, `genre_info`, `recommendation`, `history`, `chit_chat`

**Intent classification:** pure keyword matching; confidence = `min(1.0, matched_keywords / 3)`; default fallback `artist_info` at 0.3.

## Key Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Tool wiring | StructuredTool wrapping (direct Python) | No process management; testable without live MCP server |
| Vector store (RAG) | DuckDB vss | Zero extra deps; same DB file; `array_cosine_similarity()` fast enough at <10k chunks |
| RAG ingestion | Lazy Wikipedia/Tavily on first query | Avoid pre-ingesting all artists; cached in `rag_chunks` |
| Artist info collection | Single `artist_info` ChromaDB collection + metadata filter | Simpler than per-artist collections |
| Memory store | `InMemoryStore` + sentence-transformers (local) | No OpenAI dependency; reuses same model as Track2Vec |
| Checkpointer | MemorySaver (dev) / AsyncRedisSaver (prod, gated on `REDIS_URL`) | No Redis overhead in dev |
| LLM client | `langchain-anthropic` `ChatAnthropic` over raw SDK | LangFuse span visibility |
| Eval framework | LangFuse + RAGAS + DeepEval | LangFuse: free tier + RAGAS native integration; DeepEval: `ToolCorrectnessMetric` fills agent eval gap |

## Corpus Facts

- 595,858 tracks; 12 audio features + 2 ENOA spatial + 32 one-hot dims ≈ 46 effective dims
- 2182 enriched tracks; 291 genre mappings; 1456 named artists
- `genre_xy` table: 6291 ENOA genres with top/left/color coordinates
- ENOA differentiator: encodes user's own playlist curation patterns, not algorithmic similarity
- Brute-force cosine ~200ms on CPU; FAISS deferred (not a blocker)
- `audio-features` Spotify endpoint dead (403, deprecated 2025) — use corpus values

## Active Gotchas

- **Git LFS blocker**: `listen_wiseer.db` via LFS — other envs can't pull. Decision deferred.
- `models/` and `data/cache/` gitignored — regenerate after pull with `make train`
- `RecommendationEngine` raises `FileNotFoundError` if pkl files missing — wrap in try/except
- **32 test failures** are all `duckdb.IOError` (missing LFS DB) — not regressions
- `full tests/unit/` suite hangs on some later test files — use targeted runs
- **REDIS_URL** needed for cross-session memory persistence; `InMemoryStore` for dev

## Gaps vs Peer Repos

From research into three peer Spotify agent repos:

| Gap | Missing capability |
|---|---|
| No listening history persistence | Can't answer "what were my top artists this year?" — only live `recently_played` (50 tracks) |
| No temporal analytics | No play counts, listening timeline, weekday/time-of-day patterns |
| No album-level lookup | Can't answer "when was [album] released?" or "how many tracks?" |
| No Spotify `/recommendations` tool | Agent can't compare "Spotify's recommendation vs mine" |
| No direct artist profile query | Can't answer "how popular is X?" or "how many followers?" |

These are natural Phase 6+ additions.

## See Also
- [[Agent Memory Types]]
- [[RAG Evaluation]]
- [[LangGraph CRAG Pipeline]]
- [[Plan and Execute Pattern]]
- [[Observability — LangFuse vs LangSmith Decision]]
- [[Production Hardening Patterns]]
