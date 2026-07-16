---
name: langgraph
description: >
  VA project-specific LangGraph context — extends global LangGraph patterns with
  this project's graph topology, AgentState schema, MCP backends, and test conventions.
  Use for any work in va-langgraph/: adding a domain subgraph, new node, routing change,
  checkpointer config, HITL gate, streaming, or FastAPI gateway work. Also triggers when
  wiring MCP tools or adding a new domain to the intent router.
wiki:
  - wiki/concepts/langgraph-crag-pipeline.md
  - wiki/concepts/langgraph-advanced-patterns.md
  - wiki/concepts/langgraph-state-reducers.md
  - wiki/concepts/production-hardening-patterns.md
  - wiki/concepts/agent-memory-types.md
  - wiki/concepts/hitl-annotation-pipeline.md
  - wiki/concepts/framework-selection.md
updated: 2026-04-29
---

# LangGraph — VA Agent

## Project context

**Stack:** `va-langgraph/` — LangGraph StateGraph, Gemini 2.5 Flash, Postgres checkpointing, FastAPI gateway.

**MCP backends:**
- `mcp_servers/product-a/` — product-a billing API (invoices, quotes, customers, products, banking, expenses)
- `mcp_servers/corpus-a/` — vendor-a CRM backend (contacts, accounting, email, invitations)

**Graph topology:**
```
START → guardrail → analyze → [domain subgraph] → format → END
                 ↘ blocked → END
                              ↘ direct → END   (out-of-domain / low confidence)
                              ↘ memory → END   (preference save)
                              ↘ escalation → END
```

**Domain subgraphs** (each in `graph/subgraphs/domains.py`):
`invoice`, `quote`, `customer`, `product`, `email`, `invitation`, `insights`, `expense`, `banking`, `accounting`, `support`

**`AgentState` fields** (`graph/state.py`):
```python
messages: Annotated[list[BaseMessage], add_messages]
session_id: str
user_id: str
page_url: str | None
user_preferences: list[dict[str, str]]   # loaded at turn start via memory_load
intent: str | None
routing_confidence: float
tool_results: list[dict[str, Any]]       # accumulated across tool calls
response: dict | None                    # serialised AssistantResponse
blocked: bool
block_reason: str | None
```

**Checkpointer:** `MemorySaver` in dev/tests; `AsyncPostgresSaver` for production Fargate.

---

## Before You Build

Answer these before touching the graph. Write answers as a short design note — they become the PR description.

**Routing**
- Which intent label routes to this feature? Does it need a new entry in `_DOMAIN_NODES`?
- Is confidence threshold handling correct? (Below `_LOW_CONF_THRESHOLD` → `direct`, not your node.)

**State**
- What new fields does this add to `AgentState`? Type, reducer, serialisable for Postgres checkpointer?
- Are existing fields being repurposed? (Add a new field instead — repurposing breaks replay.)

**MCP tools**
- Which MCP backend(s) does this use? Which specific tool functions?
- Are the MCP tool schemas (Pydantic) already defined, or do they need adding?

**Topology**
- New domain subgraph (in `domains.py`) or extending an existing one?
- Where does it join/leave the main flow? Update `_DOMAIN_NODES` and `_route_intent` accordingly.

**Testing**
- New domain → new fixtures in `tests/evalsuite/fixtures/corpus-a_tickets.json`?
- Can the subgraph be unit-tested with a mock `AgentState` dict before wiring into the graph?

---

## Source of truth

Wiki pages are the canonical reference — read them before coding.
Key pages: [[LangGraph CRAG Pipeline]], [[LangGraph Advanced Patterns]], [[LangGraph State Reducers]], [[Production Hardening Patterns]].

---

## State design

- Always use `TypedDict` with explicit field types — never raw dicts
- `total=False` makes all fields optional; use it unless you have required fields that must always be present
- Messages field always uses `Annotated[list, add_messages]` — never plain `list`
- For parallel fan-out: accumulate lists with `Annotated[list, operator.add]`, not overwrite
- Keep state flat — avoid nested dicts inside state fields; they make reducers complex
- The TypedDict schema is the node contract — nodes return partial dicts, never mutate state directly

```python
class AgentState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    query: str
    intent: str
    retrieved_chunks: list[RetrievalResult]
    confidence_score: float
    confident: bool
    retry_count: int
    escalate: bool
```

---

## Node conventions

- Every node is an `async def` — even if it does no I/O today, it will
- Nodes return a partial dict of only the fields they update — nothing else
- Name nodes after what they do, not what they are (`condense_query` not `HistoryCondenserNode`)
- Wrap any blocking I/O in `asyncio.to_thread()` — CPU-bound inference, Chroma queries, DuckDB calls
- One responsibility per node — if a node does two distinct things, split it

