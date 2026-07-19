# Research: Phase 7 — Music Exploration Architecture
Date: 2026-04-26

## Summary

Phase 6 left the system stable but the architecture is still a monolith: Spotify client buried in the agent layer, tool modules mixed together, and the graph wired for recommendation-first rather than exploration. Phase 7 reworks this toward a conversational music explorer where recommendations, personalized discovery, genre/artist deep dives, and playlist management are all first-class. The key structural change is extracting Spotify as a proper FastMCP server. Graph topology and tool modules follow from that.

---

## 1. Current State Assessment

### What exists and works

| Component | State |
|---|---|
| LangGraph graph (5-step, 5 intents) | Working. Intent routing solid. |
| GMM + LightGBM recommender | Working. 595k corpus, ENOA spatial features. |
| Spotify OAuth + httpx client | Working. Token cached, retry/backoff on 429. |
| Chainlit UI + Postgres checkpointer | Working. Docker Compose stable. |
| Episodic/taste/procedural memory | Working. In-session only (InMemoryStore). |
| Tavily web search (artist/genre context) | Working. Replaced RAG in Phase 6. |
| Eval harness (LangFuse, 3 tiers) | Working. Intent + tool correctness + RAGAS faithfulness. |

### What's missing for exploration

| Gap | Impact |
|---|---|
| No `GET /me/top/tracks` or `/me/top/artists` by time range | Can't answer "what have I been listening to most" or seed personalization from real history |
| No `GET /artists/{id}/related-artists` | Can't answer "who sounds like X?" without falling back to Tavily |
| No `GET /recommendations` (Spotify native) | No fallback for tracks/artists outside our corpus |
| No `GET /artists/{id}/albums` or `/top-tracks` | Exploration dead-ends when user wants discography context |
| Tools mixed in one file (`src/mcp_server/server.py` + `src/agent/tools.py`) | Hard to extend, no domain separation, agent imports ML layer directly |
| `AgentResponse` output schema missing | Responses are unstructured strings; no track_list, suggestions, or source citations |
| HITL on playlist writes missing | Agent can create/modify playlists without confirmation |

---

## 2. Spotify MCP Server Design

### Why extract it

