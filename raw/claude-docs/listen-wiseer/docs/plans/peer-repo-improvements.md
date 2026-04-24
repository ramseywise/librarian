# Plan: Peer Repo Improvements

**Research:**
- `.claude/docs/research/peer-repos.md` (spotify-ai-analytics, spotify-langgraph-agent, WikiSpotify-MCP)
- `.claude/docs/research/spotify-folder-repos.md` (spotify_etl, Rhythmify, Spotify-Discover-2.0, NewReleases, release-gun, spotify_app)

**Status:** Draft — awaiting approval

---

## Summary

Six improvements derived from studying both sets of peer repos. Ordered by impact.

---

## Improvement 1 — Top Tracks & Artists by Time Range (`/me/top/`)

**Why:** Biggest quick win. Multiple peer repos (Rhythmify, Discover 2.0) use Spotify's Affinity API to answer "my top artists this month", "my most-listened tracks all-time". We have zero `/me/top/` integration. This is entirely different from recently-played — it's Spotify's own affinity score, reliable, and instantly available in 3 time windows.

**Three time windows:**
- `short_term` — ~4 weeks
- `medium_term` — ~6 months
- `long_term` — all-time

**Files to modify/create:**
1. `src/spotify/fetch.py` — add:
   ```python
   fetch_top_tracks(client, time_range: str, limit: int = 50) → list[TopTrack]
   fetch_top_artists(client, time_range: str, limit: int = 50) → list[TopArtist]
   ```
   Both call `GET /v1/me/top/{type}?time_range={}&limit={}`, paginate to `limit`.

2. `src/spotify/schemas.py` (or `src/utils/schemas.py`) — add Pydantic models:
   ```python
   class TopTrack(BaseModel):
       track_id: str; name: str; artist: str; album: str
       popularity: int; duration_ms: int; spotify_url: str

   class TopArtist(BaseModel):
       artist_id: str; name: str; genres: list[str]
       popularity: int; followers: int; spotify_url: str
   ```

3. `src/agent/tools.py` — add two tools to `ALL_TOOLS`:
   ```python
   get_top_tracks_tool     # args: time_range (short/medium/long_term), limit (default 10)
   get_top_artists_tool    # args: time_range (short/medium/long_term), limit (default 10)
   ```

4. `src/agent/nodes.py` — add `"top_tracks"` and `"top_artists"` to `_INTENT_TOOL_HINTS`.

5. `src/mcp_server/server.py` — expose as MCP tools.

**Scopes required:** `user-top-read` — already in our scope list.

---

## Improvement 2 — Persist Recently-Played as `track_history` (rolling cron)

**Why:** `fetch_recently_played()` is currently a live call (max 50 tracks, not persisted). We lose all history older than ~50 plays. By polling hourly via `make sync-history`, we accumulate a real timeline. This is the complement to the GDPR export — the GDPR export gives deep history, the cron gives ongoing accumulation.

**Key constraint (from peer repo research):** Spotify only returns last 50 recently-played. Must poll frequently (hourly) to avoid gaps.

### 2a — DuckDB table

Add to `src/etl/db.py`:
```sql
CREATE TABLE IF NOT EXISTS track_history (
    played_at     TIMESTAMPTZ PRIMARY KEY,
    track_id      VARCHAR,
    track_name    VARCHAR,
    artist_name   VARCHAR,
    album_name    VARCHAR,
    duration_ms   INTEGER,
    popularity    INTEGER,
    spotify_url   VARCHAR
)
```

### 2b — Sync function

Add `sync_recently_played(conn, client)` to `src/etl/sync.py`:
- Call `fetch_recently_played(client)` → returns last 50 plays with `played_at` timestamps
- INSERT OR IGNORE on `played_at` PK (idempotent re-runs)
- Log: `log.info("sync.history.done", n_inserted=n, n_skipped=skipped)`
- Gated on `sync_recently_played: bool = True` in `src/utils/config.py`

### 2c — Makefile target

```makefile
sync-history:
    PYTHONPATH=src uv run python -m etl.sync --history-only
```

**Note on GDPR export:** Separate from this. If user has the GDPR export JSON files, Improvement 5 (below) ingests them into the same `track_history` table.

---

## Improvement 3 — Artist Public Profile + Album Metadata Tools

**Why:** Quick wins identified in peer-repo research (WikiSpotify). Agent currently can't answer "how popular is X?", "what genres does Spotify classify X as?", or "when was [album] released?".

### 3a — Artist profile tool

