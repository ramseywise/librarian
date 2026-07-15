---
title: Listen-Wiseer Project
tags: [langgraph, rag, memory, eval, project]
summary: Spotify recommendation agent with ENOA taste-map personalisation — LangGraph ReAct + Chainlit UI, LightGBM classifiers, DuckDB vss RAG, and three-tier eval harness.
updated: 2026-07-14
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
  - raw/sessions/claude-2026-07-07-this-github-listen-wiseer-has-gone-throu-0cd5da0c.md
  - raw/claude-docs/listen-wiseer/docs/plans/peer-repo-improvements.md
  - raw/claude-docs/listen-wiseer/docs/plans/phase1_flask_origin.md
  - raw/claude-docs/listen-wiseer/docs/plans/phase2a_infra_refactor.md
  - raw/claude-docs/listen-wiseer/docs/plans/phase2b_recommendation_layer.md
  - raw/claude-docs/listen-wiseer/docs/plans/phase2c_etl_lastfm.md
  - raw/claude-docs/listen-wiseer/docs/plans/phase2d_etl_sync_hardening.md
  - raw/claude-docs/listen-wiseer/docs/plans/phase2e_genre_tables.md
  - raw/claude-docs/listen-wiseer/docs/plans/phase3a_preprocessing.md
  - raw/claude-docs/listen-wiseer/docs/plans/phase3b_train.md
  - raw/claude-docs/listen-wiseer/docs/plans/phase3c_add_catboost.md
  - raw/claude-docs/listen-wiseer/docs/plans/phase3d_eda.md
  - raw/claude-docs/listen-wiseer/docs/plans/phase5b_intent.md
  - raw/claude-docs/listen-wiseer/docs/plans/phase5c_eval.md
  - raw/claude-docs/listen-wiseer/docs/plans/phase6_dashboard.md
  - raw/claude-docs/listen-wiseer/docs/research/music-agent/recommender-design-v1.md
  - raw/claude-docs/listen-wiseer/docs/research/spotify-folder-repos.md
  - raw/claude-docs/listen-wiseer/memory/MEMORY.md
  - raw/claude-docs/listen-wiseer/memory/user_profile.md
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

**5 intents:** `artist_info`, `genre_info`, `recommendation`, `history`, `chit_chat`

**Intent classification:** pure keyword matching; confidence = `min(1.0, matched_keywords / 3)`; default fallback `artist_info` at 0.3.

**Phase 5b implementation detail:** `rewrite_query` only calls the LLM (Haiku, shared `_llm` instance) when a coreference signal is detected in the padded query string (`" it "`, `" they "`, `"the artist"`, etc.) — single-turn queries and pronoun-free multi-turn queries skip the call entirely. `validate_tool_output` runs after `call_tools` with three checks (empty/error output, intent↔tool-used misalignment via `_TOOL_INTENT_MAP`, soft entity-coverage logging) and injects one corrective `SystemMessage` retry capped by `tool_validation_retries` (max 1, via `max_tool_validation_retries` setting) before passing through regardless. The 10th agent tool, `get_related_artists_tool` (wraps `GET /artists/{id}/related-artists`), was added in this phase specifically to give `validate_tool_output` something to route to for `recommendation`-intent queries phrased as "who sounds like X?".

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

**Eval harness module layout** (instantiates [[Anthropic Three-Tier Eval Taxonomy]] for this project): `evals/agent/intent_eval.py` (Tier 1 — deterministic, imports `QueryAnalyzer` directly, no DuckDB import chain), `evals/agent/trajectory_eval.py` (Tier 2), `evals/agent/graders.py` (Tier 3 — RAGAS + DeepEval, Haiku-backed), `evals/agent/cost_gate.py` (single `CONFIRM_EXPENSIVE_OPS` env-var source of truth — `evals/graders/answer_eval.py` was refactored to import from here instead of a hardcoded bool), and `evals/run_agent_eval.py --tier {1,2,3,all}` as the single CLI entry point wired to `make eval-unit`/`eval-trajectory`/`eval-e2e`. Golden dataset: `evals/datasets/golden_intent.jsonl`, 50 hand-crafted `AgentGoldenSample` rows (10 per intent × 5 intents, with adversarial/ambiguous samples spread across intents).

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

## Memory & Workflow Conventions

The project's own Claude memory (`memory/MEMORY.md`, `memory/user_profile.md`) instantiates the same conventions as [[Claude Workflow System]]: memory kept minimal (user profile + project decisions + genuinely non-obvious lessons only, no project-relative memory dir), all pipeline phases (research → plan → execute → review) run directly in the main conversation context rather than subagents, and formatting/test gates (ruff, pytest) are enforced via hooks rather than run manually. Dev stack recorded: `uv`, `ruff`, `pytest`, Pydantic v2, PyTorch/HuggingFace, Polars, numpy, scikit-learn, `langchain-anthropic` for LangFuse-traced LLM calls.

This project's `.claude/skills/` also defines a six-skill generic dev-workflow family (`code_debug`, `code_execute`, `code_pr`, `code_refactor`, `code_review`, `code_test`) — see the "Listen-Wiseer Generic Dev-Workflow Skill Family" section of [[Claude Workflow System]] for the compiled detail; these are project-local instantiations of the same `/code-debug`, `/execute-plan`, `/quick-pr`, `/code-review`, and (for `/consolidate`, previously a content-less stub) refactor skills already tracked there.

## See Also
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
