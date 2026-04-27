---
title: Agent Memory Types
tags: [memory, langgraph, concept]
summary: Three-tier memory taxonomy (semantic/episodic/procedural) with storage patterns, context window strategies, reflection pattern, and SQLite preference store for VA agents — backed by LangGraph BaseStore.
updated: 2026-04-26
sources:
  - raw/playground-docs/agentic-rag-copilot-research.md
  - raw/playground-docs/librarian-components.md
  - raw/claude-docs/listen-wiseer/docs/plans/phase4b_memory.md
  - raw/gdrive/2026-04-24-langgraph-yan.md
  - raw/claude-docs/playground/docs/research/agentic-ai/memory-architecture.md
---

# Agent Memory Types

## Three-Tier Memory Taxonomy (Cognitive Science Model)

Agents need three distinct memory types with different storage and retrieval patterns. Do not collapse these into a single "memory store."

| Tier | What it stores | Storage shape | Retrieval pattern | Update pattern |
|------|---------------|---------------|-------------------|----------------|
| **Semantic** | Facts, knowledge, entities | Profile (single JSON doc) or Collection (vector index) | Key lookup or semantic search | Upsert on new fact |
| **Episodic** | Past task records, conversation history, few-shot examples | Append-only log or vector index | Semantic search by similarity | Append only |
| **Procedural** | Rules, system prompt, tone, persona | Updatable prompt template | Direct load at session start | Rewrite on feedback |

### Semantic Memory — Two Sub-modes

**Profile mode** (single evolving document):
```python
store.put(("users", user_id), "profile", {
    "language": "da", "payment_method": "invoice",
    "preferred_contact": "email", "last_updated": "2026-04-26"
})
profile = store.get(("users", user_id), "profile").value
```

**Collection mode** — use when facts are too numerous for a single JSON doc. Each fact is a separate document; retrieval is semantic search. LangGraph `Store` is key-value only — for vector search, use an external store (Chroma, pgvector) and reference IDs from `Store`.

### Episodic Memory — Few-Shot Injection

```python
similar_episodes = vector_store.similarity_search(
    query=current_task, k=3, filter={"user_id": user_id}
)
few_shot_context = format_as_examples(similar_episodes)
# Prepend to system prompt or inject into context window
```

### Procedural Memory — Self-Updating System Prompts

Agents can rewrite their own instructions based on feedback (reflection pattern — see below):
```python
store.put(("agents", agent_id), "system_prompt", {
    "version": 7,
    "content": "You are a billing assistant for...",
    "updated_at": "2026-04-26",
    "updated_reason": "User corrected VAT calculation tone"
})
```

---

## The Four Types (LangGraph Mechanism View)

| Type | What it holds | Lifetime | LangGraph mechanism |
|---|---|---|---|
| **In-context** | Current messages, active task state, retrieved chunks | One session | `AgentState` + checkpointer |
| **Episodic** | Past conversation summaries per user | Days to weeks | `BaseStore` (cross-thread) |
| **Semantic** | User preferences, domain facts, entity knowledge | Persistent | `BaseStore` + vector retrieval |
| **Procedural** | Learned tool sequences, user shortcuts, prompt variants | Persistent | `BaseStore` (named templates) |

## Implementation Priority (for copilot)

1. **In-context** — already handled by LangGraph checkpointer. Done.
2. **Episodic** — add `BaseStore` + write session summary to store at `END` node. Cost: 1 Haiku call per session (~$0.0001). High ROI — enables "last time you asked about X..."
3. **Semantic** — extract entities from conversation, store in `BaseStore` vector namespace, retrieve relevant facts at `analyze` node.
4. **Procedural** — store approved action sequences. Lowest priority — requires enough usage data to learn patterns.

## Long-Term Memory Write Timing

When writing to `BaseStore`, choose based on latency requirements:

| Timing | When | Trade-off |
|---|---|---|
| **Hot path** | During the agent run, inside a node | Immediate — adds latency to the user-facing response |
| **Background** | Async task spawned after the run completes | No latency impact, slight delay before memory is available |

Prefer background writes for session summaries and episodic store updates. Use hot path only when the memory is needed within the same run (e.g. procedural memory update that affects the current response).

## LangGraph `BaseStore` (0.4+)

