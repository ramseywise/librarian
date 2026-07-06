# Research: spotify/ Folder Repos vs listen-wiseer

## Sources Studied

Six repos in `/spotify/`:

| Repo | Focus |
|------|-------|
| `spotify_etl-main` | Periodic recently-played ETL → PostgreSQL (pandas, spotipy, AWS RDS) |
| `Rhythmify-main` | Flask app: user dashboard (top artists/tracks/genres) + TF-IDF content-based recommender |
| `Spotify-Discover-2.0` | Flask app: `/me/top/tracks` with time ranges + tuneable recommendation seeds → auto-update playlist daily |
| `Spotify-NewReleases-main` | Cron-style new-release tracker for followed artists + record labels → writes playlist |
| `spotify-release-gun-master` | New-release alerter (albums/singles from followed artists) → RSS/Slack/console |
| `spotify_app-main` | PlaylistBuddy: cosine-similarity playlist augmentation using audio features + "mean song" filter |

---

## What They Do That We Don't

### 1. Persist Recently-Played to DB as `track_history` (spotify_etl)

**How they do it:**
- Call `spotify.current_user_recently_played(limit=50)` on a cron/hourly basis
- Clean: flatten JSON → pandas DataFrame → strip apostrophes from string cols
- Validate: primary key uniqueness on `played_at`, null checks (Pydantic v1 decorator wrapping DataFrame)
- Upsert to PostgreSQL: two tables — `track_history` (played_at PK, track metadata) + `audio_features` (id PK, 13 audio features)
- FK constraint: `track_history.id → audio_features.id`

**Schema they use:**
```sql
track_history (
  played_at TIMESTAMPTZ PRIMARY KEY,
  id VARCHAR(255),          -- track_id
  name, artists, album VARCHAR(255),
  duration_ms INT, explicit BOOL,
  href VARCHAR(500), is_local BOOL,
  popularity INT, uri VARCHAR(255)
)
audio_features (id PK, danceability, energy, key, loudness, mode, speechiness,
                acousticness, instrumentalness, liveness, valence, tempo,
                analysis_url, time_signature)
```

**Gap in listen-wiseer:**
We call `fetch_recently_played()` on-demand (live, max 50, not persisted). No `played_at` timestamps in DuckDB. We have `audio_features` for playlist tracks but not for recently-played tracks. No `track_history` concept.

**Key insight:** Since Spotify only returns the last 50 plays and has no cursor for going further back, you MUST poll frequently (hourly) to build a history. The GDPR export is the only way to get historical data older than ~50 plays.

---

### 2. Top Tracks/Artists by Time Range (`/me/top/`) — Spotify Affinity API (Rhythmify, Discover 2.0)

**What they do:**
- Call `GET /v1/me/top/tracks` and `GET /v1/me/top/artists` with `time_range` parameter
- Three windows: `short_term` (~4 weeks), `medium_term` (~6 months), `long_term` (all-time)
- Paginate up to 100 results (limit=50, offset)
- Return: name, popularity, followers, genres, image URLs, external URLs

**Rhythmify extracts from top artists:**
- name, popularity, followers, genres, image_url, external_url
- Sunburst chart: genre → artist hierarchy (Plotly)
- Genre frequency aggregation across top artists

**Rhythmify extracts from top tracks:**
- song_name, song_duration, song_popularity, album_name, album_release_date, album_total_tracks, artist_name

**Discover 2.0 use:**
- Creates a playlist from top tracks with daily auto-refresh (cron + MySQL to store refresh tokens)
- Tuneable attributes for recommendation seeding (min/max energy, tempo, acousticness, etc.)

**Gap in listen-wiseer:**
We have ZERO `/me/top/` integration. No affinity-based top tracks or artists at any time range. This is a major missing capability — the agent cannot answer "who are my top artists this month?" or "what are my most-listened tracks all-time?".

**Why this matters more than GDPR history:**
- Available instantly via API — no export needed
- 3 time windows cover short, medium, and long-term taste
- Up to 100 artists/tracks per window
- This is Spotify's own affinity calculation (very reliable signal)

---

### 3. New-Release Tracking for Followed Artists + Record Labels (Spotify-NewReleases, spotify-release-gun)

**What they do:**
- `current_user_followed_artists()` — get all followed artists (paginated, cursor-based)
- For each followed artist: `artist_albums(artist_id, album_type='album,single')` — get recent releases
- Filter: within last N days, release_date_precision == 'day', not a radio show/extended version
- Country availability check: `album['available_markets']`
- Deduplication: JSON cache of already-handled album IDs
- Output: update a Spotify playlist, OR push to RSS/Slack

