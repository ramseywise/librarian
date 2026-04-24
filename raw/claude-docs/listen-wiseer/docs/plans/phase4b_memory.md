# Phase 4b — Long-Term Memory for ENOA

> Sources: "Long-Term Agentic Memory with LangGraph" (Langmem/Coursera) and
> "LLMs as Operating Systems: Agent Memory" (Letta/MemGPT, Coursera).
> These steps add persistent memory across sessions to the ENOA recommendation agent.

**Predecessor**: Phase 4a (LangGraph agent + Chainlit) — DONE
**Next**: Phase 5a (RAG + artist context)

---

## Pre-requisites (before Step 4.1)

### P0: Make `agent_node` async ✓ DONE — 2026-04-05

**Gap**: `nodes.py:65` calls `_llm_with_tools.invoke()` synchronously. LangGraph wraps it
via `run_in_executor` today, but Steps 4.2–4.5 add `await store.search()` /
`await store.put()` calls inside nodes. Those require native async nodes.

**Files**:
- `src/agent/nodes.py` — change `agent_node` to `async def`, use `await _llm_with_tools.ainvoke(messages)`

**Test**: existing `tests/unit/agent/test_graph.py` should still pass (LangGraph handles async nodes natively).

### P1: Wire `user_id` through Chainlit ✓ DONE — 2026-04-05

**Gap**: Steps 4.2–4.4 namespace memory by `langgraph_user_id` in config. Currently `main.py`
only sets `thread_id`.

**Files**:
- `src/app/main.py` — add `langgraph_user_id` to config dict. Use `settings.spotify_user_id`
  as default (single-user app). Can upgrade to per-session auth later.

### P2: Add `recursion_limit` to `build_graph` ✓ DONE — 2026-04-05

**Gap**: `graph.py` doesn't pass `recursion_limit` to `compile()` — only set via config in
`main.py:43`. Anyone calling `graph.invoke()` directly (smoke tests, scripts) misses it.

**Files**:
- `src/agent/graph.py` — add `recursion_limit=RECURSION_LIMIT` to `builder.compile()`

---

## Step 4.1 — History overflow: trim messages ✓ DONE — 2026-04-05

> Moved up from original Step 4.6 — long conversations hit context limits before memory
> features matter. Do this first.

**Gap** (from MemGPT course): no strategy for long sessions. Zouk/kizomba exploration sessions
can easily hit 20+ messages.

**What**: Add a `trim_history` node before the agent node. If message count > 20, apply
`trim_messages(strategy="last")`. Start with trim; upgrade to summarization if context loss
is visible in testing.

**Files**:
- `src/agent/nodes.py` — `def trim_history(state): return {"messages": trim_messages(...)}`
- `src/agent/graph.py` — insert trim node: `START → trim_history → agent → [route] → ...`
- `src/utils/config.py` — add `max_history_messages: int = 20`

**Test**: `tests/unit/agent/test_nodes.py` — 3 tests (under/over/at limit)

---

## Step 4.2 — Cross-session recall: Redis checkpointer ✓ DONE — 2026-04-05

**Gap**: `MemorySaver` — in-process only, lost on restart.

**What**: Replace `MemorySaver` with `AsyncRedisSaver`. Gate on config: `MemorySaver` when
`REDIS_URL` is empty (local dev), `AsyncRedisSaver` when set.

**Files**:
- `src/agent/graph.py` — conditional checkpointer based on `settings.redis_url`
- `src/agent/dependencies.py` (new) — lifespan management: `await saver.setup()` on startup,
  teardown on shutdown
- `src/utils/config.py` — add `redis_url: str = ""` and `redis_ttl_minutes: int = 1440`
- `.env.example` — add `REDIS_URL=redis://localhost:6379`
- `pyproject.toml` — `uv add langgraph-checkpoint-redis` (confirm before touching)

**Note**: Use direct constructor + `setup()`, not `from_conn_string` context manager.

**Multi-turn input**: Pass `{"messages": [HumanMessage(content=query)]}` not `initial_state()`.
LangGraph's `add_messages` reducer handles the merge.

**Test**: `tests/unit/agent/test_graph.py` — test that `build_graph()` returns a compiled graph
with both checkpointer paths (mock Redis connection).

---

## Step 4.3 — Episodic memory: past sessions as few-shots ✓ DONE — 2026-04-05

**What**: Store past recommendation sessions (user request + track list returned) and inject the
2 most similar past sessions as few-shot examples into the system prompt.

**Files**:
- `src/agent/memory_store.py` (new) — store factory:
  ```python
  from langgraph.store.memory import InMemoryStore
  # Use local sentence-transformers (already installed) — no OpenAI dependency
  store = InMemoryStore(index={"embed": "sentence-transformers:all-MiniLM-L6-v2"})
  ```
  If `InMemoryStore` doesn't support `sentence-transformers:` prefix, fall back to a custom
  `_embed_fn` using the model we already load for Track2Vec.
- `src/agent/graph.py` — compile graph with `store=store`
- `src/agent/nodes.py` — in `agent_node`, call
  `store.search(("enoa", user_id, "sessions"), query=user_request, limit=2)` and prepend
  results to system prompt as examples. After successful recommendation, `store.put(...)`.