See [[LangGraph BaseStore]] for full detail.

```python
from langgraph.store.memory import InMemoryStore
from langgraph.store.postgres import AsyncPostgresStore

# Development
store = InMemoryStore()

# Production
store = AsyncPostgresStore.from_conn_string(settings.database_url)

# Compile with store attached
graph = graph.compile(checkpointer=checkpointer, store=store)
```

### Accessing from nodes

```python
async def retrieve_node(state: AgentState, config: RunnableConfig) -> AgentState:
    store = config["store"]
    # Read episodic memory for this user
    memories = await store.asearch(
        namespace=("user", state["user_id"], "memories"),
        query=state["query"],
        limit=3,
    )
    # Write new memory after session
    await store.aput(
        namespace=("user", state["user_id"], "memories"),
        key=f"session_{state['session_id']}",
        value={"summary": state["session_summary"], "timestamp": now()},
    )
```

`AsyncPostgresStore` uses the same Postgres instance as the checkpointer — no new infra required if Postgres is already in the stack.

## Short-Term Memory Schema

For MVP context management, the short-term memory schema:

```python
{
    "session_id": str,
    "conversation_history": list[dict],
    "tool_results": list[dict],
    "agent_state": dict,
    "artefact_refs": list[str],
    "turn_count": int
}
```

**Constraints:**
- Schema must be defined and frozen before any agent writes to it — retrofitting is expensive
- Compaction must write raw turns to cold storage (S3) before discarding — needed for GDPR audit trail
- `trace_id` is non-negotiable on every turn — without it observability is blind
- Sensitive data must never enter the LLM payload unredacted — redact at assembly time, not storage time

## SQLite Preference + Session Store (Lightweight Implementation)

For local dev and small deployments, a single SQLite table covers semantic (profile) and episodic (session summaries) memory:

```python
CREATE TABLE preference_store (
    user_id TEXT NOT NULL,
    key     TEXT NOT NULL,   -- "pref:language", "session:2026-04-26", "proc:system_prompt"
    value   TEXT NOT NULL,   -- JSON
    updated_at TEXT NOT NULL,
    PRIMARY KEY (user_id, key)
);
```

**Key namespacing:** `pref:*` = user preferences, `session:YYYY-MM-DD` = session summaries, `proc:system_prompt` = current instruction version.

**Production upgrade path:** swap SQLite for Postgres without changing calling code — same async interface.

---

## Reflection Pattern (Self-Improving Agents)

Agents can improve their own procedural memory based on user feedback signals.

**Hot-path reflection** (immediate, adds ~1–2s latency):
```
User message → Agent response → Reflection node → Update system prompt → Next turn
```

**Background reflection** (async, no latency impact — preferred for production):
```
User message → Agent response → [background task: Reflection → Update system prompt]
```

**Reflection trigger signals:** user explicitly corrects the agent, user overrides an action, low confidence score, negative rating.

```python
async def reflection_node(state: AgentState) -> dict:
    if not should_reflect(state):
        return {}
    current_prompt = await store.get(("agents", "billing"), "system_prompt")
    updated = await llm.ainvoke(
        f"Given this correction: {state['last_correction']}\n"
        f"Update this system prompt:\n{current_prompt.value['content']}"
    )
    await store.put(("agents", "billing"), "system_prompt", {
        "version": current_prompt.value["version"] + 1,
        "content": updated.content,
        "updated_at": date.today().isoformat(),
    })
    return {"reflection_applied": True}
```

---

## Memory Loading Pattern at Turn Start

Load all three tiers at the start of each turn before routing:

```python
async def load_memory_node(state: AgentState, store: BaseStore) -> dict:
    user_id = state["user_id"]
    prefs  = await store.aget(("users", user_id), "profile")
    session = await store.aget(("users", user_id), f"session:{date.today().isoformat()}")
    system  = await store.aget(("agents", "billing"), "system_prompt")
    return {
        "user_prefs": prefs.value if prefs else {},
        "session_context": session.value if session else {},
        "system_prompt": system.value["content"] if system else DEFAULT_PROMPT,
    }
```

---

## Context Window Management

### History Pruning (from ADK samples)

`shared/tools/history_pruning.py` pattern — removes prior tool responses before each LLM call:
- Keeps: user messages + agent text + current turn tool calls
- **Neither rag_poc nor playground has this.** Long sessions accumulate full tool history.