```python
async def rerank(state: AgentState) -> dict:
    pairs = [(state["query"], c.text) for c in state["retrieved_chunks"]]
    scores = await asyncio.to_thread(cross_encoder.predict, pairs)
    ranked = sorted(zip(scores, state["retrieved_chunks"]), reverse=True)
    return {
        "reranked_chunks": [c for _, c in ranked],
        "confidence_score": float(ranked[0][0]) if ranked else 0.0,
    }
```

---

## Graph wiring

- Use `add_conditional_edges` with a dict mapping return values to node names — don't use lambdas inline
- `Command(goto=..., update={...})` for routing that also needs to write state
- Compile once, reuse the compiled graph — never recompile per request
- Subgraphs for independently testable pipelines; expose via `.as_node()` or pass the compiled graph directly

```python
def route_by_intent(state: AgentState) -> str:
    if state["intent"] == "conversational":
        return "generate"
    if state["intent"] == "lookup_simple":
        return "snippet_retrieve"
    return "retrieve"

graph.add_conditional_edges("plan", route_by_intent, {
    "generate": "generate",
    "snippet_retrieve": "snippet_retrieve",
    "retrieve": "retrieve",
})
```

---

## HITL

Two mechanisms — pick based on where the pause decision is made:

**Static breakpoints** — pause at a known node boundary:
```python
graph.compile(
    interrupt_before=["tool_executor"],
    checkpointer=checkpointer,
)
```

**Dynamic `interrupt()`** — pause inside a node when runtime state determines it:
```python
from langgraph.types import interrupt

async def review_node(state: AgentState) -> dict:
    draft = await generate_draft(state)
    approved = interrupt({"draft": draft, "prompt": "Approve this action?"})
    if not approved:
        return {"messages": [HumanMessage("Revise: rejected")]}
    return {"output": draft}
```

Resume always uses `Command(resume=...)`:
```python
await graph.ainvoke(Command(resume=True), config=thread_config)
```

Breakpoints require `checkpointer` — no checkpointer means no HITL.

---

## Checkpointer

| Backend | When to use |
|---|---|
| `MemorySaver` | Dev, unit tests — lost on restart |
| `AsyncSqliteSaver` | Local / single-instance — survives restarts |
| `AsyncPostgresSaver` | Production multi-instance Fargate |

Inject via config — never hardcode backend:
```python
def _build_checkpointer(cfg: Settings):
    if cfg.checkpoint_backend == "postgres":
        from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
        return AsyncPostgresSaver.from_conn_string(cfg.checkpoint_postgres_url)
    if cfg.checkpoint_backend == "sqlite":
        from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
        return AsyncSqliteSaver.from_conn_string(cfg.db_path)
    from langgraph.checkpoint.memory import MemorySaver
    return MemorySaver()
```

---

## Streaming

| Mode | Use for |
|---|---|
| `values` | Debug — full state snapshot after each node |
| `updates` | Progress indicators — state delta per node |
| `events` | UI streaming — token stream + tool activity |

```python
async for event in graph.astream_events(
    {"messages": [HumanMessage(message)]},
    config={"configurable": {"thread_id": session_id}},
    version="v2",
):
    if event["event"] == "on_chat_model_stream":
        yield f"data: {json.dumps({'type': 'token', 'content': event['data']['chunk'].content})}\n\n"
    elif event["event"] == "on_tool_start":
        yield f"data: {json.dumps({'type': 'tool_start', 'tool': event['name']})}\n\n"
```

---

## Production checklist

Before shipping any LangGraph service:

- [ ] Embedder warmup called in FastAPI lifespan before first request
- [ ] Checkpointer injected (not `MemorySaver`) for any stateful service
- [ ] `AsyncAnthropic(max_retries=3)` — no custom retry logic needed
- [ ] All blocking I/O wrapped in `asyncio.to_thread()`
- [ ] DuckDB write paths use a sync helper + `asyncio.to_thread` (single-writer lock)
- [ ] Chroma concurrent upsert protected by `asyncio.Lock()`
- [ ] Metadata filter keys validated against an allowlist before SQL interpolation
- [ ] `escalate` flag surfaced in API response for frontend handoff
- [ ] CORS origins explicit in production (not `"*"`)
- [ ] Fargate task memory covers loaded embedding model (4096 MiB for e5-large)

---

## Never do

- Never call `graph.compile()` inside a request handler — compile once at startup
- Never use `MemorySaver` in production — state is lost on restart
- Never mutate state in place inside a node — return a new partial dict
- Never use `operator.add` on messages — always `add_messages` (handles dedup and updates)
- Never run Chroma / DuckDB / cross-encoder calls directly in `async def` without `to_thread`
- Never pass the full `AgentState` to an LLM call — always extract only the needed fields

---

## See also (wiki)

- [[LangGraph CRAG Pipeline]] — full CRAG topology with state schema
- [[LangGraph Advanced Patterns]] — subgraphs, Send API, time-travel, streaming
- [[LangGraph State Reducers]] — parallel super-steps and reducer types
- [[Production Hardening Patterns]] — P0/P1/P2 checklist with code fixes
- [[ADK vs LangGraph Comparison]] — when to use each
