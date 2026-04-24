# Plan: Phase 5b — Intent Routing + Query Understanding

Date: 2026-04-06 (rev 2)
Predecessor: Phase 5a (RAG core adaptation)
Next: Phase 5c (eval harness)

---

## Context & What Exists

`rag_core/orchestration/query_understanding.py` exists but is built for Danish
customer support (Danish keywords, intents: factual/procedural/exploratory/troubleshooting).
`rag_core/orchestration/router.py` has a `QueryAnalyzer` + `RoutingDecision` structure.

The current agent (`src/agent/nodes.py`) relies entirely on the LLM to pick the
right tool via ReAct reasoning — no explicit intent classification. This works for
simple queries but is unreliable for multi-step or ambiguous requests.

`rag_core/schemas/retrieval.py` defines `Intent` enum with `ARTIST_INFO`, `GENRE_INFO`,
`HISTORY`, `CHIT_CHAT`, `OUT_OF_SCOPE` — but is missing `RECOMMENDATION`. The enum
needs to be extended before `query_understanding.py` can reference it.

**Goal**: Add a lightweight intent router with safeguards to the agent graph:

1. **Pre-retrieval**: Classify intent, extract entities, expand queries. When
   confidence is low or the query is ambiguous, ask the user to clarify *before*
   committing to a tool path.
2. **Post-retrieval**: After tool execution, validate whether the result addresses
   the original query. If not, inject a corrective hint and allow one retry.

**Design principle**: The router is **a node in the agent graph**, not a separate
sub-graph. Intent is a **hint**, not a hard route — the ReAct agent makes the final
tool choice. Clarification and validation are lightweight guardrails, not blocking
gates.

---

## Out of Scope

- Spotify `/recommendations` API — Phase 6
- Full eval harness with trace-level metrics — Phase 5c
- Streaming / token-by-token responses — later
- Full CRAG retry loop — Phase 5c eval will determine if needed
- LLM-based intent classification — keyword-based is sufficient for now;
  Phase 5c eval will surface if upgrade is needed

---

## Updated Graph Topology

```
START
  → trim_history
  → classify_intent          (keyword, no LLM — fast)
  → [confidence < threshold?]
      → YES → clarify_or_proceed  (inject clarification AIMessage → END, wait for user)
      → NO  → rewrite_query       (Haiku coreference resolution, gated on pronoun detection)
              → agent              (ReAct with intent hint in system prompt)
              → [route_after_agent]
                  → call_tools → validate_tool_output → [ok?]
                      → YES → agent (loop continues)
                      → NO  → agent (retry with corrective hint, max 1 retry)
                  → __end__
```

---

## Steps

### Step 1: Extend Intent enum + music query understanding ✓ DONE — 2026-04-06

**Files**:
- `src/rag_core/schemas/retrieval.py` (add `RECOMMENDATION` to `Intent` enum)
- `src/rag_core/orchestration/query_understanding.py` (replace Danish patterns)
- `tests/unit/rag/test_query_understanding.py` (new)

**What**:

1. Add `RECOMMENDATION = "recommendation"` to `Intent` enum in `schemas/retrieval.py`.

2. Replace `query_understanding.py` internals. Keep `QueryAnalysis` dataclass and
   `QueryAnalyzer` class structure — replace all content:

**New intent patterns** (replace `INTENT_PATTERNS`):
```python
INTENT_PATTERNS: dict[str, dict[str, list[str]]] = {
    "artist_info": {
        "keywords": [
            "who is", "tell me about", "what do you know about", "biography",
            "history of", "background on", "artist info", "about the band",
            "when did", "where is", "discography", "influences", "style of",
        ],
    },
    "genre_info": {
        "keywords": [
            "what is", "explain", "describe", "genre", "subgenre", "music style",
            "what does", "characteristics of", "origins of",
        ],
    },
    "recommendation": {
        "keywords": [
            "recommend", "suggest", "find me", "similar to", "sounds like",
            "more of", "playlist", "tracks like", "what should i listen to",
            "based on", "fans of", "if i like", "like",
        ],
    },
    "history": {
        "keywords": [
            "recently played", "what have i been", "my listening", "my history",
            "i've been listening", "last week", "my taste", "my playlists",
            "what did i listen", "my spotify",
        ],
    },
    "chit_chat": {
        "keywords": [
            "hello", "hi", "hey", "thanks", "thank you", "bye", "how are you",
            "what's up", "good morning", "good night",
        ],
    },
}
```

