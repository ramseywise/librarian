---
name: listen-wiseer architecture and phase status
description: listen-wiseer project — phase status, key design decisions, corpus facts, open gotchas
type: project
---

Spotify music recommendation agent. LangGraph + Chainlit + FastMCP + LightGBM + ChromaDB.

**Why:** Personal music assistant personalised to the user's own ENOA taste map — not a generic Spotify wrapper.

## Phase status (as of 2026-04-06)

| Phase | Status |
|-------|--------|
| 1 — structlog, Pydantic v2, Polars loader | ✓ DONE |
| 1.5 — Spotify OAuth (httpx), exception hierarchy | ✓ DONE |
| 2 — GMM + LightGBM; 4 pipelines; 8 MCP tools; 222 tests | ✓ DONE |
| 3a–3d — ETL hardening, feature engineering, EDA notebooks | ✓ DONE |
| 4a — LangGraph agent + Chainlit | ✓ DONE |
| 4b — episodic, taste, procedural memory (MemorySaver) | ✓ DONE |
| 5a — RAG core: DuckDB vector store, MiniLM, Wikipedia/Tavily, 93 tests | ✓ DONE |
| 5b — Intent routing: 6 steps, 5 intents, clarification node, 10 tools, 97 tests | ✓ DONE |
| 5c — Eval harness (LangFuse tracing, golden dataset, intent/tool metrics) | **UP NEXT** |
| 6a — Playwright UI smoke tests, visual regression | PLANNED |
| 6b — Observability dashboard | PLANNED |

## Graph topology (post-5b)

```
START → trim_history → classify_intent → [route_after_classify]
    → low confidence  → clarify_or_proceed → END (wait for user)
    → high confidence → rewrite_query (coreference-gated Haiku) → agent → [route]
        → call_tools → validate_tool_output → agent (loop)
        → END
```

## Key architectural decisions

- 595k-row corpus. Brute-force cosine ~200ms — acceptable; FAISS deferred.
- ENOA (top/left) coordinates are the differentiator: encode user's own curation patterns, not just audio similarity.
- StructuredTool wrapping (direct Python calls) over langchain-mcp-adapters — simpler, no process management.
- Single `"artist_info"` ChromaDB collection with artist metadata filter (not per-artist collections).
- Lazy ChromaDB ingestion: fetch Wikipedia/Tavily on first query, upsert, cache.
- `MemorySaver` for in-session multi-turn only — cross-session persistence deferred.
- LLM: single `_llm` (Haiku) reused for both agent and rewrite — no separate `_haiku` instance.
- `langchain-anthropic` (`ChatAnthropic`) used over raw SDK for LangFuse span visibility.

## Active gotchas

- **Git LFS blocker**: `listen_wiseer.db` via LFS — other env can't pull. Decision deferred.
- `models/` and `data/cache/` gitignored — regenerate after pull (`make train`)
- `RecommendationEngine` raises `FileNotFoundError` if pkls missing — wrap in try/except
- `audio-features` Spotify endpoint dead (403, deprecated 2025)
- Last.fm key may still be pending activation (error 10 = pending manual review, not wrong key)
- 32 test failures are all `duckdb.IOError` (missing LFS DB) — not regressions
- Full `tests/unit/` suite hangs on some later test files — use targeted runs
- **REDIS_URL** needed for cross-session memory persistence; `InMemoryStore` for dev

## ETL / data facts

- `data/listen_wiseer.db`: 2182 tracks, 291 genre mappings, 2182 enriched profiles
- `artists` table has `artist_name` column — populated from playlist CSVs; 1456 names
- `audio_features.features_source` — `'spotify'` for all 2182 bootstrap rows
- `genre_xy` table: 6291 ENOA genres with top/left/color
- Cron: `~/Library/LaunchAgents/com.wiseer.listen-wiseer-sync.plist` registered, daily 02:00

## How to apply

Next session: start Phase 5c eval harness. See `.claude/docs/SESSION.md` for next session prompt.
