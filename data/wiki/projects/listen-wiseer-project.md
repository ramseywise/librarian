---
title: Listen-Wiseer Project
tags: [langgraph, rag, memory, eval, project]
summary: Personal music copilot with ENOA taste-map personalisation — LangGraph agent behind a React web player (FastAPI SSE over Navidrome; Chainlit retired 2026-10-30), GMM/LightGBM reranking, agentic web search and a three-tier eval harness; Spotify-free since Phase 9 (2026), running on MusicBrainz, ListenBrainz, Last.fm and Deezer.
updated: 2026-10-30
sources:
  - data/raw/playground-docs/2026-07-13-puffin-agentic-protocols-general-vs-specific.md
  - data/raw/playground-docs/2026-07-13-puffin-listen-wiseer-knowledge-plan.md
  - data/raw/claude-docs/listen-wiseer/memory/project_listen_wiseer.md
  - data/raw/claude-docs/listen-wiseer/docs/plans/phase4a_agent_chainlit.md
  - data/raw/claude-docs/listen-wiseer/docs/plans/phase4b_memory.md
  - data/raw/claude-docs/listen-wiseer/docs/plans/phase5a_rag.md
  - data/raw/claude-docs/listen-wiseer/docs/research/eval-harness.md
  - data/raw/claude-docs/listen-wiseer/docs/research/infra_support.md
  - data/raw/claude-docs/listen-wiseer/docs/research/peer-repos.md
  - data/raw/claude-docs/listen-wiseer/docs/plans/phase6_refactor.md
  - data/raw/claude-docs/listen-wiseer/docs/CHANGELOG.md
  - data/raw/claude-docs/listen-wiseer/docs/ttd.md
  - data/raw/claude-docs/listen-wiseer/docs/plans/phase7a-exploration-tools.md
  - data/raw/claude-docs/listen-wiseer/docs/plans/phase7b-intent-refactor-ux.md
  - data/raw/claude-docs/listen-wiseer/docs/plans/phase7c-memory-genre-polish.md
  - data/raw/claude-docs/listen-wiseer/docs/research/music-agent/exploration-architecture.md
  - data/raw/claude-docs/listen-wiseer/docs/research/music-agent/recommender-design.md
  - data/raw/claude-docs/listen-wiseer/docs/research/music-agent/peer-repos.md
  - data/raw/claude-docs/listen-wiseer/docs/research/music-agent/spotify-repos.md
  - data/raw/claude-docs/listen-wiseer/docs/research/evaluation/eval-harness.md
  - data/raw/claude-docs/listen-wiseer/docs/README.md
  - data/raw/sessions/claude-2026-07-07-this-github-listen-wiseer-has-gone-throu-0cd5da0c.md
  - data/raw/claude-docs/listen-wiseer/docs/plans/peer-repo-improvements.md
  - data/raw/claude-docs/listen-wiseer/docs/plans/phase1_flask_origin.md
  - data/raw/claude-docs/listen-wiseer/docs/plans/phase2a_infra_refactor.md
  - data/raw/claude-docs/listen-wiseer/docs/plans/phase2b_recommendation_layer.md
  - data/raw/claude-docs/listen-wiseer/docs/plans/phase2c_etl_lastfm.md
  - data/raw/claude-docs/listen-wiseer/docs/plans/phase2d_etl_sync_hardening.md
  - data/raw/claude-docs/listen-wiseer/docs/plans/phase2e_genre_tables.md
  - data/raw/claude-docs/listen-wiseer/docs/plans/phase3a_preprocessing.md
  - data/raw/claude-docs/listen-wiseer/docs/plans/phase3b_train.md
  - data/raw/claude-docs/listen-wiseer/docs/plans/phase3c_add_catboost.md
  - data/raw/claude-docs/listen-wiseer/docs/plans/phase3d_eda.md
  - data/raw/claude-docs/listen-wiseer/docs/plans/phase5b_intent.md
  - data/raw/claude-docs/listen-wiseer/docs/plans/phase5c_eval.md
  - data/raw/claude-docs/listen-wiseer/docs/plans/phase6_dashboard.md
  - data/raw/claude-docs/listen-wiseer/docs/research/music-agent/recommender-design-v1.md
  - data/raw/claude-docs/listen-wiseer/docs/research/spotify-folder-repos.md
  - data/raw/claude-docs/listen-wiseer/memory/MEMORY.md
  - data/raw/claude-docs/listen-wiseer/memory/user_profile.md
  - data/raw/claude-docs/listen-wiseer/docs/plans/LIS-77-plan.md
  - data/raw/claude-docs/listen-wiseer/docs/plans/phase8-rag-rightsize-agentic-search.md
  - data/raw/claude-docs/listen-wiseer/docs/reviews/phase8-rag-rightsize-agentic-search.md
  - data/raw/repos/listen-wiseer/.claude--docs--plans--LIS-77-plan.md
  - data/raw/repos/listen-wiseer/.claude--docs--plans--phase1_flask_origin.md
  - data/raw/repos/listen-wiseer/.claude--docs--plans--phase2a_infra_refactor.md
  - data/raw/repos/listen-wiseer/.claude--docs--plans--phase2b_recommendation_layer.md
  - data/raw/repos/listen-wiseer/.claude--docs--plans--phase2c_etl_lastfm.md
  - data/raw/repos/listen-wiseer/.claude--docs--plans--phase2d_etl_sync_hardening.md
  - data/raw/repos/listen-wiseer/.claude--docs--plans--phase2e_genre_tables.md
  - data/raw/repos/listen-wiseer/.claude--docs--plans--phase3a_preprocessing.md
  - data/raw/repos/listen-wiseer/.claude--docs--plans--phase3b_train.md
  - data/raw/repos/listen-wiseer/.claude--docs--plans--phase3c_add_catboost.md
  - data/raw/repos/listen-wiseer/.claude--docs--plans--phase3d_eda.md
  - data/raw/repos/listen-wiseer/.claude--docs--plans--phase4a_agent_chainlit.md
  - data/raw/repos/listen-wiseer/.claude--docs--plans--phase4b_memory.md
  - data/raw/repos/listen-wiseer/.claude--docs--plans--phase5a_rag.md
  - data/raw/repos/listen-wiseer/.claude--docs--plans--phase5b_intent.md
  - data/raw/repos/listen-wiseer/.claude--docs--plans--phase5c_eval.md
  - data/raw/repos/listen-wiseer/.claude--docs--plans--phase6_dashboard.md
  - data/raw/repos/listen-wiseer/.claude--docs--plans--phase6_refactor.md
  - data/raw/repos/listen-wiseer/.claude--docs--plans--phase7a-exploration-tools.md
  - data/raw/repos/listen-wiseer/.claude--docs--plans--phase7b-intent-refactor-ux.md
  - data/raw/repos/listen-wiseer/.claude--docs--plans--phase7c-memory-genre-polish.md
  - data/raw/repos/listen-wiseer/.claude--docs--plans--phase8-rag-rightsize-agentic-search.md
  - data/raw/repos/listen-wiseer/.claude--docs--reviews--phase8-rag-rightsize-agentic-search.md
  - data/raw/repos/listen-wiseer/CLAUDE.md
  - data/raw/repos/listen-wiseer/README.md
