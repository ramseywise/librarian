# Research: What Would Support Building listen-wiseer
Date: 2026-04-02 (updated — expanded to cover recommender design, Spotify API, and RAG/websearch)

## Summary
Phase 2's content-based recommender is structurally sound but has gaps worth addressing before agent wiring: the 595k-row corpus is large enough to warrant approximate nearest-neighbour search instead of brute-force cosine, and the ENOA coordinate system in the data is a strong differentiator from Spotify's own recommendations. Spotify's `/recommendations` endpoint produces collaborative-filtered results — these are complementary to, not competitive with, our audio-feature approach and should be exposed as a tool for the agent to compare or blend. For artist context RAG, Wikipedia is unreliable for niche/emerging artists; a multi-source strategy (Wikipedia + MusicBrainz + web search) is needed to surface "crazy facts" reliably.

## Scope
Investigated: Phase 1/2 recommender design choices, corpus characteristics, Spotify recommendation API capabilities and gaps, RAG/websearch options for artist context. Did not investigate: cloud deployment, multi-user auth, real-time Spotify streaming events.

---

## Findings

### 1. Phase 1/2 Recommender — What Was Built and Why

#### Corpus characteristics
| Property | Value |
|----------|-------|
| Corpus rows | 595,858 tracks |
| Feature dimensions | 12 numeric (audio) + 2 ENOA spatial + 24 one-hot key_mode + 8 one-hot decade = ~46 effective dims |
| Playlist label source (`enoa.csv`) | 2,870 tracks across 32 playlists |
| Positive rate in classifiers | ~52 positives / 2,870 total ≈ 1.8% — highly imbalanced |

At 595k rows, a brute-force cosine scan is **O(n·d)** per query with n=595k and d=12. In practice this runs in ~200ms on CPU with numpy, which is acceptable but leaves room for approximation.

#### Audio feature limitations
Spotify's audio features (`danceability`, `energy`, `valence`, etc.) are derived from an in-house signal processing model (Echo Nest / Spotify ML). Key limitations:
- **No timbre/texture representation** — features capture rhythm and energy but not tone colour (e.g. Rhodes vs Moog vs acoustic piano all look similar to the model)
- **Genre label sparsity** — `first_genre` in the corpus is the primary artist genre, not per-track. Genres like `afrobeat`, `ambient`, `experimental` are broad.
- **ENOA coordinates** (top/left): these are the biggest differentiator. They encode a 2D emotional/sonic space derived from playlist curation behaviour — tracks close in ENOA space are things *the user* has grouped together, not just algorithmically similar. This is what makes GenrePipeline and the spatial proximity filter meaningful.

#### Design choices — assessed
| Choice | Assessment | Notes |
|--------|------------|-------|
| GMM (8 components) | Sound | Soft assignments give graded cluster membership; 8 aligns with user's genre groupings |
| LightGBM reranker per playlist | Sound | Handles imbalance well; calibrated probs useful; but 32 classifiers means 32 pkl files — lazy loading is correct call |
| Camelot wheel (24 positions) | Correct | Standard DJ mixing tool; circular distance implementation is correct |
| Tempo half/double-time detection | Correct | Common for dance music (zouk, house) where tracks at 60bpm and 120bpm are the same feel |
| ENOA as a feature in cosine | Good | Adds spatial personalisation signal that pure audio features don't have |
| Weighted cosine vs. Euclidean | Appropriate | Normalisation makes scale-different features (tempo 60-200 vs. danceability 0-1) comparable |
| MMR for diversity | Good | Prevents top-k from being 10 near-identical tracks |

#### Gap: approximate nearest neighbour
At 595k rows, brute-force cosine is ~150-250ms per query. For interactive use (agent calls tool, user waits) this is fine. If the agent makes multiple tool calls per turn (track + artist + playlist), latency compounds. Worth noting but not a blocker.

Options if latency becomes a problem: **FAISS** (IndexFlatIP after L2-normalising) — deterministic exact results, ~10ms. **Annoy** — simpler but approximate. Not needed now.