Note: `"like"` and `"sounds like"` overlap between `genre_info` and `recommendation`.
Resolution: `recommendation` wins when `"similar"`, `"recommend"`, `"suggest"`, or
`"find me"` also appear. `genre_info` wins when `"what is"`, `"explain"`, `"genre"`
co-occur. Implement via scoring — the intent with the highest keyword hit count wins.
The existing scoring logic handles this naturally.

**Entity extraction** — replace `extract_entities()`:
```python
ENTITY_PATTERNS: dict[str, list[str]] = {
    "mood": ["happy", "sad", "energetic", "chill", "melancholic", "upbeat",
             "dark", "romantic", "mellow", "intense", "dreamy"],
    "time_period": ["70s", "80s", "90s", "2000s", "2010s", "recent",
                    "classic", "vintage", "new", "modern"],
    "context": ["workout", "study", "party", "sleep", "focus", "driving",
                "dinner", "cooking", "running", "relaxing"],
}
```

**Query expansion** — replace `expand_query()` with music synonyms:
```python
MUSIC_SYNONYMS: dict[str, list[str]] = {
    "track": ["song", "tune", "record"],
    "artist": ["musician", "band", "singer", "performer"],
    "similar": ["like", "sounds like", "in the style of", "reminiscent of"],
    "recommend": ["suggest", "find me", "show me"],
}
```

**Query decomposition** — replace Danish `"og"` splitting with English `"and"`:
```python
# Split on "and" with question-like patterns
if " and " in query_lower and any(k in query_lower for k in ("who", "what", "recommend")):
    parts = re.split(r"\s+and\s+", query, flags=re.IGNORECASE)
    ...
```

**Complexity terms** — replace Danish terms:
```python
COMPLEX_TERMS = [
    "compare", "difference between", "versus", "pros and cons",
    "best way to", "how does", "relationship between",
]
```

**Tests** (new file `tests/unit/rag/test_query_understanding.py`):
```python
# Intent classification
def test_classify_artist_info()        # "who is Aphex Twin?"
def test_classify_genre_info()         # "what is bossa nova?"
def test_classify_recommendation()     # "recommend me tracks similar to Boards of Canada"
def test_classify_history()            # "what have I been listening to?"
def test_classify_chit_chat()          # "hello!"
def test_classify_default_fallback()   # "asdfghjkl" → low confidence

# Entity extraction
def test_extract_mood_entity()         # "chill tracks for studying"
def test_extract_time_period()         # "80s rock"
def test_extract_context()             # "workout playlist"
def test_extract_no_entities()         # "who is Radiohead?"

# Query expansion
def test_expand_adds_synonyms()        # "find me songs similar to Radiohead"
def test_expand_no_match_passthrough() # "who is Aphex Twin?" → no expansion

# Decomposition
def test_decompose_multi_question()    # "who is Radiohead and what genre are they?"
def test_decompose_single_passthrough()# "who is Aphex Twin?" → [original]

# Confidence
def test_high_confidence_strong_match()  # multiple keyword hits → confidence > 0.5
def test_low_confidence_weak_match()     # no keyword hits → confidence ≤ 0.3
```