**LabelRecentTracks additionally:**
- Search for label releases: `search(q='label:"{label}" tag:new', type='album')`
- Filter by label name on the full album object (not just search result)

**Gap in listen-wiseer:**
No new-release tracking at all. Agent cannot answer "what has [followed artist] released recently?" or "are there any new releases from artists I follow?". We have `get_related_artists_tool` but no followed-artists awareness or release monitoring.

**Two useful endpoints we're not calling:**
- `GET /v1/me/following?type=artist` — user's followed artists
- `GET /v1/artists/{id}/albums?album_type=album,single` — filtered by recency

---

### 4. Interactive Audio-Feature Filtering for Recommendations (spotify_app PlaylistBuddy)

**What they do:**
- Build a DataFrame of playlist tracks + audio features
- Compute "mean song" — centroid of all audio feature vectors
- Call `sp.recommendations(seed_tracks=...)` in batches of 5
- Score candidates: cosine similarity vs. existing playlist tracks
- Manual feature filter UI: user picks feature (speechiness, acousticness, etc.) + high/low direction
- Mean-song filter: euclidean distance from centroid to select most "playlist-consistent" recommendations

**Gap in listen-wiseer:**
Our engine does similarity scoring but doesn't expose interactive audio-feature filtering to the agent or user. The user can't say "find me tracks like this playlist but more acoustic" with a direct feature constraint.

**Note:** The Spotify Recommendations API (`/v1/recommendations`) with tuneable attributes (`target_energy`, `min_acousticness`, etc.) is entirely unused in our codebase. Our recommender builds candidates from playlist co-occurrence + GMM clusters, not from Spotify's own recommendation endpoint with tuneable parameters.

---

### 5. Currently Playing / Playback Control (Spotify-Discover-2.0)

**What they do:**
- `GET /v1/me/player/currently-playing` — name + album art of current track
- `GET /v1/me/player/devices` — list available devices
- `PUT /v1/me/player/play` — start playback on a device
- `PUT /v1/me/player/pause` — pause
- `PUT /v1/me/player/shuffle` — toggle shuffle
- `POST /v1/me/player/next` — skip to next track

**Gap in listen-wiseer:**
No playback awareness. Agent cannot tell you what's currently playing or control playback. This requires `user-read-playback-state` / `user-modify-playback-state` scopes (we don't have them).

**Assessment:** Lower priority — our Chainlit interface is async, playback control is a different use case. But "what's playing now?" is a natural conversational query.

---

### 6. User Liked/Saved Tracks (Spotify-NewReleases)

**What they do:**
- `current_user_saved_tracks(limit=50)` with pagination — all liked/saved tracks
- Used to filter: don't recommend tracks already liked, don't add duplicate likes to new-release playlist

**Gap in listen-wiseer:**
We have a `faves` table with manual scores, but no integration with Spotify's actual saved tracks library. We don't sync `user-library-read` saved tracks to DuckDB.

---

## What We Have That They Don't

- **GMM + LightGBM ML recommender** — none of these use trained models; they use Spotify's API recommendations or TF-IDF cosine similarity
- **ENOA genre taxonomy** — our custom spatial genre map; none have this
- **RAG / Wikipedia context** — music knowledge retrieval; none have this
- **LangGraph agent with memory** — persistent taste profile across sessions; none have this
- **DuckDB analytics layer** — one place for all data; most use pandas + external DB
- **Structured ETL pipeline** — playlist status config, staleness detection, incremental sync; none have this

---

## Priority Assessment

| Gap | API Used | Effort | Impact |
|-----|----------|--------|--------|
| **Top tracks/artists by time range** | `/me/top/tracks`, `/me/top/artists` | Small | High — directly answers "my top X" queries |
| **Persist recently-played as track_history** | `/me/player/recently-played` (cron) | Medium | High — enables listening history over time |
| **Followed artists + new releases** | `/me/following`, `/artists/{id}/albums` | Medium | Medium — surfaces new music from followed artists |
| **Tuneable recommendations** | `/v1/recommendations` with target params | Small | Medium — feature-constraint filtering ("more acoustic") |
| **Currently playing** | `/me/player/currently-playing` | Small | Low — needs new scope, niche use case |
| **Saved/liked tracks sync** | `/me/tracks` (library) | Medium | Low — we have faves table already |