#### Gap: no freshness signal
Corpus is frozen at training time. New tracks released after the corpus was built won't appear in recommendations. The agent could surface this by appending live Spotify search results to recommendations for genres/artists the user is actively exploring — see §3.

---

### 2. Spotify API — What It Offers and How to Use It

Spotify has its own recommendation endpoints. These are distinct from what we built and complementary.

#### `/recommendations` endpoint
- **Input**: up to 5 seed tracks, artists, or genres + audio feature targets (e.g. `target_energy=0.8`, `min_danceability=0.5`)
- **Output**: list of recommended tracks (up to 100)
- **Algorithm**: collaborative filtering + audio features + editorial metadata — not disclosed
- **Key difference from our system**: Spotify's results are popularity-weighted and corpus-global; our system is personalised to the user's own playlist history via ENOA coordinates and per-playlist classifiers
- **Rate limits**: counted against standard API quota (no separate limit)
- **Auth required**: yes, same OAuth flow already implemented

**What Spotify recommendations are good for:**
- Seeding new genre exploration (user asks "more like this artist" when artist not in our corpus)
- Fallback when our corpus misses a track (track not in 595k rows)
- Discovering tracks outside the user's existing taste bubble

**What they don't do:**
- Personalise to *this user's* playlist patterns (ENOA, classifier signals)
- Apply Camelot/tempo compatibility constraints
- Return tracks that match the user's spatial taste map

#### Other useful Spotify endpoints
| Endpoint | What it returns | Use for |
|----------|-----------------|---------|
| `GET /artists/{id}/related-artists` | 20 related artists | "Who sounds like X?" |
| `GET /artists/{id}/top-tracks` | Top 10 tracks (market-filtered) | Seed for ArtistPipeline |
| `GET /artists/{id}/albums` | Album list | RAG context, discography |
| `GET /search?type=track,artist` | Search by text query | Resolve "find me tracks by X" |
| `GET /audio-analysis/{id}` | Detailed beat/section/pitch analysis | Richer timbre data (not in our corpus) |
| `GET /me/top/tracks` and `/artists` | User's personal top tracks/artists | Session personalisation |

#### Missing from current MCP server
The server exposes `get_playlist_tracks`, `get_track_features`, `get_recently_played`, `search_tracks`. Not exposed:
- `GET /recommendations` — the agent has no tool to call Spotify's own recommender
- `GET /artists/{id}/related-artists` — useful for "find me artists like X"
- `GET /me/top/tracks` and `/me/top/artists` — user's all-time listening profile

These would be natural Phase 4 tool additions.

---

### 3. RAG / Websearch for Artist Context

The "crazy facts" use case: user asks "what's interesting about the artist I'm listening to?" — information that would not be in Claude Haiku's training data, or that is too recent/obscure.

#### Problem with Wikipedia alone
Wikipedia is good for established artists (Aphex Twin, Miles Davis) but:
- Missing or thin pages for niche/emerging artists (e.g. "Menahan Street Band", "El Michels Affair" — both in the corpus)
- Wikipedia content is slow to update for current news/releases
- `wikipedia.page(title).content` returns the full article (~20k chars) — chunking strategy matters

#### Multi-source strategy
| Source | Strengths | Weaknesses | Package |
|--------|-----------|------------|---------|
| Wikipedia | Deep biographical, discography, genre history | Thin or absent for niche artists | `wikipedia` (installed) |
| MusicBrainz | Open music database; strong for release dates, label history, member changes, collaborations | No "interesting facts" narrative | `musicbrainz` (not installed) or REST API via `httpx` |
| Web search | Current tour dates, reviews, recent news, collaborations | Rate-limited; requires API key (Brave, Serper, Tavily) | — |
| Last.fm API | Artist bios, similar artists, listener counts | Bio is Wikipedia-derived; similar artists is collaborative | REST via `httpx` |
| Bandcamp | Artist narrative, album notes | Hard to scrape reliably | — |