3. Clean up the `INTENT_MAP` bridge in `src/rag_core/orchestration/graph.py` (lines 41-46).
   The bridge maps old Danish intent strings (`"factual"`, `"procedural"`, etc.) to the
   `Intent` enum. After replacing `query_understanding.py`, the old strings no longer
   exist. Update the bridge to map the new intent strings directly:
   ```python
   INTENT_MAP: dict[str, Intent] = {
       "artist_info": Intent.ARTIST_INFO,
       "genre_info": Intent.GENRE_INFO,
       "recommendation": Intent.RECOMMENDATION,
       "history": Intent.HISTORY,
       "chit_chat": Intent.CHIT_CHAT,
   }
   ```
   Remove the `# Bridge mapping until Phase 5b` comment — it's no longer temporary.

**Run**: `uv run pytest tests/unit/rag/test_query_understanding.py -v`

**Done when**: Music intent classification works for all 5 intents + fallback.
INTENT_MAP bridge updated to use new intent strings.

---

### Step 2: Intent router + clarification node — add to agent graph ✓ DONE — 2026-04-06

**Files**:
- `src/utils/config.py` (add `intent_confidence_threshold` setting)
- `src/agent/state.py` (add `intent`, `intent_confidence`, `entities`, `query_variants` fields)
- `src/agent/nodes.py` (add `classify_intent_node`, `clarify_or_proceed` node, update system prompt)
- `src/agent/graph.py` (insert nodes, add conditional routing)
- `tests/unit/agent/test_intent_routing.py` (new)

**What**: Two new nodes before the ReAct agent:

1. `classify_intent` — keyword-based classification (no LLM). Populates
   `intent`, `intent_confidence`, `entities`, `query_variants` in state.
2. `clarify_or_proceed` — conditional routing based on confidence threshold.
   Below threshold → inject a clarification-requesting `AIMessage` and route to
   `__end__` (the user's next message re-enters the graph naturally — no
   `interrupt()` needed). Above threshold → pass through to `rewrite_query`.

**Config addition** (`utils/config.py`):
```python
# Intent routing
intent_confidence_threshold: float = 0.4
```

**AgentState additions** (`agent/state.py`):
```python
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    intent: str                  # "artist_info", "recommendation", etc.
    intent_confidence: float     # 0.0–1.0 from keyword classifier
    entities: dict               # {"mood": [...], "time_period": [...]}
    query_variants: list[str]    # expanded/decomposed query variants
```

**Important**: All new fields are accessed via `state.get("field", default)` throughout
the codebase — never `state["field"]`. LangGraph tolerates missing TypedDict keys at
runtime. This means existing tests that construct `{"messages": [...]}` continue to
work without modification. Add a test confirming backward compatibility.

**New nodes** (`agent/nodes.py`):

