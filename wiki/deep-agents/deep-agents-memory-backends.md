---
title: Deep Agents Memory Backends
tags: [deep-agents, memory, pattern]
summary: Pluggable backend system for Deep Agents file operations and memory — StateBackend (ephemeral), StoreBackend (cross-thread), FilesystemBackend (local disk), and CompositeBackend (routing).
updated: 2026-04-25
sources:
  - raw/agent-skills/deep-agents-memory/SKILL.md
---

# Deep Agents Memory Backends

## Backend Types

| Backend | Scope | Production Ready | Use For |
|---|---|---|---|
| `StateBackend` (default) | Thread-scoped | Yes | Temporary working files |
| `StoreBackend` | Cross-thread | Yes (with `PostgresStore`) | Long-term memory, user preferences |
| `FilesystemBackend` | Real disk | Local only | CLI tools, dev workflows |
| `CompositeBackend` | Routing | Yes | Mix ephemeral + persistent by path |

## StateBackend (Default)

Files live in thread state — lost when the thread ends. No setup required.

```python
agent = create_deep_agent()  # Default: StateBackend
# /draft.txt written in thread-1 is GONE when thread-1 ends
# /draft.txt is NOT visible to thread-2
```

## StoreBackend (Cross-Thread Persistence)

Files persist across threads and sessions via `Store`:

```python
from deepagents.backends import StoreBackend
from langgraph.store.memory import InMemoryStore  # dev
# from langgraph.store.postgres import AsyncPostgresStore  # prod

store = InMemoryStore()
agent = create_deep_agent(
    backend=lambda rt: StoreBackend(rt),
    store=store  # required
)
```

## FilesystemBackend (Local Dev Only)

Reads and writes real files on disk. Never use in web servers — restrict with `virtual_mode=True`:

```python
agent = create_deep_agent(
    backend=FilesystemBackend(root_dir=".", virtual_mode=True),  # restricts to root_dir
    interrupt_on={"write_file": True},
    checkpointer=MemorySaver()
)
```

## CompositeBackend (Hybrid Routing)

Routes different path prefixes to different backends. Longest prefix wins:

```python
store = InMemoryStore()
agent = create_deep_agent(
    backend=lambda rt: CompositeBackend(
        default=StateBackend(rt),       # /draft.txt → ephemeral
        routes={"/memories/": StoreBackend(rt)}  # /memories/*.txt → persistent
    ),
    store=store
)
```

Useful pattern: working files go to `StateBackend`, user preferences and notes go to `StoreBackend` under `/memories/`.

## Store Operations (in custom tools)

Access the store inside tools via `ToolRuntime`:

```python
from langchain.tools import tool, ToolRuntime

@tool
def save_preference(key: str, value: str, runtime: ToolRuntime) -> str:
    """Save a user preference."""
    runtime.store.put(("user_prefs",), key, {"value": value})
    return f"Saved {key}"

@tool
def get_preference(key: str, runtime: ToolRuntime) -> str:
    """Get a user preference."""
    result = runtime.store.get(("user_prefs",), key)
    return str(result.value) if result else "Not found"
```

## Production Notes

- Use `AsyncPostgresStore` instead of `InMemoryStore` for production
- `InMemoryStore` is lost on process restart
- `CompositeBackend` matches longest prefix — order the routes accordingly
- Path must include the prefix exactly: `/memories/prefs.txt` matches `/memories/` but `/prefs.txt` does not

## See Also

- [[Deep Agents Framework]]
- [[Agent Memory Types]]
- [[LangGraph BaseStore]]
