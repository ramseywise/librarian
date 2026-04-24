# Plan: Phase 2b — Recommendation Layer (Phase 2 rebuild)
Status: COMPLETE (see CHANGELOG.md [0.3.0])

## Goal
Full ML recommendation layer: GMM clustering, LightGBM reranker, 4 pipelines, MCP tools, 139 unit tests.

## What was built
- `src/recommend/schemas.py` — `RecommendRequest`, `RecommendResult` (Pydantic v2)
- `src/recommend/modules/similarity.py` — weighted cosine, Camelot harmonic distance, tempo compatibility, MMR
- `src/recommend/modules/clustering.py` — GMM soft clustering, `filter_corpus_by_cluster`
- `src/recommend/modules/classifiers.py` — LightGBM + `CalibratedClassifierCV` reranker, per-playlist pkl I/O
- `src/recommend/modules/genre.py` — ENOA spatial proximity, genre zone filtering
- `src/recommend/train.py` — fits GMM + scaler + per-playlist classifiers → `models/*.pkl`
- `src/recommend/pipelines.py` — `TrackPipeline`, `ArtistPipeline`, `PlaylistPipeline`, `GenrePipeline`
- `src/recommend/engine.py` — `RecommendationEngine` singleton, lazy classifier cache
- `src/mcp_server/server.py` — 4 MCP tools: `recommend_similar_tracks`, `recommend_for_artist`, `recommend_for_playlist`, `recommend_by_genre`
- 139 unit tests across `tests/unit/recommend/`

## Removed
- Legacy `src/models/clustering.py`, `classifiers.py`, `cosine.py` (pandas, hardcoded paths)