---

# Listen-Wiseer Project

Personal music recommendation agent (originally Spotify-based; Spotify-free since Phase 9) personalised to the user's own ENOA taste map — not a generic Spotify wrapper. ENOA (top/left) coordinates encode a 2D emotional/sonic space derived from the user's playlist curation behaviour.

## Stack

| Layer | Technology |
|---|---|
| Orchestration | LangGraph (ReAct agent) |
| UI | React web player (`web/`, Vite) with an assistant side panel, served by FastAPI (`/api/chat` SSE, `/api/playable`) over Navidrome; Chainlit until 2026-10-30 |
| ML | LightGBM (32 per-playlist classifiers) + GMM (8 components) |
| RAG | DuckDB vss (`rag_chunks` table, `all-MiniLM-L6-v2`, 384-dim) |
| Vector cache | ChromaDB (`artist_info` collection, lazy ingestion) |
| Memory | LangGraph `InMemoryStore` + langmem (episodic/semantic/procedural) |
| Checkpointer | MemorySaver (dev) / AsyncRedisSaver (prod) — superseded: Postgres in Docker as of 2026-10 |
| Data | 595k-row corpus, 2182 tracks, 291 genre mappings |
| Tools | MCP server (8 tools) + StructuredTool wrappers (20 tools) |
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
| **7a — Exploration tools (6 new Spotify endpoints + agent tools)** | **✓ Done** |
| **7b — Intent taxonomy refactor + Chainlit UX (quick-reply chips)** | **✓ Done** |
| **7c — Genre lineage, taste analysis, cross-session memory** | **✓ Done** |