```python
from rag_core.orchestration.query_understanding import QueryAnalyzer

_query_analyzer = QueryAnalyzer()

_INTENT_TOOL_HINTS: dict[str, str] = {
    "artist_info": "Use get_artist_context to answer questions about this artist.",
    "genre_info": "Use get_artist_context with the genre name to get genre info.",
    "recommendation": "Use recommend_* tools based on the type of recommendation requested.",
    "history": "Use get_recently_played to fetch the user's listening history.",
    "chit_chat": "Respond directly without using tools.",
}


async def classify_intent_node(state: AgentState) -> dict:
    """Classify query intent and extract entities. No LLM call — pure keyword."""
    messages = state.get("messages", [])
    query = ""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            query = str(msg.content)
            break

    analysis = _query_analyzer.analyze(query)
    log.info(
        "agent.classify_intent",
        intent=analysis.intent,
        confidence=analysis.confidence,
        entities=analysis.entities,
        complexity=analysis.complexity,
    )
    return {
        "intent": analysis.intent,
        "intent_confidence": analysis.confidence,
        "entities": analysis.entities,
        "query_variants": analysis.sub_queries[:3],
    }


def route_after_classify(state: AgentState) -> str:
    """Route based on intent confidence: low → clarify, high → proceed."""
    confidence = state.get("intent_confidence", 0.0)
    intent = state.get("intent", "")

    # Chit-chat always proceeds (no clarification needed)
    if intent == "chit_chat":
        return "rewrite_query"

    if confidence < settings.intent_confidence_threshold:
        return "clarify_or_proceed"
    return "rewrite_query"


async def clarify_or_proceed(state: AgentState) -> dict:
    """Inject a clarification request when intent confidence is low.

    Returns an AIMessage asking the user to be more specific. The graph
    routes to __end__ after this node — the user's next message re-enters
    the graph with more context.
    """
    intent = state.get("intent", "unknown")
    entities = state.get("entities", {})
    query = ""
    for msg in reversed(state.get("messages", [])):
        if isinstance(msg, HumanMessage):
            query = str(msg.content)
            break

    # Build contextual clarification
    if entities:
        entity_hint = f" I can see you're interested in: {entities}."
    else:
        entity_hint = ""

    clarification = (
        f"I want to make sure I help you with the right thing.{entity_hint} "
        f"Could you clarify what you're looking for? For example:\n"
        f"- Info about an artist or genre? (e.g. \"who is Aphex Twin?\")\n"
        f"- Music recommendations? (e.g. \"recommend tracks like Boards of Canada\")\n"
        f"- Your listening history? (e.g. \"what have I been playing?\")"
    )
    log.info(
        "agent.clarify",
        intent=intent,
        confidence=state.get("intent_confidence", 0.0),
        query=query,
    )
    return {"messages": [AIMessage(content=clarification)]}
```

**System prompt injection** — update `agent_node` to include intent hint:
```python
# In agent_node, after building prompt_parts:
intent = state.get("intent", "")
entities = state.get("entities", {})
intent_hint = _INTENT_TOOL_HINTS.get(intent, "")
if intent_hint:
    intent_block = f"<query_classification>\nIntent: {intent}\n{intent_hint}"
    if entities:
        intent_block += f"\nExtracted entities: {entities}"
    intent_block += "\n</query_classification>"
    prompt_parts.append(intent_block)
```

**Graph update** (`agent/graph.py`):
```python
# Passthrough stub — Step 3 replaces with real coreference rewrite
async def _rewrite_query_stub(state: AgentState) -> dict:
    return {}

builder.add_node("classify_intent", classify_intent_node)
builder.add_node("clarify_or_proceed", clarify_or_proceed)
builder.add_node("rewrite_query", _rewrite_query_stub)  # stub until Step 3

builder.add_edge(START, "trim_history")
builder.add_edge("trim_history", "classify_intent")
builder.add_conditional_edges(
    "classify_intent",
    route_after_classify,
    {"clarify_or_proceed": "clarify_or_proceed", "rewrite_query": "rewrite_query"},
)
builder.add_edge("clarify_or_proceed", END)    # wait for user response
builder.add_edge("rewrite_query", "agent")
# ... rest unchanged
```

**Note**: `rewrite_query` is a passthrough stub in this step. Step 3 replaces
it with the real coreference resolution node. This allows Step 2 to be
independently testable and runnable.

**Tests** (new file `tests/unit/agent/test_intent_routing.py`):
```python
def test_classify_intent_node_populates_state()   # returns intent + entities + confidence
def test_classify_intent_node_artist()             # "who is Aphex Twin?" → artist_info
def test_classify_intent_node_recommendation()     # "suggest tracks like X" → recommendation

def test_route_after_classify_low_confidence()     # confidence < 0.4 → "clarify_or_proceed"
def test_route_after_classify_high_confidence()    # confidence > 0.4 → "rewrite_query"
def test_route_after_classify_chit_chat_always_proceeds()  # chit_chat → "rewrite_query" regardless

def test_clarify_or_proceed_returns_ai_message()   # returns AIMessage with clarification
def test_clarify_or_proceed_includes_entities()    # entities mentioned in clarification
```

