# Plan: Phase 3a — Feature Engineering & Preprocessing

Date: 2026-04-04
Predecessor: Phase 2 (ETL + recommendation layer)
Next: Phase 3b (training pipeline)

---

## Context

Spotify deprecated the audio-features endpoint (403 for all apps, 2025). The ~2182 existing corpus tracks have full Spotify audio features from before deprecation. New tracks synced after the cutoff have NO audio features — only metadata (name, year, popularity), artist data, playlist membership, and Last.fm genres.

This plan builds a comprehensive feature engineering layer (`recommend/preprocessing.py`) that:
1. Computes proxy features from playlist co-occurrence, artist profiles, and genre structure
2. Imputes missing audio features via a cascade (artist → genre → global median)
3. Adds collaborative and temporal signals currently ignored by the ML pipeline
4. Transitions data loading from archived CSVs to DuckDB

---

## Architecture

**`etl/`** owns:
- DB schema (including new `track_embeddings` table)
- Raw data sync (Spotify, Last.fm, CSV archives)
- Storage of computed features (writing embeddings to DB)

**`recommend/preprocessing.py`** (new) owns:
- Feature computation logic (Track2Vec, artist-median, playlist-centroid propagation)
- Imputation strategies (artist → genre → global median cascade)
- Feature matrix assembly (combine audio + embeddings + collaborative signals → ML-ready arrays)
- Called by both `train.py` and `engine.py`

Key insight: **which features to compute and how to impute** are ML decisions, not ETL decisions. ETL stores what preprocessing asks it to.

---

## Current Feature Inventory

| Source | Features | Used in ML? |
|--------|----------|-------------|
| `tracks` | `year`, `decade`, `popularity`, `first_genre`, `genre_cat` | `popularity` yes, `decade` yes (one-hot) |
| `audio_features` | 9 audio floats, `tempo`, `duration_ms`, `key`, `mode`, `key_mode` | All 9 audio yes, `key_mode` yes (one-hot), `duration_ms` no |
| `genre_map`/`genre_xy` | `top`, `left`, `gen_4`/`gen_6`/`gen_8`, `my_genre`, `sub_genre` | `top` yes, `left` yes |
| `artists` | `artist_name`, `popularity`, `genres` | **Not used** |
| `faves` | `fave_score` | **Not used** |
| `playlist_tracks` | junction: track ↔ playlist | **Not used** |
| `track_artists` | junction: track ↔ artist | **Not used** |

---

## Feature Engineering — 7 New Signal Groups

### 1. Track2Vec (playlist co-occurrence embeddings)
- Treat each playlist as a "sentence", each track_id as a "word"
- gensim `Word2Vec(sentences, vector_size=64, window=5, min_count=1, sg=1, seed=42)`
- 64d embedding per track — captures human curation intent directly
- Stored in `track_embeddings` table (expensive to compute, reused)
- Exposed to classifier as scalar `embedding_similarity` (cosine between seed and candidate)

### 2. Imputation cascade (for tracks missing audio features)
- Level 1: **Artist-median** — same-artist corpus tracks with real features → their median
- Level 2: **Genre-median** — same-`first_genre` tracks → genre median
- Level 3: **Global-median** — corpus-wide median (last resort)
- Marks `features_source`: `'imputed_artist'`, `'imputed_genre'`, `'imputed_global'`

### 3. Collaborative features (from junction tables)
- `n_playlists` — how many user playlists contain this track
- `playlist_diversity` — how many distinct `gen_4` groups the track spans
- `fave_score` — from faves table (already in DB, free signal)

### 4. Temporal features
- `year_normalized` — `(year - min_year) / (max_year - min_year)`, 0–1 scale
- `years_since_release` — `current_year - year`, recency signal

### 5. Artist-genre ENOA centroid
- Artist has comma-separated `genres` in `artists` table
- Split → look up each in `genre_xy` → average `(top, left)` across matched genres
- Produces `artist_enoa_top`, `artist_enoa_left` — richer than single `first_genre`

### 6. Artist profile propagation
- Compute median audio features across all tracks by the same artist
- If a new track has no audio features but the artist has other corpus tracks → propagate
- More precise than genre-median because it's artist-specific