## Build Phase History (Pre-4a)

Finer-grained phase numbering from the project's own plan docs (these collapse into the "1" and "2" rows of the Phase Status table above, plus the 3a–3d preprocessing/training sub-phases):

| Phase | What shipped |
|---|---|
| **1 — Flask origin** | Original prototype: Flask OAuth + Spotify API client (pandas/requests), ENOA genre mapping, IsolationForest outlier detection, cosine/Euclidean similarity, Spectral clustering, sklearn classifier pipeline, Marshmallow schemas. Fully superseded by Phase 2a. |
| **2a — Infra refactor** | Replaced Flask with production structure: custom OAuth httpx client (`src/spotify/`), FastMCP server, Chainlit stub, `pydantic-settings` config, typed exception hierarchy, DuckDB/Polars ETL, Docker Compose (Jaeger + Postgres profiles). |
| **2b — Recommendation layer rebuild** | Full ML layer: GMM soft clustering + LightGBM `CalibratedClassifierCV` reranker per playlist, weighted cosine + Camelot harmonic distance + tempo compatibility + MMR diversification, ENOA spatial proximity filtering, 4 pipelines (Track/Artist/Playlist/Genre), 4 MCP tools, 139 unit tests. Removed legacy pandas-based `src/models/`. |
| **2c — ETL rebuild + Last.fm** | Last.fm enrichment (play count, listener count, tags) wired into `etl/sync.py`; 227-test suite; pre-commit hooks (ruff + pyright). |
| **2d — ETL bootstrap + sync hardening** | Bootstrapped DuckDB from CSV archives (~2870 tracks); 100ms inter-batch throttle on Spotify calls; 23h cooldown guard in `plan_sync` (`needs_sync` skips playlists synced within 23h); per-step sync CLI limits (`--playlists`, `--tracks`, `--audio`, `--artists`) to bound blast radius while testing; macOS `launchd` daily cron. Confirmed the `audio-features` 403 was Spotify's 2025 endpoint deprecation, not a missing OAuth scope. |
| **2e — Genre tables** | Normalized denormalized `track_profile` genre columns into `track_genre` (per-track, `genre_source`: manual/lookup/model), `artist_genre` and `playlist_genre` (aggregated via junction tables — mode for categorical, mean for `top`/`left`), and `external_tracks` (595,858-row training corpus from `spotify_train_data.csv`). `track_profile` converted from table to VIEW. `genre_infer` cron (model-driven inference for `genre_source='unknown'` rows) blocked on the Phase 3b classifier. |
| **3a — Feature engineering / preprocessing** | New `recommend/preprocessing.py` module (feature computation is an ML decision, ETL just stores what preprocessing asks for): [[Track2Vec Playlist Co-Occurrence Embeddings]] (64-dim), a 3-level imputation cascade for missing audio features (artist-median → genre-median → global-median, tagged via `features_source`), collaborative features (`n_playlists`, `playlist_diversity`, `fave_score`), temporal features (`year_normalized`, `years_since_release`), artist-genre ENOA centroid, and playlist-centroid propagation. Feature counts grew 12→15 (similarity), 11→15 (clustering), 16→18 (classifier). |
| **3b — Training pipeline** | Added `src/paths.py` path anchor (`REPO_ROOT`/`MODELS_DIR`/`DATA_DIR`) to remove hardcoded paths from `server.py`/`engine.py`; retrained GMM + scaler + per-playlist classifiers on the enriched feature matrix; end-to-end smoke test via `RecommendationEngine`. |
| **3c — CatBoost comparison** | See [[LightGBM vs CatBoost Comparison]] — fixed a train/inference feature-distribution mismatch (`cluster_prob`, `similarity_score` were zeroed at train time but real at inference) and added CatBoost as an alternate estimator with native categorical handling. |
| **3d — EDA notebook suite** | 8 notebooks in `notebooks/eda/`: smoke tests, corpus health (null audit, `features_source` breakdown, outlier detection), library exploration, feature engineering/importance (incl. Track2Vec t-SNE/UMAP), ENOA genre-space deep dive, retrieval diagnostics (GMM silhouette, cluster-genre alignment), LightGBM-vs-CatBoost model comparison, and end-to-end rerank-stage audit. |

