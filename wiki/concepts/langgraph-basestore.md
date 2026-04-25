---
title: LangGraph BaseStore
tags: [langgraph, memory, concept]
summary: LangGraph's cross-thread persistent key-value store with optional vector search — the standard backend for episodic, semantic, and procedural agent memory.
updated: 2026-04-24
sources:
  - raw/playground-docs/librarian-stack-audit.md
  - raw/playground-docs/rag-agent-template-research.md
---

# LangGraph BaseStore

`BaseStore` is LangGraph's abstraction for persistent storage that survives across threads (conversations). Unlike checkpointers — which store per-thread state — BaseStore stores data shared across all threads for a given agent or user.

## What It Backs

The three persistent memory types all route through BaseStore:

| Memory type | What's stored | Scope |
|---|---|---|
| **Episodic** | Past conversation summaries per user | Per user, cross-thread |
| **Semantic** | User preferences, domain facts | Per user, searchable by embedding |
| **Procedural** | Learned tool sequences, prompt variants | Global or per-user |

In-context memory (current session state in TypedDict) does NOT use BaseStore — it lives in the checkpointer.

## Interface

```python
from langgraph.store.base import BaseStore

# Store a fact
store.put(namespace=("user", user_id), key="preference", value={"theme": "dark"})

# Retrieve exact key
item = store.get(namespace=("user", user_id), key="preference")

# Vector search (if store supports it)
results = store.search(namespace=("user", user_id), query="past investment advice", limit=5)
```

## Storage Backends

| Backend | Use case |
|---|---|
| `InMemoryStore` | Dev/testing — not persistent across restarts |
| `PostgresStore` | Production — persistent, supports vector search via pgvector |
| `RedisStore` | High-throughput — fast reads, optional vector search |

## Relationship to Checkpointer

| | Checkpointer | BaseStore |
|---|---|---|
| Scope | Single thread | Cross-thread |
| Contents | Full state snapshots | Specific facts/memories |
| Access | Automatic (LangGraph managed) | Explicit `store.get()` / `store.put()` |
| Time-travel | Yes | No |

## Langmem Integration

`langmem` is a wrapper library that builds agent-ready memory tools on top of BaseStore — `create_memory_store_manager()`, `create_search_memory_tool()`. Reduces boilerplate for the common patterns.

## See Also
- [[Agent Memory Types]]
- [[LangGraph Advanced Patterns]]
- [[Production Hardening Patterns]]