### Summarization Node

See [[Summarization Node]] for full detail. 8-message trigger, 4-message overlap. Separate summarizer model call (Haiku) for cost. Preserves factual state across compaction.

```
trigger: len(messages) >= 8
overlap: keep last 4 messages after compaction
model: Haiku (cost-efficient, targeted)
```

## ADK vs LangGraph: State Access

| | ADK | LangGraph |
|---|---|---|
| Mechanism | Mutable dict via `ToolContext.state` | Typed TypedDict passed through nodes |
| Scope | Shared across all agents in a session | Per-node return dicts, merged by LangGraph |
| Type safety | None | Full (TypedDict schema is the contract) |
| Multi-agent propagation | `session.state` survives agent transitions | Checkpointer handles cross-turn persistence |

**ADK multi-agent auth gotcha:** `asyncio.create_task()` copies a context snapshot — `ContextVar` mutations after creation are invisible to child tasks. Use `session.state` as the primary auth channel for multi-agent, not `ContextVar`.

## Langmem — Practical Memory Tools

`langmem` wraps the `BaseStore` patterns above into agent-ready tools:

```python
from langmem import create_manage_memory_tool, create_search_memory_tool

namespace = ("enoa", "{langgraph_user_id}", "taste")
manage_memory_tool = create_manage_memory_tool(namespace=namespace)
search_memory_tool  = create_search_memory_tool(namespace=namespace)
# Add to ALL_TOOLS — agent decides when to call them
```

**Episodic store** (past sessions as few-shots):

```python
# InMemoryStore with local sentence-transformers (no OpenAI dep)
store = InMemoryStore(index={"embed": "sentence-transformers:all-MiniLM-L6-v2"})

# In agent_node: retrieve 2 most similar past sessions, inject as examples
memories = store.search(("enoa", user_id, "sessions"), query=user_request, limit=2)
# After successful recommendation:
store.put(("enoa", user_id, "sessions"), key=session_id, value={...})
```

**Procedural memory** (per-user system prompt evolution):

```python
# Namespace: ("enoa", user_id, "strategy")
# get_procedural_prompt() → prepend to system prompt or fall back to default
# update_procedural_prompt() → overwrite with new instructions
```

**Background optimizer** (Sonnet, not on hot path):

```python
from langmem import create_multi_prompt_optimizer

optimizer = create_multi_prompt_optimizer(
    model="anthropic:claude-sonnet-4-6", kind="metaprompt"
)
# Call async after session ends (asyncio.create_task) — don't block user response
optimizer.invoke({"trajectories": [...], "prompts": [current_prompt]})
```

**Memory stats in prompt** — tells the agent what it knows before responding:
```
"You have 3 past sessions on record. 2 taste facts stored."
```
Mirrors MemGPT's memory statistics pattern. Inject as `<memory_stats>` block in system prompt.

**Redis checkpointer gate:**
```python
if settings.redis_url:
    checkpointer = AsyncRedisSaver(...)
    await checkpointer.setup()
else:
    checkpointer = MemorySaver()  # dev: in-process only
```

## Store Operations Reference

```python
store.put(("user-123", "facts"), "location", {"city": "Copenhagen"})  # Put
item = store.get(("user-123", "facts"), "location")                    # Get → item.value
results = store.search(("user-123", "facts"), filter={"city": "Copenhagen"})  # Filter search
store.delete(("user-123", "facts"), "location")                        # Delete
```

In nodes, access via `runtime.store` (Deep Agents) or `config["store"]` (plain LangGraph). Do NOT capture the store instance in a closure — always access via the runtime/config parameter.

## Deep Agents Memory Backends

For Deep Agents, memory is surfaced through pluggable backends rather than direct `BaseStore` access. See [[Deep Agents Memory Backends]] for the `StateBackend` / `StoreBackend` / `CompositeBackend` pattern.

## See Also
- [[LangGraph CRAG Pipeline]]
- [[ADK Context Engineering]]
- [[LangGraph Advanced Patterns]]
- [[Listen-Wiseer Project]]
- [[Deep Agents Memory Backends]]
- [[LangGraph BaseStore]]
- [[Self-Learning Agents]]
- [[Chain of Thought]]