## Phase 6 — What Changed

Phase 6 stabilized the stack and replaced RAG with Tavily for artist context:

- **Dead deps removed:** chromadb, arize-phoenix, openinference — also removed dead Compose services and dead config
- **Persistence:** MemorySaver → Postgres (via `db-init` Compose service, `POSTGRES_URL` env var)
- **Web search:** Tavily replaces Wikipedia RAG for artist context — `get_artist_context_tool` calls `TavilyClient`; RAG suspended but not deleted in `rag_core/`
- **System prompt updates:** aligned with Tavily-first retrieval strategy

**Phase 6 also planned (but deferred) a Streamlit data dashboard** (`src/app/dashboard.py`) — a standalone entry point separate from the Chainlit agent UI, for corpus overview (feature-distribution histograms), a GMM cluster browser (ENOA scatter coloured by cluster), a playlist inspector (per-playlist LightGBM scores + F1/ROC-AUC), and a recommendation explorer (direct `RecommendationEngine` queries bypassing the agent). The actual Phase 6 that shipped was the stabilize + Postgres + Tavily work above; the dashboard plan was explicitly named as out-of-scope in the Phase 5c eval plan ("Dashboard / visualization — Phase 6b") and has not been built as of this ingest.

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

**7 intents (post-7b):** `artist_info`, `genre_info`, `recommendation`, `history`, `chit_chat`, `explore_my_taste`, `discover`

**Intent classification:** pure keyword matching; confidence = `min(1.0, matched_keywords / 3)`; default fallback `artist_info` at 0.3.

**Phase 5b implementation detail:** `rewrite_query` only calls the LLM (Haiku, shared `_llm` instance) when a coreference signal is detected in the padded query string (`" it "`, `" they "`, `"the artist"`, etc.) — single-turn queries and pronoun-free multi-turn queries skip the call entirely. `validate_tool_output` runs after `call_tools` with three checks (empty/error output, intent↔tool-used misalignment via `_TOOL_INTENT_MAP`, soft entity-coverage logging) and injects one corrective `SystemMessage` retry capped by `tool_validation_retries` (max 1, via `max_tool_validation_retries` setting) before passing through regardless. The 10th agent tool, `get_related_artists_tool` (wraps `GET /artists/{id}/related-artists`), was added in this phase specifically to give `validate_tool_output` something to route to for `recommendation`-intent queries phrased as "who sounds like X?".

## Key Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Tool wiring | StructuredTool wrapping (direct Python) | No process management; testable without live MCP server |
| Vector store (RAG) | DuckDB vss | Zero extra deps; same DB file; `array_cosine_similarity()` fast enough at <10k chunks |
| RAG ingestion | Lazy Wikipedia/Tavily on first query | Avoid pre-ingesting all artists; cached in `rag_chunks` |
| Artist info collection | Single `artist_info` ChromaDB collection + metadata filter | Simpler than per-artist collections |
| Memory store | `AsyncPostgresStore` (prod) / `InMemoryStore` (dev, via `MEMORY_STORE_URL`) | Cross-session taste/episodic memory persistence |
| Checkpointer | AsyncPostgresSaver (prod) / MemorySaver (dev) | Postgres via Docker Compose |
| LLM client | `langchain-anthropic` `ChatAnthropic` over raw SDK | LangFuse span visibility |
| Eval framework | LangFuse + RAGAS | LangFuse: free tier + RAGAS native integration. DeepEval was planned for `ToolCorrectnessMetric` but never imported, and was removed 2026-07-19 after its autoloaded pytest plugin broke collection |

