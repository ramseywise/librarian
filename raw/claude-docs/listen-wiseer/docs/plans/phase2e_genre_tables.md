# Phase 2e — Genre Tables (track_genre, artist_genre, playlist_genre, external_tracks)

## Goal

Normalize genre data out of `track_profile` into dedicated, updatable tables that support:
- New track ingestion with model-inferred genre assignments
- Artist and playlist genre profiles derived from track-level data
- External training corpus for classifier training

## Current state

- `track_profile` — denormalized view with genre columns baked in (1780/2182 tracks have gen_4; 1775 have top/left)
- `genre_map` — 291 rows: `first_genre → gen_4/6/8/my_genre/sub_genre/top/left/color`
- `genre_xy` — 6291 rows: `first_genre → top/left/color` (full ENOA map)
- `playlists` — genre columns (`gen_4`, `gen_6`, `gen_8`, `top_genres`, `other_genres`) baked into the table
- `artists.genres` — raw Spotify genre string list, not mapped to taxonomy

## Coverage gaps (as of 2026-04-04)

- 173 tracks have `first_genre` but no `gen_4` (not in `genre_map`)
- 178 tracks have `first_genre` but no `top/left` (not in `genre_xy`)
- 229 tracks have no `first_genre` at all

## Tables to create

### 1. `track_genre`

Source of truth for per-track genre assignment. Updatable when new tracks arrive or model re-runs.

```sql
CREATE TABLE track_genre (
    track_id       VARCHAR PRIMARY KEY,
    first_genre    VARCHAR,
    gen_4          VARCHAR,
    gen_6          VARCHAR,
    gen_8          VARCHAR,
    my_genre       VARCHAR,
    sub_genre      VARCHAR,
    top            DOUBLE,
    left           DOUBLE,
    color          VARCHAR,
    genre_source   VARCHAR  -- 'manual' | 'model' | 'lookup'
);
```

Population logic (in order of priority):
1. Join `track_profile` → `genre_map` on `first_genre` for taxonomy columns
2. Join `track_profile` → `genre_xy` on `first_genre` for `top`/`left`/`color`
3. `genre_source = 'manual'` where gen_4 comes from genre_map; `'lookup'` where only genre_xy; `'model'` reserved for inference

### 2. `artist_genre`

Derived from `track_genre` via `track_artists`. Centroid of member tracks.

```sql
CREATE TABLE artist_genre (
    artist_id        VARCHAR PRIMARY KEY,
    gen_4            VARCHAR,   -- mode across tracks
    gen_6            VARCHAR,
    gen_8            VARCHAR,
    my_genre         VARCHAR,
    top              DOUBLE,    -- mean of track top values
    left             DOUBLE,    -- mean of track left values
    dominant_genres  VARCHAR,   -- JSON array of top first_genres by count
    track_count      INTEGER
);
```

Derivation: aggregate `track_genre` joined through `track_artists`, mode for categorical, mean for numeric.

### 3. `playlist_genre`

Derived from `track_genre` via `playlist_tracks`. Replaces genre columns in `playlists`.

```sql
CREATE TABLE playlist_genre (
    playlist_id     VARCHAR PRIMARY KEY,
    gen_4           VARCHAR,   -- mode
    gen_6           VARCHAR,
    gen_8           VARCHAR,
    top_genres      VARCHAR,   -- JSON array (top 5 by count)
    other_genres    VARCHAR,   -- JSON array (remaining)
    top             DOUBLE,    -- centroid
    left            DOUBLE,
    track_count     INTEGER
);
```

After population: drop `gen_4`, `gen_6`, `gen_8`, `top_genres`, `other_genres` from `playlists`.

### 4. `external_tracks`

595k-row Spotify training corpus from `data/archived/spotify_train_data.csv`.