**Run**: `uv run pytest tests/unit/agent/test_intent_routing.py -v`

**Done when**: Graph starts at `classify_intent`; low-confidence queries trigger
clarification; high-confidence queries proceed with intent hint in system prompt.

---

### Step 3: Query rewriting for multi-turn context ✓ DONE — 2026-04-06

**Files**:
- `src/agent/nodes.py` (add `rewrite_query` node)
- `src/agent/graph.py` (already wired in Step 2)
- `tests/unit/agent/test_intent_routing.py` (extend)

**What**: On multi-turn conversations, rewrite the query to be standalone
(resolve "it", "them", "that artist"). Single-turn queries pass through unchanged.
Uses the existing `_llm` (Haiku, shared with `agent_node`). Gated on coreference
signal detection — no LLM call when no pronouns detected.

**Node** (`nodes.py`):
```python
_COREFERENCE_SIGNALS = [
    " it ", " they ", " them ", " that ", " this ",
    "the artist", "the band", "the song", " their ",
]
# Space-padded to avoid matching inside words ("kizomita", "weather").
# Query is padded with spaces before checking: f" {query.lower()} "

async def rewrite_query(state: AgentState) -> dict:
    """Rewrite query as standalone if multi-turn with coreference signals.

    Reuses the module-level _llm (Haiku) — no separate instance needed.
    """
    messages = state.get("messages", [])
    if len(messages) <= 1:
        return {}  # single turn — no rewrite

    query = ""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            query = str(msg.content)
            break

    padded = f" {query.lower()} "
    if not any(signal in padded for signal in _COREFERENCE_SIGNALS):
        return {}  # no coreference — skip

    history = "\n".join(
        f"{'User' if isinstance(m, HumanMessage) else 'Assistant'}: {m.content}"
        for m in messages[-5:-1]
    )
    prompt = (
        "Rewrite the following question as a standalone question that doesn't "
        "require the conversation history to understand. Only output the "
        "rewritten question, nothing else.\n\n"
        f"History:\n{history}\n\n"
        f"Question: {query}\n\n"
        "Standalone question:"
    )
    # Reuse _llm (already Haiku via settings.anthropic_model), not _llm_with_tools
    response = await _llm.ainvoke([HumanMessage(content=prompt)])
    rewritten = str(response.content).strip()
    log.info("agent.rewrite_query", original=query, rewritten=rewritten)

    new_messages = list(messages[:-1]) + [HumanMessage(content=rewritten)]
    return {"messages": new_messages}
```

**Tests** (extend `test_intent_routing.py`):
```python
def test_rewrite_single_turn_passthrough()       # 1 message → returns {}
def test_rewrite_no_coreference_passthrough()    # "what genre is zouk?" → {}
def test_rewrite_fires_on_pronoun(mock_haiku)    # "tell me more about them" → calls Haiku
```

**Run**: `uv run pytest tests/unit/agent/test_intent_routing.py -v`

**Done when**: Rewrite fires on pronoun-bearing multi-turn; single-turn passes through.

---

### Step 4: Post-tool output validation node ✓ DONE — 2026-04-06

**Files**:
- `src/agent/nodes.py` (add `validate_tool_output` node)
- `src/agent/state.py` (add `tool_validation_retries` counter)
- `src/agent/graph.py` (insert between `call_tools` and `agent`)
- `tests/unit/agent/test_intent_routing.py` (extend)

**What**: After `call_tools` executes, validate the tool output before passing
back to the agent loop. This is **medium-weight** validation — no LLM call,
just heuristic checks that are cheap to compute:

1. **Empty/error check**: Tool returned empty string, error message, or
   "not found" / "unavailable" sentinel.
2. **Intent-output alignment**: The tool that ran matches the classified intent.
   e.g. if intent was `recommendation` but only `get_artist_context` ran,
   flag potential misroute.