**Eval harness module layout** (instantiates [[Anthropic Three-Tier Eval Taxonomy]] for this project): `evals/agent/intent_eval.py` (Tier 1 — deterministic, imports `QueryAnalyzer` directly, no DuckDB import chain), `evals/agent/trajectory_eval.py` (Tier 2), `evals/agent/graders.py` (Tier 3 — RAGAS, Haiku-backed), `evals/agent/cost_gate.py` (single `CONFIRM_EXPENSIVE_OPS` env-var source of truth — `evals/graders/answer_eval.py` was refactored to import from here instead of a hardcoded bool), and `evals/run_agent_eval.py --tier {1,2,3,all}` as the single CLI entry point wired to `make eval-unit`/`eval-trajectory`/`eval-e2e`. Golden dataset: `evals/datasets/golden_intent.jsonl`, 50 hand-crafted `AgentGoldenSample` rows (10 per intent × 5 intents, with adversarial/ambiguous samples spread across intents).

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
- **32 test failures** are all `duckdb.IOError` (missing LFS DB) — not regressions *(stale by Phase 8: a re-measured baseline on a fixed venv was 443 passed / 3 skipped / 0 failed)*
- `full tests/unit/` suite hangs on some later test files — use targeted runs
- **REDIS_URL** needed for cross-session memory persistence; `InMemoryStore` for dev
- **libomp load order**: LightGBM and torch (via `sentence-transformers`) vendor different `libomp.dylib` builds. If torch's loads first, LightGBM training segfaults with no traceback. `tests/conftest.py` imports `lightgbm` at module scope to pin the order; don't remove it. `KMP_DUPLICATE_LIB_OK` does not help ([[Native Library Load-Order Collision]])
- **deepeval removed (2026-07-19)**: never imported, but its autoloaded pytest plugin imported `langchain.schema` (gone in langchain 1.x) and broke collection. Don't re-add it without checking langchain 1.x support
- **Python pin**: `requires-python = ">=3.11"` has no upper bound, so `uv sync` on a 3.13+ default interpreter fails to build `gensim`. The committed `.python-version` (3.11) is load-bearing

## Gaps vs Peer Repos

From research into **nine** Spotify peer repos across two research passes: three MCP/AI-agent repos (`spotify-ai-analytics`, `spotify-langgraph-agent`, `WikiSpotify-MCP`) plus six utility-app repos (`spotify_etl`, `Rhythmify`, `Spotify-Discover-2.0`, `Spotify-NewReleases`, `spotify-release-gun`, `spotify_app`/PlaylistBuddy):

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

### Peer Repo Implementation Detail

A follow-up plan (`peer-repo-improvements.md`) turned the gap table into 8 concrete implementation steps batched into 4 groups by dependency: **Batch A** (quick wins — top tracks/artists by time range, artist profile + album lookup tools, no schema changes), **Batch B** (`track_history` DDL + hourly `sync_recently_played` cron — prerequisite for C), **Batch C** (followed-artist tracking + GDPR export ingest + listening-history analytics), **Batch D** (tuneable `/v1/recommendations` with a `FEATURE_PRESETS` dict mapping natural-language asks like "more acoustic" → `target_acousticness=0.8`). Peer schema reference from `spotify_etl`: a `track_history(played_at PK, id, name, artists, album, ...)` + `audio_features(id PK, ...)` two-table split with an FK — listen-wiseer's planned `track_history` table folds both into one row per play instead. GDPR ingest detail: filter `ms_played >= 30_000` (skip non-plays) and `spotify_track_uri IS NOT NULL` (skip podcasts), extract `track_id` from the `spotify:track:{id}` URI, insert-or-ignore on `played_at` PK for idempotent re-runs.

The earlier recommender-design research pass (`recommender-design-v1.md`) also flagged specific design rationale behind Phase 2b's choices: the 24-position Camelot wheel with circular distance is the standard DJ harmonic-mixing convention; tempo half/double-time detection matters because dance genres like zouk and house treat 60bpm and 120bpm as the same feel; MMR prevents a top-k list from being near-duplicate tracks. For artist-context RAG, it recommended a 3-tier fallback (Wikipedia primary → Last.fm API for niche/emerging artists whose Wikipedia pages are thin or absent → paid web search for recency) with 300–500 token chunks and 50-token overlap, and lazy (not pre-ingested) ChromaDB population via a single `artist_info` collection filtered by artist-ID metadata rather than one collection per artist.