Add to `src/spotify/fetch.py`:
```python
fetch_artist_profile(client, artist_name: str) → ArtistProfile
```
- `GET /v1/search?q={artist_name}&type=artist&limit=1`
- Returns: `ArtistProfile(name, genres, followers, popularity, spotify_url, artist_id)`

Add to `src/agent/tools.py` + `src/mcp_server/server.py`.

### 3b — Album info tool

Add to `src/spotify/fetch.py`:
```python
fetch_album_info(client, album_name: str, artist_name: str = "") → AlbumInfo
```
- `GET /v1/search?q=album:{album_name}+artist:{artist_name}&type=album&limit=1`
- Returns: `AlbumInfo(name, artist, release_date, total_tracks, spotify_url)`

Add to `src/agent/tools.py` + `src/mcp_server/server.py`.

**Pydantic models** — add to `src/utils/schemas.py`:
```python
class ArtistProfile(BaseModel):
    name: str; genres: list[str]; followers: int
    popularity: int; spotify_url: str; artist_id: str

class AlbumInfo(BaseModel):
    name: str; artist: str; release_date: str
    total_tracks: int; spotify_url: str
```

---

## Improvement 4 — Followed Artists + New Release Tracker

**Why:** Two peer repos (NewReleases, release-gun) do this. Agent currently has `get_related_artists_tool` but no followed-artist awareness. "What has [artist I follow] released this week?" is unanswerable. "New release" tracking is a distinct use case from recommendations.

**Two new capabilities:**

### 4a — Fetch followed artists

Add to `src/spotify/fetch.py`:
```python
fetch_followed_artists(client) → list[FollowedArtist]
```
- `GET /v1/me/following?type=artist&limit=50` — cursor-paginated (use `after` cursor)
- Returns: `FollowedArtist(artist_id, name, genres, popularity, followers)`

**Scope required:** `user-follow-read` — need to add to `.env.example` and OAuth scope list.

### 4b — Check recent releases per artist

Add to `src/spotify/fetch.py`:
```python
fetch_artist_recent_releases(client, artist_id: str, days: int = 14) → list[Release]
```
- `GET /v1/artists/{id}/albums?album_type=album,single&limit=50`
- Filter: `release_date >= today - days`, `release_date_precision == 'day'`
- Returns: `Release(album_id, name, artist, release_date, release_type, total_tracks, spotify_url)`

### 4c — Agent tool

Add `get_new_releases_tool` to `src/agent/tools.py`:
- Calls `fetch_followed_artists()` → for each artist, `fetch_artist_recent_releases(days=14)`
- Returns: list of recent releases from followed artists, sorted by release_date desc
- Limit output to 20 releases max (context guard)

Add to `src/mcp_server/server.py`.

**Scope change:** Add `user-follow-read` to `src/spotify/auth.py` SCOPE constant and `.env.example` docs.

---

## Improvement 5 — GDPR History Ingest (deep historical listening data)

**Why:** The spotify-ai-analytics peer repo demonstrates that Spotify's GDPR export (`StreamingHistory*.json`) enables rich temporal analytics going back years. Combined with Improvement 2 (rolling cron), we get: GDPR export for deep history + hourly cron for ongoing. Same `track_history` table receives both.

**Requires:** User has requested their Spotify data from spotify.com/account/privacy (takes ~5 days to arrive as ZIP).

### 5a — Ingest module

New file: `src/etl/history.py`

```python
def ingest_history(conn: duckdb.DuckDBPyConnection, json_dir: Path) -> int:
    """Ingest Spotify GDPR export JSON files into track_history."""
```

Implementation:
- `pl.read_ndjson()` / `pl.read_json()` with `diagonal_relaxed` for multi-file concat
- Filter: `ms_played >= 30_000` (30s threshold — skip non-plays)
- Filter: `spotify_track_uri IS NOT NULL` (skip podcast/audiobook entries)
- Extract `track_id` from URI: `spotify:track:{track_id}`
- Map GDPR fields to `track_history` schema:
  - `ts` → `played_at` (UTC timestamp)
  - `master_metadata_track_name` → `track_name`
  - `master_metadata_album_artist_name` → `artist_name`
  - `master_metadata_album_album_name` → `album_name`
  - `ms_played` → `duration_ms`
- INSERT OR IGNORE on `played_at` PK (idempotent)
- Return count of inserted rows

### 5b — Makefile target

```makefile
ingest-history:
    PYTHONPATH=src uv run python -m etl.history
```

### 5c — Agent analytics tools (pairs with 5a)

New file: `src/etl/history_analytics.py` — DuckDB-backed functions:

```python
get_listening_summary(conn, start_date=None, end_date=None) → dict
  # total_plays, total_minutes, unique_tracks, unique_artists, date_range

get_top_artists_history(conn, limit=10, start_date=None, end_date=None) → list[dict]
  # artist_name, total_plays, minutes_played

get_top_tracks_history(conn, limit=10, start_date=None, end_date=None) → list[dict]
  # track_name, artist_name, play_count, minutes_played

get_monthly_trend(conn) → list[dict]
  # year, month, total_plays, total_minutes

get_weekly_pattern(conn) → list[dict]
  # weekday, time_range (Night/Morning/Afternoon/Evening), total_plays
```

Add 4 tools to `src/agent/tools.py` wrapping these functions.
Add `"listening_history"` intent to `_INTENT_TOOL_HINTS` in `src/agent/nodes.py`.

---

## Improvement 6 — Tuneable Spotify Recommendations (`/v1/recommendations`)

**Why:** Discovered in spotify_app (PlaylistBuddy). Spotify's recommendation endpoint accepts `target_*` and `min_*/max_*` params for audio features (energy, acousticness, tempo, danceability, etc.). We never use this endpoint. Our agent cannot handle "find tracks like this playlist but more acoustic" or "energetic Brazilian music".

**Spotify Recommendations API:**
```
GET /v1/recommendations
  seed_tracks: up to 5 track IDs
  seed_artists: up to 5 artist IDs
  seed_genres: up to 5 genre strings
  target_energy, target_acousticness, target_danceability: 0.0–1.0
  min_tempo, max_tempo: BPM
  limit: up to 100
```

**Files to modify:**
1. `src/spotify/fetch.py` — add:
   ```python
   fetch_recommendations(
       client,
       seed_tracks: list[str] | None = None,
       seed_artists: list[str] | None = None,
       seed_genres: list[str] | None = None,
       target_features: dict[str, float] | None = None,
       limit: int = 20
   ) → list[RecommendedTrack]
   ```

2. `src/agent/tools.py` — add `spotify_recommend_tool`:
   - Accepts: seed track/artist names (agent resolves to IDs), optional feature constraints as natural language ("more acoustic", "high energy") → parsed to `target_*` params
   - Returns: list of recommended tracks with preview URLs

**Feature parsing:** Agent uses a small dict to map natural language to Spotify params:
```python
FEATURE_PRESETS = {
    "acoustic": {"target_acousticness": 0.8},
    "energetic": {"target_energy": 0.85},
    "danceable": {"target_danceability": 0.8},
    "instrumental": {"target_instrumentalness": 0.7},
    "mellow": {"target_energy": 0.3, "target_valence": 0.4},
}
```

---

## Implementation Order

| # | Improvement | New Files | Modified Files | Effort |
|---|-------------|-----------|----------------|--------|
| 1 | Top tracks/artists by time range | — | fetch.py, tools.py, server.py, nodes.py | Small |
| 2 | Artist profile + album info tools | — | fetch.py, tools.py, server.py, schemas.py | Small |
| 3 | `track_history` table DDL | — | etl/db.py | Small |
| 4 | Persist recently-played (cron) | — | etl/sync.py, config.py, Makefile | Small |
| 5 | Followed artists + new releases | — | fetch.py, tools.py, server.py, auth.py | Medium |
| 6 | GDPR history ingest | etl/history.py | etl/db.py, Makefile | Medium |
| 7 | History analytics tools | etl/history_analytics.py | agent/tools.py, agent/nodes.py | Medium |
| 8 | Tuneable Spotify recommendations | — | fetch.py, tools.py, server.py | Medium |

**Suggested batches:**
- **Batch A (quick wins):** Steps 1 + 2 — 4 new tools, no schema changes, isolated
- **Batch B (history foundation):** Steps 3 + 4 — DDL + cron, prerequisite for 6+7
- **Batch C (new data sources):** Steps 5 + 6 + 7 — followed artists, GDPR ingest, analytics
- **Batch D (recommendation enhancement):** Step 8 — tuneable recommendations

---

## Scopes Needed (new)

| Scope | Required for |
|-------|-------------|
| `user-top-read` | Improvement 1 — already in scope list ✓ |
| `user-follow-read` | Improvement 5 — NEW, add to auth.py + .env.example |
| `user-read-currently-playing` | Playback awareness (out of scope for now) |

---

## Out of Scope

- Streamlit/Plotly dashboard — wrong UI for this project (we have Chainlit)
- Cloud deployment / GCP Secret Manager — local .env pattern is fine
- Direct Wikipedia summary tool — our RAG covers this better
- Currently playing / playback control — different use case, needs new scopes, lower priority
- Liked/saved tracks sync — we have `faves` table; redundant for now