3. **Entity coverage**: If entities were extracted (mood, genre), check whether
   the tool output references them.

When validation fails: inject a corrective `SystemMessage` hint into the
conversation and allow the agent one more iteration. Track retries via
`tool_validation_retries` in state to cap at 1 retry (prevent loops).

**State addition** (`agent/state.py`):
```python
tool_validation_retries: int  # 0 initially, max 1
```

**Config addition** (`utils/config.py`):
```python
max_tool_validation_retries: int = 1
```

**Node** (`nodes.py`):
```python
_TOOL_INTENT_MAP: dict[str, set[str]] = {
    "artist_info": {"get_artist_context"},
    "genre_info": {"get_artist_context", "recommend_by_genre"},
    "recommendation": {
        "recommend_similar_tracks", "recommend_for_artist",
        "recommend_by_genre", "recommend_for_playlist",
        "get_related_artists", "search_tracks",
    },
    "history": {"get_recently_played"},
}

_ERROR_SIGNALS = [
    "failed to fetch", "not found", "not available", "engine not available",
    "no results", "no recently played", "no tracks found",
]
# Note: bare "error" omitted — too broad, matches innocuous content like
# "critical error in the best way". The specific signals above are sufficient.


async def validate_tool_output(state: AgentState) -> dict:
    """Validate tool output against query intent. No LLM call.

    Checks:
    1. Tool returned non-empty, non-error content
    2. Tool aligns with classified intent
    3. Extracted entities appear in output (soft check)

    On failure: injects corrective hint, increments retry counter.
    On success or retry exhausted: passes through.
    """
    messages = state.get("messages", [])
    intent = state.get("intent", "")
    entities = state.get("entities", {})
    retries = state.get("tool_validation_retries", 0)
    max_retries = settings.max_tool_validation_retries

    # Find the most recent ToolMessage(s)
    tool_messages = []
    for msg in reversed(messages):
        if hasattr(msg, "type") and msg.type == "tool":
            tool_messages.append(msg)
        elif tool_messages:
            break  # stop at first non-tool message after collecting tools

    if not tool_messages:
        return {}  # no tool output to validate

    issues = []

    # Check 1: Empty or error output
    for tm in tool_messages:
        content = str(tm.content).lower()
        if not content.strip():
            issues.append("Tool returned empty output.")
        elif any(signal in content for signal in _ERROR_SIGNALS):
            issues.append(f"Tool may have failed: {tm.content[:100]}")

    # Check 2: Intent-tool alignment
    expected_tools = _TOOL_INTENT_MAP.get(intent, set())
    if expected_tools:
        used_tools = {tm.name for tm in tool_messages if hasattr(tm, "name")}
        if used_tools and not used_tools & expected_tools:
            issues.append(
                f"Intent was '{intent}' but tools used were {used_tools}. "
                f"Expected one of: {expected_tools}."
            )

    # Check 3: Entity coverage (soft — only log, don't fail)
    if entities and not issues:
        all_output = " ".join(str(tm.content).lower() for tm in tool_messages)
        missing_entities = []
        for entity_type, values in entities.items():
            for val in values:
                if val.lower() not in all_output:
                    missing_entities.append(f"{entity_type}:{val}")
        if missing_entities:
            log.debug(
                "agent.validate.entity_gap",
                missing=missing_entities,
                intent=intent,
            )

    if not issues or retries >= max_retries:
        if issues:
            log.warning(
                "agent.validate.issues_exhausted",
                issues=issues,
                retries=retries,
            )
        return {}  # pass through

    # Inject corrective hint
    hint = (
        f"[Validation] The previous tool output may not fully address the query. "
        f"Issues: {'; '.join(issues)} "
        f"Consider using a different tool or approach."
    )
    log.info("agent.validate.retry", issues=issues, retry=retries + 1)
    return {
        "messages": [SystemMessage(content=hint)],
        "tool_validation_retries": retries + 1,
    }
```