**What we have that peers don't:**
- GMM + LightGBM ML recommender (no peer uses trained models)
- ENOA genre taxonomy (6k+ genre spatial map)
- Persistent taste memory (langmem across sessions)
- Full RAG pipeline (hybrid search, Wikipedia, reranking)
- Multi-node agent graph (intent classification, query rewriting, validation)

These are natural Phase 7+ additions.

## Refactor Plan (2026-07-07 Review)

A review session flagged that the project has been through many revisions and is still short of test-ready. Two open follow-ups from that review:

- **Bring RAG back, cleaned up.** The Tavily-only web search from Phase 6 was a stopgap. The plan is to base the reinstated RAG path on the (cleaner) playground RAG implementation rather than the original `rag_core/` — and strip any leftover references inherited from playground's Danish support-bot origins. Listen-Wiseer's retrieval domain is music-genre lookup only, not support content.
- **Agentic web search, not a single Tavily call.** Open question raised: how to move from a single `TavilyClient` lookup (current `get_artist_context_tool`) to a genuinely agentic web search — i.e. a loop that can reformulate queries, decide whether more search is needed, and synthesize across multiple calls, rather than one-shot retrieval. Not yet resolved; flagged for a dedicated research pass before the FastAPI refactor.

Both items are pre-implementation research/plan-stage decisions (not yet executed) as of this review.

## Phase 8 — RAG Right-Sizing + Agentic Web Search (2026-07-07, executed)

Both follow-ups above were closed in Phase 8. The original `rag_core/` was deleted outright
rather than cleaned up: genre lookup did not justify a vector store. The single Tavily call
became an agentic search node — query decomposition into sub-queries, parallel Tavily
fan-out, and a **confidence gate** (high / medium / low) on the merged results modelled on
[[CRAG Retry Logic]], with low confidence routed to a retry/reformulate branch. Eighteen
tests were added with the phase; the review pass still found a multi-turn defect the tests
could not see — `format_response` walked message history backwards collecting citations with
no turn boundary, leaking the previous turn's sources into the current answer
([[Turn-Bounded Citation Walk]]). Fixed by stopping at the most recent `HumanMessage`, with
six regression tests. A test-driven checklist (`ttd.md`) tracks remaining coverage.

