# Research: Peer Repo Capabilities vs listen-wiseer

## Sources Studied

- `spotify-ai-analytics-main` — Listening history analytics from Spotify JSON GDPR exports (Streamlit + Polars + LangGraph)
- `spotify-langgraph-agent-main` — Thin MCP-based Spotify search agent (Groq + LangGraph ReAct)
- `WikiSpotify-MCP-Server-main` — Wikipedia + Spotify public search via MCP (Gemini, deployed to Cloud Run)

---

## What They Do That We Don't

### 1. Listening History Analytics (spotify-ai-analytics)

**What it does:**
Parses the Spotify GDPR JSON export (`StreamingHistory*.json`) — the full timestamped play log you request from Spotify privacy settings. Fields include: `ts` (UTC timestamp), `ms_played`, `track_name`, `artist_name`, `album_name`, `spotify_track_uri`, `reason_start`, `reason_end`, `shuffle`, `skipped`.

**Analytics implemented:**
- `get_summary()` — total plays, total minutes, unique tracks/artists, date range
- `get_top_artists(start_date, end_date)` — hours played, track count, unique track ratio
- `get_top_tracks(start_date, end_date, artist_filter)` — play count, minutes played
- `get_monthly_listening_trend()` — year-month aggregation of plays + time
- `get_weekly_listening_trend()` — weekday × time-of-day (Night/Morning/Afternoon/Evening bins) cross-tab

**Dashboard:** Streamlit with Plotly — interactive bar charts for all the above.

**LangGraph agent:**
- 3-node graph: `IntentParser → DataFetch → Analyst`
- Intent classification via structured LLM output → `factual_query | insight_analysis | recommendation | other`
- Per-intent system prompt personas in `Analyst` node
- Context-window guard: result truncation at 1000 chars, warning if tool limit > 15 rows

**Gap in listen-wiseer:**
- We have NO listening history in DuckDB. `fetch_recently_played()` is on-demand live call (max 50 tracks, not persisted, no timestamps stored).
- We have NO temporal analytics: no play counts, no listening timeline, no "what did I listen to last month" capability.
- The agent cannot answer: "What were my top artists this year?", "How has my listening changed?", "When do I listen most?"

---

### 2. Album Metadata Tool (WikiSpotify)

**What it does:**
`spotify_get_album(album_name, artist_name="")` — Spotify v1/search for albums, returns title, artist, release date, track count, Spotify link.

**Gap in listen-wiseer:**
- MCP server has `get_track_features`, `get_playlist_tracks` but no album-level lookup.
- Agent has `search_tracks_tool` (track search) but nothing for "when was [album] released?" or "how many tracks on [album]?"

---

### 3. Artist Public Profile Tool (WikiSpotify)

**What it does:**
`spotify_search_artist(artist_name)` — Spotify v1/search for artists, returns name, genres (Spotify-assigned), followers, popularity score, Spotify link.

**Gap in listen-wiseer:**
- Agent has `get_related_artists_tool` (related-artists endpoint) but no direct artist profile query.
- Cannot answer: "How popular is [artist]?", "How many followers does [artist] have?", "What genres does Spotify classify them as?"

---

### 4. Direct Wikipedia Summary Tool (WikiSpotify)

**What it does:**
`wikipedia_summary(title)` — fetches Wikipedia page summary directly via `wikipediaapi` library.

**Gap in listen-wiseer:**
- We have full RAG pipeline (Wikipedia ingest → chunk → embed → DuckDB vector search) but this is async and requires prior ingestion.
- `get_artist_context_tool` wraps `MusicRAG.get_context()` which triggers Wikipedia fetch + chunk + embed on cache miss — slow for first access.
- A lightweight direct-fetch fallback could serve known-good cases faster.

**Note:** Our RAG approach is architecturally superior for nuanced queries. The direct-fetch is only useful as a quick complement, not a replacement.

---

## What We Have That They Don't

- **ML-backed recommendations** — GMM clustering + LightGBM reranker, 4 request types (track/artist/playlist/genre)
- **ENOA genre taxonomy** — 6k+ genre spatial map, genre-zone navigation
- **Persistent taste memory** — langmem across sessions (procedural + episodic + taste facts)
- **Audio feature extraction** — 14 Spotify audio features in DuckDB
- **Full RAG pipeline** — hybrid search (semantic + keyword), chunked Wikipedia, reranking
- **Multi-node agent graph** — intent classification, query rewriting, output validation, prompt optimization

---

## Key Insight

The most substantial gap is **listening history analytics**. The peer repo demonstrates that Spotify's GDPR export is rich enough to support meaningful personal analytics (temporal patterns, diversity metrics, listening habits) — and this is entirely orthogonal to our recommendation engine. We already have the stack (Polars + DuckDB + LangGraph agent) to implement this. The missing piece is:

1. Ingest the GDPR export into a `listening_history` DuckDB table
2. Add analysis functions (temporal aggregations)
3. Expose them as agent tools
4. Optionally: ETL the recently-played endpoint to persist ongoing history

The album/artist public profile tools are quick wins (~50 lines each) that round out the agent's factual Q&A capability.