```sql
CREATE TABLE external_tracks (
    track_id        VARCHAR PRIMARY KEY,
    track_name      VARCHAR,
    artist_names    VARCHAR,
    popularity      DOUBLE,
    release_date    VARCHAR,
    year            INTEGER,
    decade          VARCHAR,
    first_genre     VARCHAR,
    danceability    DOUBLE,
    energy          DOUBLE,
    loudness        DOUBLE,
    speechiness     DOUBLE,
    acousticness    DOUBLE,
    instrumentalness DOUBLE,
    liveness        DOUBLE,
    valence         DOUBLE,
    tempo           DOUBLE,
    duration_ms     BIGINT,
    time_signature  INTEGER,
    key             INTEGER,
    mode            INTEGER,
    key_labels      VARCHAR,
    mode_labels     VARCHAR,
    key_mode        VARCHAR,
    top             DOUBLE,
    left            DOUBLE,
    color           VARCHAR,
    y_target        VARCHAR
);
```

## Implementation steps

### Step 1 — Create and populate `track_genre`
- File: `src/etl/genre_tables.py`
- Read from `track_profile`, join `genre_map` and `genre_xy`
- Write to `track_genre` with `genre_source` flag
- Log coverage stats: n with full taxonomy, n lookup-only, n missing

### Step 2 — Create and populate `artist_genre`
- Aggregate `track_genre` via `track_artists`
- Mode for categorical fields, mean for top/left
- dominant_genres: top 5 `first_genre` values by count as JSON

### Step 3 — Create and populate `playlist_genre`
- Aggregate `track_genre` via `playlist_tracks`
- top_genres/other_genres: split at top 5 by count, serialize as JSON
- Drop genre cols from `playlists` after populating

### Step 4 — Load `external_tracks`
- Read `data/archived/spotify_train_data.csv` with Polars
- Deduplicate on `id` (track_id)
- Write to DuckDB `external_tracks`
- Log row count

### Step 5 — Regenerate `track_profile`
- `track_profile` is currently a table; convert to a VIEW over normalized tables
- Join: `tracks` + `audio_features` + `track_genre` + `faves`

### Step 6 — Wire genre profiles into sync cron
- Add `sync_genre_profiles(conn)` to end of `sync()` in `src/etl/sync.py`
- Calls `populate_track_genre`, `populate_artist_genre`, `populate_playlist_genre`
- Runs after `sync_lastfm_genres` so newly tagged tracks get profiles immediately
- **DONE** ✓

### Step 7 — Genre inference cron (post Phase 3b)
Depends on trained genre classifier (Phase 3b). Once model exists:
- Create `src/etl/genre_infer.py` — loads model, runs inference on `track_genre` rows
  where `genre_source = 'unknown'`, writes back `gen_4/6/8/my_genre/sub_genre` + sets
  `genre_source = 'model'`
- Add as a second launchd cron (weekly, after nightly sync) or a post-sync hook
- Input: `track_genre` WHERE `genre_source = 'unknown'` + audio features
- Output: updated `track_genre` rows + refreshed `artist_genre` / `playlist_genre`

## Status

| Step | Status |
|------|--------|
| 1. track_genre | ✓ Done (2182 rows: 1780 manual, 141 lookup, 261 unknown) |
| 2. artist_genre | ✓ Done (1456 rows) |
| 3. playlist_genre | ✓ Done (30 rows) |
| 4. external_tracks | ✓ Done (595,858 rows) |
| 5. track_profile VIEW | ✓ Done (COALESCE track_genre + genre_map fallback) |
| 6. sync_genre_profiles in cron | ✓ Done |
| 7. genre_infer cron | Blocked on Phase 3b classifier |

## Files created/modified

| File | Action |
|------|--------|
| `src/etl/genre_tables.py` | Created |
| `src/etl/db.py` | Added DDL for 4 new tables; updated track_profile VIEW |
| `src/etl/sync.py` | Added `sync_genre_profiles()` + wired into `sync()` |

## New machine setup sequence

```bash
make init-db                                      # bootstrap from archived CSVs
make data-sync                                    # pull fresh from Spotify + Last.fm
PYTHONPATH=src uv run python -m etl.genre_tables  # populate genre tables
```

Note: `listen_wiseer.db` is gitignored — not pushed. Data must be re-derived on new machines.