Detail from the Phase 8 plan and review: the gate shipped with three provenance tiers
(direct answer / raw results / nothing) rather than four, and only `low` produces the honest
non-answer; the tier rides in a `content_and_artifact` tool artifact that the validation node
reads to gate corrective retries ([[Provenance-Tiered Confidence Gate]]). The delete-vs-archive
reasoning, the eval-tree lineage leak, and the stabilize-pass findings (unbounded
`requires-python`, an eval plugin's telemetry hang, a stale "32 failures" baseline that was
really 0) are in [[Delete an Unfinished RAG Retrofit, Don't Archive It]]. The review used eight
parallel finder angles; its five non-blocking notes were deliberate coupling (validation node
duck-typing one tool pair's artifact shape), per-call client construction, a thread pool spun
up for single queries, two duplicate URL-dedup helpers, and a call site passing an empty
`entities` dict that silently disables one complexity signal.

## Phase 9 — Free Music Stack (S0–S7, done by 2026-10)

The project left Spotify entirely: Premium was cancelled and the developer API closed to
personal apps. Spotify was removed in stage S5. What replaced it:

- **Identity spine:** MusicBrainz MBIDs. `track_xref` maps each track to its MBID and to
  Spotify, Deezer, ISRC and YouTube ids.
- **Similarity candidates:** ListenBrainz, Last.fm and Deezer. LightGBM still decides which
  candidates fit the taste profile. Audio Features had been restricted earlier, so the
  model already ran on derived proxies.
- **Playback:** a YouTube link plus an inline Deezer link and 30 s preview. Nothing is
  downloaded from either, because their terms forbid it. `playable_cache` caches YouTube
  lookups.
- **Legal downloads (S6):** downloadable catalogues (Jamendo, Internet Archive) go into a
  local `library` table and are served to Subsonic apps by navidrome.
- **Local playlists:** stored by artist, title and MBID, exportable as JSPF.
- **History:** the old Spotify tables (`tracks`, `playlists`, `audio_features`) are a
  frozen archive keyed by legacy ids. Listening history comes from the Spotify privacy
  export (`make import-history`), then `make resolve-ids` maps plays to MusicBrainz and
  Deezer ids, resumably.
- **S7** added evals. The S3b reranker work was carried into audit item F.

## Repo Audit (2026-10-30)

| Item | Scope | Status |
|---|---|---|
| A | Fresh-clone path plus `make doctor` | done |
| B | Docs | done |
| C | Dependency diet plus a pyright gate | done |
| D | Coverage to 83% | done |
| E | Docker and MCP over HTTP | done |
| F | Data-gated work | partial; needs a Spotify export |

Resulting conventions:

- **The committed database is the bootstrap.** A fresh clone runs `git lfs pull` to get
  the ~11 MB DuckDB file, then `uv sync`, `make train` (reads DuckDB, no CSVs),
  `make doctor`, `make app`.
- **`make init-db` only migrates the schema.** It imports CSVs only if an optional,
  gitignored archive directory exists.
- **`make doctor` checks readiness.** It reports keys set or unset (never their values),
  DuckDB row counts and models present. `--strict` exits 1 on any warning, and
  `make app` runs it first without blocking.
- **Docker** runs postgres, db-init, mcp, app and navidrome (the app became the `api` service on 2026-10-30, see below) as non-root, multi-stage
  images. The checkpointer is Postgres in Docker and MemorySaver in dev.
- **MCP** is stdio by default, with server logs on stderr so stdout stays JSON-RPC.
  `streamable-http` serves on `:8765`.
- **CI** runs ruff, `pyright src` and unit tests with an 80% coverage floor. The eval CI
  gate fails a PR if any Tier 1 metric drops more than 5% from the committed baseline
  (golden intent set: 61 samples).
- **Gotchas recorded:**
  - Last.fm error 10 means the key is pending manual activation, not wrong.
  - `[tool.uv.sources]` index pins only reach direct dependencies; see
    [[Index Pin Applies Only to Direct Dependencies]].
  - A committed `.python-version` (3.11) stops `uv` picking a newer interpreter where
    `gensim` fails to build.

## Web Player Replaces Chainlit (2026-10-30)

The Chainlit chat UI is gone. The app is now a React web player (`web/`, Vite) with the
assistant in a side panel, backed by a FastAPI service in `src/api/` that proxies
Navidrome, streams chat over SSE (`/api/chat`) and resolves playback (`/api/playable`).

- **Local dev:** `make navidrome` (music server on `:4533`), `make seed-library` (a few
  CC-licensed tracks plus the first-run Navidrome admin), `make api` (FastAPI on
  `127.0.0.1:8000`; `API_PORT` moves it) and `make web` (Vite on `:5173`, proxying `/api`).
  `make dev` runs API and UI together; after `make web-build`, the API serves the built UI at `/`.
- **Docker:** the stack is postgres, db-init, navidrome, api (which builds `web/` with
  Node 22 and serves it) and mcp. `make infra-down` keeps volumes (Navidrome users and
  playlists, Postgres). `make infra-smoke` checks API health, that `/` returns
  `index.html`, that a Range request on a stream returns 206, and the MCP server.
- **DuckDB is single-writer across processes.** The player API is *the* writer (`plays`,
  `track_xref`, caches) and opens a connection per request. The MCP server opens the
  database read-only and skips cache writes; its one real write, `download_track`, opens
  read-write and returns a clear "database in use" message when the lock is held. New
  tools read via `db()` and write via `db(write=True)`, handling `duckdb.IOException`.
  This is the same one-writer discipline as [[Append-Only Log Writer Invariants]].

## LIS-77 — Runtime Bugs Behind a Green Suite (2026-07-30)

A repo-wide review sweep found two runtime bugs with ~470 passing tests: a function-local
import of a nonexistent `_llm` name inside the search synthesis helper (the only multi-hit
test patched the helper itself), and an unawaited `async get_store()` handed to the sync
fire-and-forget scheduler of the Phase 4b background prompt optimizer — meaning the optimizer
had been receiving a coroutine instead of a store. See [[Mocked-Away Body Hides the Defect]].

## Memory & Workflow Conventions

The project's own Claude memory (`memory/MEMORY.md`, `memory/user_profile.md`) instantiates the same conventions as [[Claude Workflow System]]: memory kept minimal (user profile + project decisions + genuinely non-obvious lessons only, no project-relative memory dir), all pipeline phases (research → plan → execute → review) run directly in the main conversation context rather than subagents, and formatting/test gates (ruff, pytest) are enforced via hooks rather than run manually. Dev stack recorded: `uv`, `ruff`, `pytest`, Pydantic v2, PyTorch/HuggingFace, Polars, numpy, scikit-learn, `langchain-anthropic` for LangFuse-traced LLM calls.

This project's `.claude/skills/` also defines a six-skill generic dev-workflow family (`code_debug`, `code_execute`, `code_pr`, `code_refactor`, `code_review`, `code_test`) — see the "Listen-Wiseer Generic Dev-Workflow Skill Family" section of [[Claude Workflow System]] for the compiled detail; these are project-local instantiations of the same `/code-debug`, `/execute-plan`, `/quick-pr`, `/code-review`, and (for `/consolidate`, previously a content-less stub) refactor skills already tracked there.

## Knowledge System Plan (2026-07-13, superseded in part)

A planning pass for a music-knowledge layer beyond Spotify similarity. Later phases took a
lighter path (DuckDB vss, then web search for artist context — see Phase 8 above), but the
reasoning is recorded:

- **APIs over scraping.** Spotify audio features, MusicBrainz (artist relationships,
  credits), Discogs (label and track credits), the Wikipedia API and Genius cover the core
  domains; scraping only for gaps.
- **Graph shape:** Artist/Song/Album/Label plus Key/Mode/RhythmPattern nodes; a **typed**
  `collaborated_with` edge (featured | produced | co-wrote | session), because the edge type
  changes its recommendation weight.
- **Hosted graph DB over embedded** for future multi-agent access: an embedded,
  single-process graph store is awkward once several agents need concurrent access.
- **Three pipelines, not one:** audio features → feature-vector similarity + rerank;
  collaboration graph → structured ingest into the graph DB; narrative text → multilingual
  embeddings into a vector store (artist material spans many languages).
- **Keep divergent signals side by side.** Listener-behaviour similarity and
  music-theory similarity will often disagree; store both with source and surface the
  disagreement rather than merging — the wiki's flag-not-overwrite rule. Multi-agent message
  types for this (song annotation, typed collaboration edges, recommendation rationale,
  graph-conflict flags) are in [[Provenance-Tracked Agent Beliefs]].

## See Also
- [[Index Pin Applies Only to Direct Dependencies]]
- [[Agent Memory Types]]
- [[RAG Evaluation]]
- [[LangGraph CRAG Pipeline]]
- [[Plan and Execute Pattern]]
- [[Observability — LangFuse vs LangSmith Decision]]
- [[Production Hardening Patterns]]
- [[Anthropic Three-Tier Eval Taxonomy]]
- [[Track2Vec Playlist Co-Occurrence Embeddings]]
- [[LightGBM vs CatBoost Comparison]]
- [[Claude Workflow System]]
- [[Turn-Bounded Citation Walk]] — instance-of (Phase 8 review finding)
- [[Kiez Project]] — related (sibling personal project)
- [[Provenance-Tiered Confidence Gate]] — instance-of (Phase 8 search confidence)
- [[Delete an Unfinished RAG Retrofit, Don't Archive It]] — instance-of (Phase 8 decision)
- [[Mocked-Away Body Hides the Defect]] — instance-of (LIS-77)
- [[Provenance-Tracked Agent Beliefs]] — related (multi-agent protocol sketched for the knowledge layer)
- [[Native Library Load-Order Collision]] — instance-of (libomp collision and deepeval plugin trap)
