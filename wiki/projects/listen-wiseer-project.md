---
title: Listen-Wiseer Project
tags: [langgraph, rag, memory, eval, project]
summary: Spotify recommendation agent with ENOA taste-map personalisation — LangGraph ReAct + Chainlit UI, LightGBM classifiers, DuckDB vss RAG, and three-tier eval harness.
updated: 2026-07-06
sources:
  - raw/claude-docs/listen-wiseer/memory/project_listen_wiseer.md
  - raw/claude-docs/listen-wiseer/docs/plans/phase4a_agent_chainlit.md
  - raw/claude-docs/listen-wiseer/docs/plans/phase4b_memory.md
  - raw/claude-docs/listen-wiseer/docs/plans/phase5a_rag.md
  - raw/claude-docs/listen-wiseer/docs/research/eval-harness.md
  - raw/claude-docs/listen-wiseer/docs/research/infra_support.md
  - raw/claude-docs/listen-wiseer/docs/research/peer-repos.md
  - raw/claude-docs/listen-wiseer/docs/plans/phase6_refactor.md
  - raw/claude-docs/listen-wiseer/docs/plans/phase7a-exploration-tools.md
  - raw/claude-docs/listen-wiseer/docs/plans/phase7b-intent-refactor-ux.md
  - raw/claude-docs/listen-wiseer/docs/plans/phase7c-memory-genre-polish.md
  - raw/claude-docs/listen-wiseer/docs/research/music-agent/exploration-architecture.md
  - raw/claude-docs/listen-wiseer/docs/research/music-agent/recommender-design.md
  - raw/claude-docs/listen-wiseer/docs/research/music-agent/peer-repos.md
  - raw/claude-docs/listen-wiseer/docs/research/music-agent/spotify-repos.md
  - raw/claude-docs/listen-wiseer/docs/research/evaluation/eval-harness.md
  - raw/claude-docs/listen-wiseer/docs/README.md
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

## Phase Status (as of 2026-07-05)

| Phase | Status |
|---|---|
| 1 — structlog, Pydantic v2, Polars loader, Spotify OAuth | ✓ Done |
| 2 — GMM + LightGBM; 4 pipelines; 8 MCP tools; 222 tests | ✓ Done |
| 3a–3d — ETL hardening, feature engineering, EDA | ✓ Done |
| 4a — LangGraph ReAct agent + Chainlit UI | ✓ Done |
| 4b — Episodic, semantic, procedural memory (MemorySaver) | ✓ Done |
| 5a — RAG core: DuckDB vss, MiniLM, Wikipedia/Tavily, 93 tests | ✓ Done |
| 5b — Intent routing: 6 nodes, 5 intents, clarification, 10 tools, 97 tests | ✓ Done |
| **6 — Stabilize + Postgres persistence + Tavily web search** | **✓ Done** |
| 7a — Exploration tools (6 new Spotify endpoints + agent tools) | Planned |
| 7b — Intent taxonomy refactor + Chainlit UX (quick-reply chips) | Planned |
| 7c — Genre lineage, taste analysis, cross-session memory | Planned |

## Phase 6 — What Changed

Phase 6 stabilized the stack and replaced RAG with Tavily for artist context:

- **Dead deps removed:** chromadb, arize-phoenix, openinference — also removed dead Compose services and dead config
- **Persistence:** MemorySaver → Postgres (via `db-init` Compose service, `POSTGRES_URL` env var)
- **Web search:** Tavily replaces Wikipedia RAG for artist context — `get_artist_context_tool` calls `TavilyClient`; RAG suspended but not deleted in `rag_core/`
- **System prompt updates:** aligned with Tavily-first retrieval strategy

## Phase 7 Roadmap

### 7a — Exploration Tools
Add 6 new Spotify fetch functions + corresponding agent tools:
- `fetch_top_tracks`, `fetch_top_artists`, `fetch_artist_info`, `fetch_artist_top_tracks`, `fetch_artist_albums`, `fetch_spotify_recommendations`
- 6 new StructuredTools wiring these into the agent
- Intent taxonomy updated with `explore_my_taste` and `discover` intents

### 7b — Intent Refactor + Chainlit UX
- `INTENT_PATTERNS` extended for `explore_my_taste` and `discover`
- Agent suggestions → Chainlit quick-reply chips (Actions + `cl.on_action`)
- Track list rendering (stretch)
- Golden dataset expanded with 5 new intent examples

### 7c — Genre Lineage, Taste Analysis, Cross-Session Memory
- `get_genre_context_tool` using structured Tavily genre queries
- `get_taste_analysis_tool` comparing short-term vs long-term artists
- Cross-session memory: `InMemoryStore` → env-switched Postgres/SQLite store via `get_store()`
- Memory persistence test

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

From research into six Spotify peer repos (three MCP/AI agents + three utility apps):

| Gap | Spotify API | Effort | Impact |
|---|---|---|---|
| **No Spotify Affinity API** | `/me/top/tracks`, `/me/top/artists` (3 time ranges: 4w/6m/all-time, up to 100 results) | Small | **High** — "who are my top artists this month?" |
| **No listening history persistence** | `/me/player/recently-played` (max 50; must poll hourly) + GDPR export for full history | Medium | High — enables temporal analytics |
| **No temporal analytics** | Derived from persisted history | — | High — play counts, listening timeline, weekday patterns |
| **No followed-artists + new-release tracking** | `/me/following`, `/artists/{id}/albums` | Medium | Medium — "what has [artist] released recently?" |
| **No Spotify `/recommendations` with tuneable params** | `/v1/recommendations?target_energy=...` | Small | Medium — "find tracks like this playlist but more acoustic" |
| **No album-level lookup** | `/v1/search?type=album` | Small | Medium — "when was [album] released?" |
| **No direct artist profile query** | `/v1/search?type=artist` | Small | Medium — popularity, followers, Spotify-assigned genres |
| **No currently-playing / playback control** | `/me/player/*` (needs extra OAuth scopes) | Small | Low — niche, async UI |
| **No saved/liked tracks sync** | `/me/tracks` (library) | Medium | Low — we have `faves` table already |

**Priority:** Spotify Affinity API (`/me/top/`) is the highest-ROI addition — available instantly (no export needed), three time windows, Spotify's own affinity calculation.

**Key insight from peer repos:** Since Spotify only returns the last 50 recently-played tracks, you MUST poll frequently (hourly) to build a listening history. The GDPR privacy export is the only way to get historical data older than ~50 plays.

**What we have that peers don't:**
- GMM + LightGBM ML recommender (no peer uses trained models)
- ENOA genre taxonomy (6k+ genre spatial map)
- Persistent taste memory (langmem across sessions)
- Full RAG pipeline (hybrid search, Wikipedia, reranking)
- Multi-node agent graph (intent classification, query rewriting, validation)

These are natural Phase 7+ additions.

## See Also
- [[Agent Memory Types]]
- [[RAG Evaluation]]
- [[LangGraph CRAG Pipeline]]
- [[Plan and Execute Pattern]]
- [[Observability — LangFuse vs LangSmith Decision]]
- [[Production Hardening Patterns]]