**Recommended approach**: Wikipedia as primary (already installed), Last.fm API as fallback for niche artists (bio + similar), web search (Brave Search API or Tavily) for recency. This is a 3-tier fallback:
1. Wikipedia: `wikipedia.search(artist_name)` → `wikipedia.page()` → chunk and embed
2. Last.fm: `https://ws.audioscrobbler.com/2.0/?method=artist.getinfo` — free API, just needs a key
3. Brave Search API or Tavily — paid but cheap (~$5/mo for low volume); returns structured results

#### ChromaDB strategy (Phase 4)
- **Don't pre-ingest everything** — the user's corpus has artists from 32 playlists + 595k tracks. Ingesting all of them upfront is slow and likely to hit Wikipedia rate limits.
- **Lazy ingestion**: agent calls a tool `get_artist_context(artist_name)` → checks ChromaDB for cached passages → if miss, fetches Wikipedia/Last.fm, chunks, embeds, upserts → returns top-k passages
- **Chunk size**: 300-500 tokens with 50-token overlap works well for Wikipedia articles. Shorter chunks for fact retrieval; longer for biography queries.
- **Collection strategy**: single `"artist_info"` collection with `artist_id` as metadata filter — avoids one collection per artist.
- **`all-MiniLM-L6-v2`** (384-dim, installed) is appropriate here. No E5 prefix required.

#### What ChromaDB gives you that in-context doesn't
At 595k tracks × potentially hundreds of artists, putting all artist bios in context is impossible. ChromaDB lets the agent retrieve only the 3-5 most relevant passages for the current conversation topic.

---

### 4. Infrastructure Gaps (carried from prior research)

| Gap | Impact | Fix |
|-----|--------|-----|
| `src/agent/` is empty | Blocks Phases 3-5 | Create `__init__.py`, `state.py`, `nodes.py`, `graph.py`, `tools.py` |
| `src/paths.py` missing | Path fragility | Add before Phase 3 |
| Training incomplete (2/32 classifiers) | Engine fails for playlist pipeline | Run `make train` |
| `chromadb.Client()` deprecated | Phase 4 startup error | Use `PersistentClient(path=...)` |
| `/recommendations`, related-artists not in MCP | Agent can't call Spotify's own recommender | Phase 4 tool additions |
| `langchain-mcp-adapters` not installed | Not a gap — use `StructuredTool` wrapping | No action needed |

---

## Key Unknowns

- **Last.fm API key**: does the user have one? Free tier is sufficient.
- **Web search service**: Brave Search API, Tavily, or Serper — which is preferred? (Tavily has a native LangChain integration; Brave is cheaper.)
- **ENOA coordinate provenance**: the `top`/`left` values in the corpus appear to be a custom 2D embedding derived from playlist co-occurrence. Where do these come from for *new* tracks not in the corpus? They would need to be computed or estimated.
- **Corpus staleness**: the corpus tracks are from ~2012-2020s range. For newly released tracks, neither ENOA nor classifiers apply. Is a fallback to `/recommendations` or a "pure audio cosine" path acceptable?
- **Multi-turn memory scope**: should the agent remember "user prefers zouk recommendations" across sessions, or is in-context sufficient?

---

## Recommendation

**Recommender system (Phase 2 post-launch)**: The current design is solid. One high-value addition before Phase 3 is exposing Spotify's `/recommendations` as an agent tool — this gives the agent a fallback for tracks/artists not in the corpus and a basis for "what does Spotify think vs. what do I think?" comparisons.

**RAG (Phase 4)**: Use lazy ChromaDB ingestion with Wikipedia as primary and Last.fm as fallback. A single `"artist_info"` collection with artist metadata filter is simpler than per-artist collections. Add a web search tool (Tavily recommended — native LangChain integration, reasonable free tier) for recency queries ("what has X been up to lately?").

**Agent tools worth adding in Phase 3/4** beyond what PLAN.md specifies:
1. `get_artist_context(artist_name)` — RAG retrieval from ChromaDB + Wikipedia/Last.fm
2. `get_spotify_recommendations(seed_tracks, target_features)` — wraps `/recommendations`
3. `get_related_artists(artist_id)` — wraps `/artists/{id}/related-artists`
4. `web_search(query)` — Tavily or Brave for recency