### 7. Playlist profile propagation
- For each track, compute centroid of all OTHER tracks in the same playlists
- Multi-playlist tracks get a weighted average across playlists
- Provides "neighborhood" feature vector even for tracks missing audio features

---

## Feature List Changes

    # similarity.py — 12 → 15 features
    SIMILARITY_FEATURES = [
        "danceability", "energy", "loudness", "speechiness",
        "acousticness", "instrumentalness", "liveness", "valence",
        "tempo", "popularity", "top", "left",
        # New
        "fave_score", "n_playlists", "year_normalized",
    ]

    # clustering.py — 11 → 15 audio features (+ one-hots stay same)
    CLUSTER_AUDIO_FEATURES = [
        "danceability", "energy", "loudness", "speechiness",
        "acousticness", "instrumentalness", "liveness", "valence",
        "tempo", "top", "left",
        # New
        "fave_score", "n_playlists", "year_normalized", "duration_ms_normalized",
    ]

    # classifiers.py — 16 → 18 features
    CLASSIFIER_FEATURES = SIMILARITY_FEATURES + [
        "similarity_score", "cluster_prob",
        "camelot_distance", "tempo_deviation",
        # New
        "embedding_similarity", "playlist_diversity",
    ]

All existing pkl models become incompatible (dimensionality changes). Phase 3b retrains everything.

---

## Out of Scope

- **Last.fm genre fill (0j-c)** — blocked on Last.fm key activation. Code ready in `sync_lastfm_genres`.
- **FAISS / ANN** — 200ms corpus scan acceptable. Optimisation deferred.
- **Track2Vec for new tracks not in any playlist** — they get zero embeddings; imputation cascade handles features.
- **Retraining models** — that's Phase 3b.

---

## Pre-requisites

- Step 0a–0i: DONE (DB bootstrapped, 2182 tracks, sync hardened, cron set up)
- 222 tests passing, 3 skipped

---

## Steps

### Step 0j-a: DB schema — `track_embeddings` table

**Files modified**: `src/etl/db.py`

Add to `_DDL`:

    CREATE TABLE IF NOT EXISTS track_embeddings (
        track_id       VARCHAR PRIMARY KEY,
        embedding      DOUBLE[64],
        model_version  VARCHAR DEFAULT 'track2vec_v1'
    );

**Done when**: `init_schema()` creates the table; existing tables unaffected.

---

### Step 0j-b: `recommend/preprocessing.py` scaffold

**Files created**: `src/recommend/preprocessing.py`

Public API:

    def load_corpus_from_db(conn) -> pl.DataFrame
    def compute_track2vec(conn, dim=64, window=5, min_count=1, seed=42) -> dict[str, np.ndarray]
    def store_track2vec(conn, embeddings: dict[str, np.ndarray]) -> int
    def compute_artist_medians(corpus) -> pl.DataFrame
    def compute_genre_medians(corpus) -> pl.DataFrame
    def impute_missing_features(corpus, artist_medians, genre_medians) -> pl.DataFrame
    def add_collaborative_features(corpus, conn) -> pl.DataFrame
    def add_temporal_features(corpus) -> pl.DataFrame
    def compute_artist_enoa_centroid(conn) -> pl.DataFrame
    def propagate_playlist_profiles(corpus, conn) -> pl.DataFrame
    def build_feature_matrix(conn) -> pl.DataFrame  # orchestrator

**Done when**: Module imports cleanly; functions have signatures + docstrings + placeholder bodies.

---

### Step 0j-c: Track2Vec implementation

**Files modified**: `src/recommend/preprocessing.py`, `pyproject.toml`

- `uv add gensim`
- `compute_track2vec()`: query `playlist_tracks` → build sequences → `Word2Vec` → return dict
- `store_track2vec()`: write embeddings to `track_embeddings` table
- Parameters: `vector_size=64`, `window=5`, `min_count=1`, `sg=1`, `seed=42`

**Done when**: Running against DB produces embeddings for all tracks in at least one playlist.

---

### Step 0j-d: Imputation cascade

**Files modified**: `src/recommend/preprocessing.py`

- `compute_artist_medians()`: group by artist_id via `track_artists` join, median audio features
- `compute_genre_medians()`: group by `first_genre`, median of same features
- `impute_missing_features()`: cascade artist → genre → global; mark `features_source`