**Graph update** (`agent/graph.py`):
```python
builder.add_node("validate_tool_output", validate_tool_output)

# Replace: builder.add_edge("call_tools", "agent")
# With:
builder.add_edge("call_tools", "validate_tool_output")
builder.add_edge("validate_tool_output", "agent")
```

**Tests** (extend `test_intent_routing.py`):
```python
def test_validate_passes_on_good_output()        # non-empty, aligned → returns {}
def test_validate_catches_empty_output()          # empty tool message → corrective hint
def test_validate_catches_error_signal()          # "not found" → corrective hint
def test_validate_catches_intent_misalignment()   # intent=recommendation but tool=get_artist_context
def test_validate_respects_retry_cap()            # retries >= max → passes through
def test_validate_no_tool_messages_passthrough()  # no tool messages → returns {}
```

**Run**: `uv run pytest tests/unit/agent/test_intent_routing.py -v`

**Done when**: Validation catches empty/error outputs and intent misalignment;
retries are capped at 1.

---

### Step 5: Related artists tool ✓ DONE — 2026-04-06

**Files**:
- `src/spotify/fetch.py` (add `fetch_related_artists`)
- `src/agent/tools.py` (add `get_related_artists_tool`)
- `tests/unit/test_spotify_client.py` (extend)
- `tests/unit/agent/test_tools.py` (extend — update count to 10)

**What**: "Who sounds like Radiohead?" → `search_tracks` (get artist ID) →
`get_related_artists` → list of similar artists. Also referenced by the
validation node's `_TOOL_INTENT_MAP` under `recommendation`.

```python
# src/spotify/fetch.py — add:
def fetch_related_artists(client: SpotifyClient, artist_id: str) -> list[dict]:
    """Fetch up to 20 related artists for artist_id."""
    response = client.get(f"artists/{artist_id}/related-artists")
    artists = response.get("artists", [])
    log.info("spotify.fetch_related_artists", artist_id=artist_id, n=len(artists))
    return [
        {"id": a["id"], "name": a["name"], "genres": a.get("genres", [])[:3]}
        for a in artists
    ]

# src/agent/tools.py — add:
def _get_related_artists(artist_id: str) -> str:
    """Find artists similar to a given Spotify artist ID."""
    from utils.exceptions import SpotifyClientError  # lazy import — matches _search_tracks pattern

    try:
        artists = fetch_related_artists(_get_client(), artist_id)
        if not artists:
            return f"No related artists found for {artist_id}"
        return "\n".join(
            f"- {a['name']} ({', '.join(a['genres']) or 'unknown genre'})"
            for a in artists
        )
    except SpotifyClientError as exc:
        log.warning("tool.get_related_artists.failed", error=str(exc))
        return f"Failed to fetch related artists: {exc}"

get_related_artists_tool = StructuredTool.from_function(
    _get_related_artists,
    name="get_related_artists",
    description=(
        "Find artists that sound similar to a given Spotify artist ID. "
        "Use for 'who sounds like X?' or 'artists similar to X' queries. "
        "Requires a Spotify artist ID — use search_tracks first to find the ID."
    ),
)
ALL_TOOLS.append(get_related_artists_tool)  # now 10 tools
```

**Tests**:
```python
# tests/unit/test_spotify_client.py
def test_fetch_related_artists_happy_path()
def test_fetch_related_artists_empty()
def test_fetch_related_artists_truncates_genres()

# tests/unit/agent/test_tools.py
def test_all_tools_count_is_10()                   # update existing assertion
def test_get_related_artists_in_all_tools()
def test_get_related_artists_formats_output()
```

**Run**: `uv run pytest tests/unit/agent/test_tools.py tests/unit/test_spotify_client.py -v`

**Done when**: `ALL_TOOLS` has 10 tools; `fetch_related_artists` tested.

---

### Step 6: End-to-end validation

**Manual smoke** (run `make app`):

