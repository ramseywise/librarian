# Phase 7b — Intent Taxonomy Refactor + Chainlit UX

**Status:** PLANNED
**Depends on:** Phase 7a ✓
**Scope:** ~3 hours

---

## Goal

Two things in one phase:
1. Make the intent classifier aware of the two new intents (`explore_my_taste`, `discover`) that already have tool hints and suggestion templates but can never be reached because they're missing from `INTENT_PATTERNS`.
2. Wire `agent_response.suggestions` into Chainlit quick-reply chips and render `track_list` as formatted message elements so the UI reflects the structured data the agent already produces.

---

## Current state

Intent taxonomy in `query_understanding.py`:
```
artist_info | genre_info | recommendation | history | chit_chat  (5 intents)
```

`nodes.py` already defines hints + suggestion templates for `explore_my_taste` and `discover` — but `classify_intent()` never emits those values, so they're dead code.

`_TOOL_INTENT_MAP` in `nodes.py` has no entries for `explore_my_taste` or `discover`, so validate_tool_output() passes through silently (no expected_tools check).

`app/main.py` only sends `result["messages"][-1].content` as a raw string — `agent_response.suggestions` and `track_list` are computed but never used.

---

## What changes

### Step 1 — Add two intents to `INTENT_PATTERNS` (`query_understanding.py`)

Add keyword lists for:

**`explore_my_taste`**
```
"my top", "my favourite", "what do i like", "my taste", "my listening habits",
"what genres am i", "what kind of music am i", "my music profile",
"what artists do i love", "my vibe"
```

**`discover`**
```
"discover", "surprise me", "what else", "something new", "new music",
"what should i try", "expand my taste", "find me something different",
"i haven't heard", "outside my bubble", "underrated", "hidden gem"
```

Note: `history` already covers "my history", "recently played", "my listening" — `explore_my_taste` keywords should be distinct (affinity/taste rather than recency). Review for overlap before finalising.

### Step 2 — Expand `_TOOL_INTENT_MAP` (`nodes.py`)

```python
"explore_my_taste": {
    "get_top_artists",
    "get_top_tracks",
    "search_taste_memory",
    "manage_taste_memory",
},
"discover": {
    "get_spotify_recommendations",
    "get_related_artists",
    "get_top_artists",  # seeding
},
```

Also add `get_top_tracks` and `get_top_artists` to `history` (already covers `get_recently_played`, but taste-over-time queries hit these tools):
```python
"history": {"get_recently_played", "get_top_tracks", "get_top_artists"},
```

### Step 3 — Chainlit quick-reply chips (`app/main.py`)

`agent_response` is already populated on every non-interrupt response. Wire it:

```python
agent_resp = result.get("agent_response", {})
reply = agent_resp.get("message") or result["messages"][-1].content
suggestions = agent_resp.get("suggestions", [])
track_list = agent_resp.get("track_list", [])
```

Render quick-reply chips as inline action buttons:
```python
actions = [
    cl.Action(name=f"suggestion_{i}", label=s, payload={"query": s})
    for i, s in enumerate(suggestions[:3])
]
msg = cl.Message(content=reply, actions=actions if actions else None)
await msg.send()
```

Handle `cl.on_action` — on chip click, submit the suggestion text as a new user message.

### Step 4 — Track list rendering (optional / stretch)

If `track_list` is non-empty, append a formatted block below the main reply:
```python
if track_list:
    formatted = "\n".join(f"• {t}" for t in track_list)
    await cl.Message(content=f"**Tracks:**\n{formatted}", author="listen-wiseer").send()
```

Kept simple for now — no custom card elements yet.

### Step 5 — Update `route_after_classify` (`nodes.py`)

Current: routes `chit_chat` directly to `format_response`, everything else to `call_agent`. No changes needed for the new intents (they follow the normal tool-calling path), but confirm the routing table handles the expand to 7 cleanly.

### Step 6 — Update eval golden dataset

Add 5 golden examples covering the new intents:
- `explore_my_taste`: "what kind of music am I into?" → expects `get_top_artists` or `get_top_tracks`
- `discover`: "surprise me with something new" → expects `get_spotify_recommendations`
- `discover`: "find me artists outside my usual bubble" → expects `get_related_artists`

File: `tests/eval/golden_dataset.json`

### Step 7 — Unit tests

New test file: `tests/unit/test_query_understanding.py`
Cover:
- `classify_intent("what are my top artists?")` → `explore_my_taste`
- `classify_intent("discover something new for me")` → `discover`
- `classify_intent("what have I been listening to lately?")` → `history` (not `explore_my_taste`)
- No ambiguity regression: `recommendation`, `artist_info`, `genre_info` keywords still route correctly

---

## Acceptance criteria

- [ ] `classify_intent("my top artists")` returns `explore_my_taste`
- [ ] `classify_intent("discover something new")` returns `discover`
- [ ] `_TOOL_INTENT_MAP` has entries for `explore_my_taste` and `discover`
- [ ] Chainlit renders suggestion chips after agent replies (visible in UI test)
- [ ] No existing tests broken; at least 8 new tests green
- [ ] Eval golden dataset extended with 5 new examples

---

## Files touched

| File | Change |
|------|--------|
| `src/rag_core/orchestration/query_understanding.py` | Add `explore_my_taste`, `discover` to `INTENT_PATTERNS` |
| `src/agent/nodes.py` | Expand `_TOOL_INTENT_MAP`; expand `history` entry |
| `src/app/main.py` | Wire `suggestions` → Chainlit actions; wire `track_list` |
| `tests/unit/test_query_understanding.py` | New — 8+ tests |
| `tests/eval/golden_dataset.json` | Extend with 5 new examples |

---

## Out of scope

- Renaming `artist_info` → `explore_artist` or `genre_info` → `explore_genre` — these renames add churn without adding capability; defer unless eval reveals misclassification
- Rich card components (Chainlit Elements API) — Step 4 uses plain text; proper cards are Phase 7c polish
- HITL confirm gate for playlist writes — already shipped via `interrupt()` in `create_playlist_tool`