**Done when**: No NULL audio features remain in output corpus.

---

### Step 0j-e: Collaborative features

**Files modified**: `src/recommend/preprocessing.py`

- `n_playlists`: COUNT from `playlist_tracks` per track
- `playlist_diversity`: COUNT(DISTINCT gen_4) via playlist_tracks → playlists join
- `fave_score`: from `faves` table, default 0.0

**Done when**: Three columns present; tracks not in any playlist get zeros.

---

### Step 0j-f: Temporal features

**Files modified**: `src/recommend/preprocessing.py`

- `year_normalized`: (year - min) / (max - min), NULLs → 0.5
- `years_since_release`: current_year - year, NULLs → median
- `duration_ms_normalized`: (duration_ms - min) / (max - min), NULLs → 0.5

**Done when**: Three columns present; no NULLs.

---

### Step 0j-g: Artist-genre ENOA centroid

**Files modified**: `src/recommend/preprocessing.py`

- Query `artists.genres` + `genre_xy` → average (top, left) per artist
- Join to corpus via `track_artists`
- Adds `artist_enoa_top`, `artist_enoa_left`

**Done when**: Columns present (NULL for artists with no matched genres — handled by imputation).

---

### Step 0j-h: Playlist profile propagation

**Files modified**: `src/recommend/preprocessing.py`

- For each track: centroid of OTHER tracks in same playlists (excluding self)
- Weighted average across multiple playlists
- Used as imputation source in the cascade

**Done when**: Tracks in playlists have propagated profile features.

---

### Step 0j-i: Update feature lists in ML modules

**Files modified**:
- `src/recommend/modules/similarity.py` — extend `SIMILARITY_FEATURES`
- `src/recommend/modules/clustering.py` — extend `CLUSTER_AUDIO_FEATURES`
- `src/recommend/modules/classifiers.py` — extend `CLASSIFIER_FEATURES`

**Done when**: Feature lists updated; imports work; existing tests adapted.

---

### Step 0j-j: `build_feature_matrix()` orchestrator

**Files modified**: `src/recommend/preprocessing.py`

Calls all the above in order:
1. `load_corpus_from_db(conn)`
2. `add_collaborative_features()`
3. `add_temporal_features()`
4. `compute_artist_enoa_centroid()` + join
5. `impute_missing_features()` (cascade)
6. `propagate_playlist_profiles()`
7. Final column selection + NULL checks

**Done when**: Returns DataFrame with all expected columns and zero NULLs in feature columns.

---

### Step 0j-k: Tests

**Files created**: `tests/unit/test_preprocessing.py`

All with synthetic fixtures (in-memory DuckDB):
- `test_load_corpus_from_db`
- `test_compute_track2vec`
- `test_impute_cascade_artist_first`
- `test_impute_cascade_genre_fallback`
- `test_impute_cascade_global_fallback`
- `test_collaborative_features`
- `test_temporal_features`
- `test_artist_enoa_centroid`
- `test_build_feature_matrix`

**Done when**: All pass; `uv run pytest tests/unit/test_preprocessing.py -v`

---

### Step 0j-l: Validation

    PYTHONPATH=src uv run python -c "
    from etl.db import get_connection
    from recommend.preprocessing import build_feature_matrix
    conn = get_connection(read_only=True)
    df = build_feature_matrix(conn)
    print(f'Rows: {len(df)}, Cols: {len(df.columns)}')
    print(f'Null counts: {df.null_count()}')
    conn.close()
    "

Expected: ~2182 rows, 0 NULLs in feature columns, majority `features_source='spotify'`.

---

## Step 0 Summary (completed 2026-04-03 / 2026-04-04)

Steps 0a–0i are DONE:
- **0a**: Bootstrap from archives → 2182 tracks in DB
- **0b**: `last_synced` column on playlists
- **0c**: 100ms inter-batch delay
- **0d**: `plan_sync` respects 23h cooldown
- **0e**: `upsert_playlists` writes `last_synced`
- **0f**: Audio-features 403 confirmed as Spotify deprecation (not scope issue)
- **0g**: Per-step sync with CLI limits
- **0h**: Validated each sync step
- **0i**: macOS launchd cron registered
- 222 tests passing, 3 skipped
