# Plan: Phase 3c — LangGraph Agent + Chainlit UI
Date: 2026-04-04 (revised)
Predecessor: Phase 3b (training pipeline)
Next: Phase 4a (RAG + artist context)

---

## Out of Scope

- **Spotify `/recommendations` endpoint** — Phase 4+
- **Last.fm API integration** — deferred; Wikipedia + web search covers the use case
- **Multi-session memory persistence** — `MemorySaver` is in-process only; Redis in Phase 4b
- **FAISS approximate nearest-neighbour** — 200ms scan acceptable for interactive use
- **Assigning ENOA coordinates to new tracks** — corpus tracks only
- **Docker / infra changes** — `infrastructure/` untouched
- **Spotify write operations** — agent recommends; does not write
- **Streaming token output in Chainlit** — `ainvoke` only; streaming is a follow-up
- **RAG (Wikipedia/Tavily/ChromaDB)** — Phase 4a
- **Related artists tool** — Phase 4a (requires new `fetch_related_artists` function)

---

## Goal

A working LangGraph ReAct agent wired into the Chainlit UI that can answer
questions about the user's Spotify listening history and produce content-based
recommendations from the corpus. RAG and artist-context tools are Phase 4a.

---

## Approach

Build bottom-up: tools as `StructuredTool` → ReAct graph → smoke test → Chainlit.

Key decisions:
- **`StructuredTool` wrapping** (direct Python calls) over `langchain-mcp-adapters` —
  zero process management, tests without a live MCP server
- **ReAct loop** (LLM → tools → LLM → ... → END) instead of single-pass —
  supports multi-step queries like "recommend based on my recent listening"
- **Messages-only state** — `AgentState` is just `{messages}`. Additional fields
  (`context_docs`, etc.) added in Phase 4 when RAG needs them
- **Lazy Spotify client** — singleton created on first Spotify tool call, not at
  module import

---

## Steps

### Step 2: Agent scaffold — `src/agent/`

**Files**: `src/agent/__init__.py` (new), `src/agent/state.py` (new),
`tests/unit/agent/__init__.py` (new), `tests/unit/agent/test_state.py` (new)

**What**: Create the agent package and define `AgentState` — the minimal shared
state dict that flows through every LangGraph node.

**Snippet**:
```python
# src/agent/state.py
from __future__ import annotations
from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
```

**Test**:
```python
# tests/unit/agent/test_state.py
from langchain_core.messages import HumanMessage
from agent.state import AgentState

def test_state_construction():
    state: AgentState = {"messages": [HumanMessage(content="hello")]}
    assert len(state["messages"]) == 1

def test_state_empty_messages():
    state: AgentState = {"messages": []}
    assert state["messages"] == []
```

**Run**: `uv run pytest tests/unit/agent/test_state.py -v`

**Done when**: `from agent.state import AgentState` succeeds; test passes.

---

### Step 3: `src/agent/tools.py` — StructuredTool wrappers

**Files**: `src/agent/tools.py` (new), `tests/unit/agent/test_tools.py` (new)

**What**: Wrap existing Python functions as `StructuredTool` objects. The agent's
LLM sees these via `bind_tools`. No MCP subprocess.

**Six tools for Phase 3c**:
1. `recommend_similar_tracks` — `engine.recommend(type="track")`
2. `recommend_for_artist` — `engine.recommend(type="artist")`
3. `recommend_by_genre` — `engine.recommend(type="genre")`
4. `recommend_for_playlist` — `engine.recommend(type="playlist")`
5. `get_recently_played` — `fetch_recently_played(client, limit)`
6. `search_tracks` — `SpotifyClient.search(query, limit)`

**Engine loading**: Module-level with `try/except` → `_engine = None`
(same pattern as `mcp_server/server.py`). Each recommend tool checks
`if _engine is None` and returns an explanatory string.

**Spotify client**: Lazy singleton via `_get_client()`:
```python
_client: SpotifyClient | None = None

def _get_client() -> SpotifyClient:
    global _client
    if _client is None:
        _client = SpotifyClient()
    return _client
```

