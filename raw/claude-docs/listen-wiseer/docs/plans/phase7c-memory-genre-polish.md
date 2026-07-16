# Phase 7c — Genre Lineage, Taste Analysis, Cross-session Memory

**Status:** PLANNED
**Depends on:** Phase 7b ✓
**Scope:** ~5 hours

---

## Goal

Three complementary improvements that complete the Phase 7 arc:
1. **Genre lineage queries** — structured Tavily queries that return genre history, parent/child genre relationships, and geographic origins rather than generic artist bios.
2. **Taste analysis with time ranges** — a new agent capability that compares `short_term` vs `long_term` top tracks/artists to surface drift, consistency, and emerging obsessions.
3. **Cross-session memory** — swap `InMemoryStore` → `AsyncPostgresStore` (or SQLite fallback for dev) so taste memories and episodic history survive server restarts.

---

## Current state

**Genre queries:** `get_artist_context_tool` in `spotify_read.py` calls `_tavily_search(f"{query} music history and context")` — generic, not structured for genre lineage. Query "what is bossa nova?" hits the same path as "tell me about Radiohead".

**Taste analysis:** Phase 7a added `get_top_tracks` and `get_top_artists` with `time_range` param. The agent can call them, but there's no tool that explicitly compares across time ranges — the LLM would have to make 2-3 tool calls and synthesise the delta itself. This works but isn't guided.

**Cross-session memory:**
```python
# agent/memory_store.py
store = InMemoryStore()  # wiped on every restart
```
`InMemoryStore` lives in `langgraph`. Taste memories, procedural notes, and episodic history all vanish on process restart. Dev penalty is low; prod penalty is high.

---

## What changes

### Step 1 — Genre-aware Tavily query builder (`agent/tools/spotify_read.py`)

Add a `_genre_context` function separate from `_get_artist_context`:

```python
def _get_genre_context(genre: str) -> str:
    """Fetch genre history, origins, key artists, and subgenres."""
    query = (
        f"{genre} music genre: origins, history, defining characteristics, "
        f"key artists, related subgenres"
    )
    return _tavily_search(query)
```

Add `get_genre_context_tool` as a `StructuredTool` with schema `{genre: str}`.

Update `_INTENT_TOOL_HINTS["genre_info"]` in `nodes.py` to prefer `get_genre_context` over `get_artist_context` for genre queries.

Add to `ALL_TOOLS` in `__init__.py` (count goes 18 → 19). Update `test_all_tools_count`.

### Step 2 — Taste drift tool (`agent/tools/spotify_read.py`)

Add `_get_taste_analysis` that calls `get_top_artists` for both `short_term` and `long_term`, then returns a structured comparison:

```python
def _get_taste_analysis() -> str:
    """Compare short-term vs long-term top artists to surface taste drift."""
    short = _get_client().get("me/top/artists", time_range="short_term", limit=10)
    long_ = _get_client().get("me/top/artists", time_range="long_term", limit=10)
    short_names = {a["name"] for a in short.get("items", [])}
    long_names = {a["name"] for a in long_.get("items", [])}
    new = short_names - long_names
    stable = short_names & long_names
    fading = long_names - short_names
    ...  # format as readable summary
```

Add `get_taste_analysis_tool` (no params). Add to `ALL_TOOLS` (count 19 → 20). Update `test_all_tools_count`.

Update `_INTENT_TOOL_HINTS["explore_my_taste"]` to include `get_taste_analysis` as primary option for drift queries.

### Step 3 — Postgres store (`agent/memory_store.py`)

Replace `InMemoryStore` with an async Postgres or SQLite store, with env-based switching:

```python
from langgraph.store.postgres import AsyncPostgresStore
from langgraph.store.memory import InMemoryStore

def get_store() -> BaseStore:
    db_url = settings.memory_store_url  # new setting
    if db_url:
        return AsyncPostgresStore.from_conn_string(db_url)
    return InMemoryStore()
```

Add `MEMORY_STORE_URL` to `utils/config.py` settings (optional, defaults to `None` → in-memory).
Add `MEMORY_STORE_URL=` to `.env.example` with a comment.

For dev, SQLite-backed store works via `sqlite+aiosqlite:///./data/memory.db`.

The `get_checkpointer()` pattern in `agent/dependencies.py` already handles async Postgres for the checkpoint store — follow the same pattern.

### Step 4 — Memory persistence test

Add `tests/unit/test_memory_store.py`:
- `test_get_store_returns_in_memory_without_url` — with `MEMORY_STORE_URL` unset
- `test_get_store_returns_postgres_with_url` — with a mock URL, verify type
- These are import/config tests, no real DB connections

### Step 5 — Update Chainlit welcome message

The current welcome lists 4 capabilities. Add the taste analysis and genre lineage prompts:
```
- **Explore your taste** — *"how has my music taste changed over time?"*
- **Genre deep dives** — *"tell me about the origins of bossa nova"*
```

### Step 6 — CLAUDE.md + memory file update

- CLAUDE.md: update Phase 7 row to `✓ DONE`, add Phase 8 placeholder
- `memory/project_listen_wiseer.md`: update phase status, add `MEMORY_STORE_URL` note to gotchas

---

## Acceptance criteria

- [ ] `get_genre_context_tool` returns genre-specific structured output (origins, key artists, subgenres) distinct from artist bio output
- [ ] `get_taste_analysis_tool` returns a human-readable drift summary (new obsessions, stable staples, fading interests)
- [ ] `get_store()` returns `InMemoryStore` without `MEMORY_STORE_URL`; returns `AsyncPostgresStore` with it set
- [ ] Taste memories persist across simulated restart (integration test with SQLite store)
- [ ] `test_all_tools_count` updated to 20
- [ ] Chainlit welcome message updated
- [ ] At least 6 new unit tests green

---

## Files touched

| File | Change |
|------|--------|
| `src/agent/tools/spotify_read.py` | Add `_get_genre_context`, `get_genre_context_tool`, `_get_taste_analysis`, `get_taste_analysis_tool` |
| `src/agent/tools/__init__.py` | Add 2 new tools; update count to 20 |
| `src/agent/nodes.py` | Update hints for `genre_info`, `explore_my_taste` |
| `src/agent/memory_store.py` | Replace `InMemoryStore` with env-switched store |
| `src/utils/config.py` | Add `memory_store_url: str | None = None` |
| `.env.example` | Add `MEMORY_STORE_URL=` |
| `src/app/main.py` | Update welcome message |
| `tests/unit/test_memory_store.py` | New — 4+ tests |
| `tests/unit/agent/test_tools.py` | Update `test_all_tools_count` to 20 |
| `CLAUDE.md` | Phase 7 → ✓ DONE |

---

## Out of scope

- Redis store (Postgres is simpler for a single-user app; Redis adds infra)
- Genre graph / taxonomy DB (full lineage trees) — Tavily is good enough for the use case
- Chainlit card components for track display — deferred to a UI polish pass
- Multi-user auth (Spotify user isolation) — single-user app for now