| # | Query | Expected flow |
|---|-------|--------------|
| 1 | `"who is Aphex Twin?"` | classify → `artist_info` (high conf) → agent → `get_artist_context` → bio |
| 2 | `"recommend me something similar"` (after #1) | classify → `recommendation` → rewrite → `"recommend something similar to Aphex Twin"` → `recommend_for_artist` |
| 3 | `"something chill"` | classify → low confidence → clarification → user clarifies → proceeds |
| 4 | `"who sounds like Radiohead?"` | classify → `recommendation` → `search_tracks` → `get_related_artists` |
| 5 | `"recommend zouk tracks"` | classify → `recommendation` → `recommend_by_genre` (regression check) |
| 6 | (empty tool result) | validate_tool_output → corrective hint → retry with different tool |

**Done when**: All 6 smoke queries behave as expected.

---

## Test Plan

| Step | Command | Verifies |
|------|---------|----------|
| 1 | `uv run pytest tests/unit/rag/test_query_understanding.py -v` | Music intent classification, entity extraction, expansion |
| 2 | `uv run pytest tests/unit/agent/test_intent_routing.py -v` | classify_intent, clarify, route logic |
| 3 | `uv run pytest tests/unit/agent/test_intent_routing.py -k rewrite -v` | Query rewrite |
| 4 | `uv run pytest tests/unit/agent/test_intent_routing.py -k validate -v` | Tool output validation |
| 5 | `uv run pytest tests/unit/agent/test_tools.py tests/unit/test_spotify_client.py -v` | Related artists tool |
| 6 | `uv run pytest tests/unit/ --tb=short -q` | Full regression |

---

## Dependency Map

```
Step 1 (query_understanding + Intent enum)
  ↓
Step 2 (classify_intent + clarify nodes + graph wiring)
  ↓
Step 3 (rewrite_query node) — needs Step 2 graph
  ↓
Step 4 (validate_tool_output node) — needs Step 2 state fields
  ↓
Step 5 (related artists tool) — independent of 1-4, but referenced by Step 4 _TOOL_INTENT_MAP
  ↓
Step 6 (smoke) — needs all steps
```

---

## Risks & Rollback

### Intent classification noise (Step 2)
- **Risk**: Keyword-based classification misroutes "what does zouk sound like?" as `artist_info`
- **Mitigation**: Hint injection is advisory — ReAct agent still makes final tool choice.
  Overlapping keywords resolved by highest-score-wins.
- **Rollback**: Remove `classify_intent` node; revert `set_entry_point`

### Clarification over-triggers (Step 2)
- **Risk**: Threshold too high → too many clarification prompts → annoying UX
- **Mitigation**: Threshold is configurable (`intent_confidence_threshold` in Settings).
  Start at 0.4 — adjust based on Phase 5c eval data. Chit-chat bypasses clarification.
- **Rollback**: Set threshold to 0.0 (effectively disables clarification)

### Query rewrite adds latency (Step 3)
- **Risk**: Every multi-turn query adds 1 Haiku call (~200ms)
- **Mitigation**: Gated on coreference signal detection; single-turn skips entirely
- **Rollback**: Remove `rewrite_query` from graph

### Validation false positives (Step 4)
- **Risk**: Validation flags good outputs as misaligned (e.g. `search_tracks` used
  as a stepping stone for `recommendation` intent)
- **Mitigation**: `_TOOL_INTENT_MAP` includes `search_tracks` under `recommendation`.
  Retry cap of 1 prevents loops. Entity check is soft (log-only, not a failure).
- **Rollback**: Remove `validate_tool_output` from graph; revert `call_tools → agent` edge

### `ALL_TOOLS` count grows (Step 5)
- **Risk**: More tools → more tokens in system prompt → LLM confused
- **Mitigation**: Tool descriptions are precise; intent hint focuses selection
- **Rollback**: Remove tool from `ALL_TOOLS`
