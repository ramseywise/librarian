---
title: Phase 7a — Exploration Tools
status: ACTIVE
date: 2026-04-26
---

## Goal

Add the missing Spotify endpoints needed for exploration (top tracks/artists, artist info, discography, Spotify recommendations), wire them as agent tools, and update the system prompt and intent hints to describe them. The tool module split already happened in Phase 6 — this is additive only.

## Scope

**Not in scope:** MCP server extraction to `mcp_servers/spotify/` (deferred), intent taxonomy refactor (Phase 7b), cross-session Redis memory (Phase 7c).

---

## Steps

### 1. `src/spotify/fetch.py` — 6 new functions

- `fetch_top_tracks(client, time_range, limit)` — GET /me/top/tracks
- `fetch_top_artists(client, time_range, limit)` — GET /me/top/artists
- `fetch_artist_info(client, artist_id)` — GET /artists/{id}
- `fetch_artist_top_tracks(client, artist_id)` — GET /artists/{id}/top-tracks
- `fetch_artist_albums(client, artist_id)` — GET /artists/{id}/albums
- `fetch_spotify_recommendations(client, seed_tracks, seed_artists, seed_genres, limit)` — GET /recommendations

### 2. `src/agent/tools/spotify_read.py` — 6 new StructuredTools

- `get_top_tracks_tool` — taste analysis ("my top tracks this month")
- `get_top_artists_tool` — taste analysis ("my top artists all-time")
- `get_artist_info_tool` — metadata (genres, popularity, followers)
- `get_artist_top_tracks_tool` — discography entry point
- `get_user_playlists_tool` — list playlists (uses existing `fetch_my_playlists`)
- `get_spotify_recommendations_tool` — discovery / corpus fallback

### 3. `src/agent/tools/__init__.py` — add all 6 to ALL_TOOLS

### 4. `src/agent/nodes.py`
- SYSTEM_PROMPT: add tool entries for all 6 new tools
- `_INTENT_TOOL_HINTS`: add `explore_my_taste`, `explore_artist`, `discover`
- `format_response`: add `suggestions` list to `agent_response`

### 5. `src/mcp_server/server.py` — add same read tools for Claude Code access

### 6. `tests/unit/test_fetch_exploration.py` — unit tests for new fetch functions (synthetic fixtures)

---

## Acceptance

- All existing tests pass (`uv run pytest tests/unit/ -x`)
- `get_top_artists` and `get_top_tracks` callable from Claude Code via MCP config
- Agent responds correctly to: "what have I been listening to lately?", "tell me about Four Tet", "show me my top artists this month"
