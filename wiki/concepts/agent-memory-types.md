---
title: Agent Memory Types
tags: [memory, langgraph, concept]
summary: Four memory types for agent systems — in-context, episodic, semantic, and procedural — and how to implement them with LangGraph BaseStore.
updated: 2026-04-24
sources:
  - raw/playground-docs/agentic-rag-copilot-research.md
  - raw/playground-docs/librarian-components.md
  - raw/claude-docs/listen-wiseer/docs/plans/phase4b_memory.md
---

# Agent Memory Types

## The Four Types

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

## See Also
- [[LangGraph CRAG Pipeline]]
- [[ADK Context Engineering]]
- [[LangGraph Advanced Patterns]]
- [[Listen-Wiseer Project]]