**Namespace**: `("enoa", user_id, "sessions")` — scoped per user via
`config["configurable"]["langgraph_user_id"]` (wired in P1).

**Test**: `tests/unit/agent/test_memory_store.py` — `test_episodic_roundtrip`: put a session,
search with similar query, assert it's retrieved.

---

## Step 4.4 — Semantic memory: ENOA user taste profile ✓ DONE — 2026-04-05

**What**: Let the agent write and update facts about the user's taste across sessions
(e.g. "prefers zouk over kizomba", "dislikes electronic BPM > 140").

**Dependency**: `uv add langmem` — confirm compatibility with `langgraph>=1.0.10` before
installing.

**Files**:
- `src/agent/tools.py` — add `manage_memory_tool` and `search_memory_tool`:
  ```python
  from langmem import create_manage_memory_tool, create_search_memory_tool
  namespace = ("enoa", "{langgraph_user_id}", "taste")
  manage_memory_tool = create_manage_memory_tool(namespace=namespace)
  search_memory_tool = create_search_memory_tool(namespace=namespace)
  ```
- Add both to `ALL_TOOLS`
- Same `store` instance from Step 4.3

**Hot path**: semantic tools run while responding — adds ~200ms per turn with a tool call.
Acceptable for ENOA since recommendations are already slow (corpus scan + LLM).

**Test**: `tests/unit/agent/test_memory_store.py` — `test_taste_profile_update`: write a fact,
search for it, assert retrieval.

---

## Step 4.5 — Procedural memory: per-user recommendation strategy ✓ DONE — 2026-04-05

**What**: Store per-user system prompt instructions that evolve over time
(e.g. "always explain why this track fits the user's ENOA zone").

**Files**:
- `src/agent/memory_store.py` — add `get_procedural_prompt(user_id, store)` and
  `update_procedural_prompt(user_id, instructions, store)` helpers using `store.get`/`store.put`
  under namespace `("enoa", user_id, "strategy")`
- `src/agent/nodes.py` — prepend procedural instructions to system prompt at graph start;
  fall back to default ENOA system prompt if namespace is empty

**Test**: `tests/unit/agent/test_memory_store.py` — `test_procedural_fallback`: empty store
returns default prompt; populated store returns stored instructions.

---

## Step 4.6 — Background prompt optimizer ✓ DONE — 2026-04-05

**What**: A separate background agent (not in the hot path) reviews conversation trajectories
and feedback signals, then updates the procedural memory for each user.

**Files**:
- `src/agent/optimizer.py` (new):
  ```python
  from langmem import create_multi_prompt_optimizer
  optimizer = create_multi_prompt_optimizer(
      model="anthropic:claude-sonnet-4-6",
      kind="metaprompt",
  )
  ```
- Call `optimizer.invoke({"trajectories": [...], "prompts": [current_prompt]})` after a session
  ends or on a schedule; write result back to procedural memory store
- `src/agent/graph.py` — add `END` callback that triggers optimizer asynchronously
  (`asyncio.create_task`) so it doesn't block the user response

**Cost note**: Sonnet call per session end. Confirm before wiring live.

**Test**: `tests/unit/agent/test_optimizer.py` — mock optimizer; assert it's called with the
correct trajectory shape.

---

## Step 4.7 — Memory statistics in ENOA prompt ✓ DONE — 2026-04-05

**What**: Tell the agent how much it knows before it responds — "You have 3 past sessions on
record. 2 taste facts stored." Mirrors MemGPT's memory statistics in context.

**Files**:
- `src/agent/nodes.py` — in `agent_node`, query store for namespace counts;
  inject as a `<memory_stats>` block in the system prompt

**Test**: `tests/unit/agent/test_nodes.py` — `test_memory_stats_injected`: populated store
produces non-empty stats block in prompt.

---

## Execution order

```
P0 (async nodes) → P1 (user_id) → P2 (recursion_limit)
  → 4.1 (trim) → 4.2 (Redis) → 4.3 (episodic) → 4.4 (semantic)
  → 4.5 (procedural) → 4.6 (optimizer) → 4.7 (memory stats)
```

---

## Dependency additions (confirm before each)

| Step | Package | Notes |
|------|---------|-------|
| 4.2 | `langgraph-checkpoint-redis` | Only if Redis path taken |
| 4.4 | `langmem` | Check compat with `langgraph>=1.0.10` |

---

## Out of Scope (Phase 4b)

- **Letta framework** — MemGPT course uses Letta server + client SDK. We build on LangGraph +
  Langmem directly — same concepts, no Letta dependency needed.
- **Shared memory blocks across agents** — only one agent in Phase 4. If a separate eval or
  curator agent is added later, shared blocks become relevant.
- **HITL interrupt_before** — could be useful for ENOA ("confirm before adding to taste
  profile?"). Defer — adds friction in the v1 conversational flow.
- **Vector DB for memory store** (Postgres/pgvector) — `InMemoryStore` for dev; swap at deploy
  time.
- **Streaming token output** — `ainvoke` only; streaming is a follow-up.
- **Rate limiting on Spotify tool calls** — not a concern at single-user scale.

---