**Result formatting**: `_format_result(result: RecommendResult) -> str` helper
(same logic as MCP server's `_format_result`).

**Tests** (mock engine + client — no pkl load or Spotify auth in unit tests):
```python
@patch("agent.tools._engine")
def test_recommend_similar_tracks_formats_result(mock_engine):
    ...

@patch("agent.tools._engine", None)
def test_recommend_engine_unavailable():
    ...

@patch("agent.tools._get_client")
def test_get_recently_played_formats_tracks(mock_get_client):
    ...
```

**Run**: `uv run pytest tests/unit/agent/test_tools.py -v`

**Done when**: All tool wrappers importable; unit tests pass with mocked deps.

---

### Step 4: ReAct graph — `src/agent/nodes.py` + `src/agent/graph.py`

**Files**: `src/agent/nodes.py` (new), `src/agent/graph.py` (new),
`tests/unit/agent/test_graph.py` (new)

**What**: Build a ReAct loop graph. The LLM decides when to call tools and when
to produce a final answer. Bounded by `settings.max_agent_iterations` via
`recursion_limit`.

**Graph structure**:
```
START → agent_node (LLM with tools bound)
    → [route_after_agent]
        → has tool_calls → call_tools (ToolNode) → agent_node  (loop)
        → no tool_calls  → END
```

No separate `synthesize` node — the LLM naturally produces a final answer when
it stops calling tools. System prompt carries persona + tool-use instructions.

**Routing function**:
```python
def route_after_agent(state: AgentState) -> str:
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "call_tools"
    return "__end__"
```

**Graph wiring**:
```python
def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("agent", agent_node)
    builder.add_node("call_tools", ToolNode(ALL_TOOLS))
    builder.add_edge(START, "agent")
    builder.add_conditional_edges(
        "agent", route_after_agent,
        {"call_tools": "call_tools", "__end__": END},
    )
    builder.add_edge("call_tools", "agent")  # loop back
    memory = MemorySaver()
    return builder.compile(
        checkpointer=memory,
        recursion_limit=settings.max_agent_iterations * 2,
    )
```

**Tests** (mock LLM — no API calls):
- `test_graph_direct_response` — no tool_calls → straight to END
- `test_graph_tool_then_response` — tool_calls → call_tools → agent → END
- `test_multiturn_memory` — two invocations same thread_id share history

**Run**: `uv run pytest tests/unit/agent/test_graph.py -v`

**Done when**: Graph builds; both test paths pass; `from agent.graph import graph` works.

---

### Step 5: End-to-end smoke test

**Prerequisite**: `make train` completed (classifiers in `models/`).

**Files**: None changed. Validation only.

**Manual smoke test**:
```bash
PYTHONPATH=src uv run python -c "
from langchain_core.messages import HumanMessage
from agent.graph import graph

result = graph.invoke(
    {'messages': [HumanMessage(content='Find me 5 tracks similar to bossa nova')]},
    config={'configurable': {'thread_id': 'smoke-1'}},
)
print(result['messages'][-1].content)
"
```

**Expected**: Final message contains a numbered track list or graceful explanation.

**Cost note**: 1-3 Anthropic API calls (~$0.01 at Haiku rates). Confirm before running.

**Done when**: Agent returns a real response; tool calls visible in message history.

---

### Step 6: Chainlit wiring — `src/app/main.py`

**Files**: `src/app/main.py` (replace echo stub)

**What**: Replace the echo stub with `graph.ainvoke`. Per-session thread ID via
`cl.user_session`. No streaming tokens (deferred).

**Snippet**:
```python
@cl.on_chat_start
async def start():
    thread_id = str(uuid.uuid4())
    cl.user_session.set("thread_id", thread_id)
    log.info("app.session_start", thread_id=thread_id)
    await cl.Message(content="Welcome to **listen-wiseer**! ...").send()

@cl.on_message
async def on_message(message: cl.Message):
    thread_id = cl.user_session.get("thread_id")
    config = {"configurable": {"thread_id": thread_id}}
    state = {"messages": [HumanMessage(content=message.content)]}
    try:
        result = await graph.ainvoke(state, config=config)
        reply = result["messages"][-1].content
    except Exception as exc:
        log.error("app.on_message.failed", error=str(exc), thread_id=thread_id)
        reply = "Something went wrong — please try again."
    await cl.Message(content=reply).send()
```

**Manual test**: `make app` → http://localhost:8000 → "recommend me some zouk tracks"

**Done when**: Chainlit UI starts; messages route through agent; multi-turn works.

---

## Test Plan

| Step | Test command | Verifies |
|------|-------------|----------|
| 2 | `uv run pytest tests/unit/agent/test_state.py -v` | AgentState construction |
| 3 | `uv run pytest tests/unit/agent/test_tools.py -v` | Tool wrappers, format, fail-soft |
| 4 | `uv run pytest tests/unit/agent/test_graph.py -v` | ReAct routing: direct + tool paths |
| 5 | Manual smoke (see above) | Live LLM + engine end-to-end |
| 6 | `make app` + manual | Chainlit → agent → response |

**Full regression after each step**: `uv run pytest tests/unit/ --tb=short -q`

---

## Risks & Rollback

### Step 3: Tool import fails if models missing
- **Mitigation**: `try/except` → `_engine = None`; each tool returns string
- **Rollback**: `git revert HEAD --no-edit`

### Step 4: ReAct loop runs away
- **Mitigation**: `recursion_limit` from config (`max_agent_iterations * 2`)
- **Rollback**: Lower `max_agent_iterations` in `.env`

### Step 4: MemorySaver thread_id collision in tests
- **Mitigation**: Unique `thread_id` per test (uuid4 or test name)

### Step 5: LLM doesn't call tools for genre queries
- **Mitigation**: Tune system prompt; explicit tool-use instructions
- **Rollback**: Prompt-only change in `nodes.py`

### Step 6: Sync tools block event loop in Chainlit
- **Mitigation**: LangGraph's ToolNode wraps sync calls via `run_in_executor`
- **Fallback**: Wrap with `asyncio.to_thread` if needed

### Global rollback
```bash
git revert HEAD~N..HEAD --no-edit
uv run pytest tests/unit/ --tb=short -q
```

---

## Dependency map

```
Step 2 (AgentState)
  ↓
Step 3 (tools.py) ← needs MODELS_DIR from paths.py (Phase 3b ✓)
  ↓
Step 4 (graph.py) ← needs Steps 2 + 3
  ↓
Step 5 (smoke test) ← needs Step 4 + trained models (Phase 3b ✓)
  ↓
Step 6 (Chainlit) ← needs Step 4
```

---

> **Phase 3c ends here. Phase 4a (RAG + artist context) follows.**