Currently `src/spotify/` is an httpx client called directly by the agent. Extracting it as a FastMCP server:
- Makes Spotify tools callable from Claude Code and other agents (same pattern as playground's knowledge-base MCP)
- Decouples the agent from the Spotify client — agent becomes tool-agnostic
- Lets us version and test Spotify tools independently
- Follows the established pattern: one FastMCP server per domain

### Proposed tool surface

```
mcp_servers/spotify/
  server.py          — FastMCP app, all tools registered here
  client.py          — httpx client (moved from src/spotify/)
  auth.py            — OAuth flow (moved from src/spotify/)
  schemas.py         — Pydantic models for all responses
```

**Read tools (safe, no confirmation):**

| Tool | Endpoint | Description |
|---|---|---|
| `get_recently_played` | `/me/player/recently-played` | Last N tracks played |
| `get_top_tracks` | `/me/top/tracks?time_range=` | Top tracks: short/medium/long term |
| `get_top_artists` | `/me/top/artists?time_range=` | Top artists: short/medium/long term |
| `search_tracks` | `/search?type=track` | Text search for tracks |
| `search_artists` | `/search?type=artist` | Text search for artists |
| `get_artist_info` | `/artists/{id}` | Artist metadata (genres, popularity, followers) |
| `get_related_artists` | `/artists/{id}/related-artists` | 20 related artists |
| `get_artist_top_tracks` | `/artists/{id}/top-tracks` | Top 10 tracks for artist |
| `get_artist_albums` | `/artists/{id}/albums` | Full discography |
| `get_playlist_tracks` | `/playlists/{id}/tracks` | Tracks in a playlist |
| `get_user_playlists` | `/me/playlists` | User's own playlists |
| `get_spotify_recommendations` | `/recommendations` | Spotify's native recommender (seed-based) |

**Write tools (HITL — confirm before executing):**

| Tool | Endpoint | Description |
|---|---|---|
| `create_playlist` | `POST /users/{id}/playlists` | New playlist (name + description) |
| `add_tracks_to_playlist` | `POST /playlists/{id}/tracks` | Add track URIs to playlist |
| `remove_tracks_from_playlist` | `DELETE /playlists/{id}/tracks` | Remove tracks |

### Authentication

OAuth flow stays in `auth.py`. Token cached to `.spotify_cache`. MCP server reads it on startup and refreshes as needed. Same httpx client, just relocated.

---

## 3. Agent Graph Redesign

### Current topology (post-5b)

```
START → trim_history → classify_intent → route_after_classify
  → low confidence  → clarify_or_proceed → END
  → high confidence → rewrite_query → agent → route
      → call_tools → validate_tool_output → agent (loop)
      → END
```

This works. The skeleton stays. What changes is the tool layer underneath `agent` and the intent taxonomy.

### Intent taxonomy

Current: `recommend`, `search`, `explore`, `save`, `direct` (5 intents)

`explore` is doing too much work — "explore genre history" and "explore related artists" and "explore my listening stats" are very different queries that need different tools. Proposed split:

| Intent | Covers | Primary tools |
|---|---|---|
| `recommend` | "songs like X", "more of this vibe", playlist-based recs | `recommend.*`, `get_spotify_recommendations` |
| `discover` | "what's new in X genre", "artists I haven't heard", fresh content | `get_spotify_recommendations`, `search_artists`, Tavily |
| `explore_artist` | "tell me about X", "who influenced X", discography deep dives | `get_artist_info`, `get_related_artists`, `get_artist_top_tracks`, `get_artist_albums`, Tavily |
| `explore_genre` | "history of drum and bass", "what came before X", genre lineage | Tavily `search_genre_history`, `search_artists` |
| `explore_my_taste` | "what have I been listening to", "my top this month", taste analysis | `get_top_tracks`, `get_top_artists`, `get_recently_played`, `search_taste_memory` |
| `save` | "create a playlist", "add these to X", HITL playlist writes | `create_playlist`, `add_tracks_to_playlist` (with confirm gate) |
| `direct` | Chit-chat, clarifications, no-tool responses | None |

6 → 7 intents, but each is sharper. Classifier prompt stays the same shape.

### Tool module layout

```
src/agent/tools/
  __init__.py        — exports ALL_TOOLS list
  recommend.py       — by_track, by_artist, by_genre, by_playlist (wraps ML layer)
  spotify_read.py    — wraps Spotify MCP read tools via MCP client
  spotify_write.py   — wraps Spotify MCP write tools + HITL confirm node
  web_search.py      — search_artist_context, search_genre_history (Tavily)
  memory.py          — manage_taste_memory, search_taste_memory
```

`spotify_read.py` and `spotify_write.py` call the FastMCP server via `langchain-mcp-adapters` or direct MCP client — same as playground's knowledge-base MCP adapter pattern. The agent doesn't import `src/spotify/` directly anymore.

### AgentResponse schema

Add a `format_response` node before END that coerces agent output into:

```python
class AgentResponse(BaseModel):
    message: str                    # conversational text
    track_list: list[Track] | None  # for recommend/discover intents
    suggestions: list[str] | None   # follow-up prompts ("Want me to save these?")
    sources: list[str] | None       # Tavily URLs if web search was used
```

Chainlit renders `track_list` as a card list, `suggestions` as quick-reply chips.

---

## 4. Exploration UX — Concrete Capabilities

What "music exploration" means in practice:

### Artist deep dives
> "Tell me about Four Tet" / "What influenced Floating Points?" / "Show me Burial's full discography"

Agent calls `get_artist_info` + `get_related_artists` + Tavily `search_artist_context`. Returns: bio summary, key albums, related artists as cards, Tavily sources cited. User can then ask about any related artist (coreference handled by rewrite_query).

### Genre lineage
> "What came before drum and bass?" / "How did UK garage evolve?" / "What's the history of bossa nova?"

Tavily `search_genre_history` with a structured query. Returns: timeline summary with key artists. Agent can follow up with `search_artists` on any mentioned artist to surface listenable examples in the corpus.

### Taste analysis
> "What have I been listening to lately?" / "Who are my top artists all-time?" / "What genres am I into this month?"

`get_top_artists(time_range=short_term)` + `get_top_tracks`. Agent synthesizes: "Your top genre this month is UK soul, led by Little Simz and Sampha. Want recs in that direction?"

### Discovery
> "What's new in jazz I might like?" / "Artists similar to my top ones but I haven't saved yet"

Combines `get_top_artists` → `get_related_artists` → filter against `get_user_playlists` tracks to surface unfamiliar artists. Spotify `get_spotify_recommendations` as seed-based fallback.

### Recommendations (unchanged)
Existing ENOA-based pipeline. HITL playlist save at the end.

---

## 5. Implementation Sequence

Three phases, each shippable independently:

### Phase 7a — Spotify MCP server + tool modules
Relocate `src/spotify/` → `mcp_servers/spotify/`. Add missing read tools (top tracks/artists, related artists, artist info/albums). Add domain-split tool modules to `src/agent/tools/`. Agent now calls MCP instead of importing client directly. No graph changes.

**Acceptance:** All existing tests pass. New tools callable from Claude Code via MCP config. `get_top_artists` and `get_related_artists` work end-to-end.

### Phase 7b — Graph + intent refactor
Split `explore` → `explore_artist` / `explore_genre` / `explore_my_taste` / `discover`. Add `AgentResponse` schema + `format_response` node. Add HITL confirm node for write tools. Update intent classifier prompts + eval golden dataset.

**Acceptance:** Intent classifier hits ≥90% on extended golden set including new intents. HITL gate fires correctly on playlist writes. Chainlit renders track cards.

### Phase 7c — Exploration UX polish
Genre lineage queries working via Tavily. Taste analysis with time range selector. Discovery flow combining top artists → related → corpus filter. Cross-session memory for taste preferences (Redis/Postgres store, replacing InMemoryStore).

**Acceptance:** End-to-end chat demo covering all 7 intents. Chainlit quick-reply suggestions firing. Memory persists across Chainlit sessions.

---

## Key Decisions

| Decision | Choice | Rationale |
|---|---|---|
| ADK vs LangGraph | LangGraph | State management needed for ML pipeline; familiar; LangSmith observability already wired |
| MCP client in agent | `langchain-mcp-adapters` | Same pattern as playground knowledge-base MCP; avoids direct process management |
| Subagents vs single graph | Single graph | Prototype — one graph with sharp nodes is simpler to debug than subagent orchestration |
| Music knowledge wiki | Defer | Tavily covers exploration for Phase 7; librarian integration is a separate project |
| Cross-session memory store | Redis (Phase 7c) | InMemoryStore is dev-only; Postgres checkpointer already running in compose |
| `AgentResponse` rendering | Chainlit native | Already embedded; no new UI work needed for cards/chips |
