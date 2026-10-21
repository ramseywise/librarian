---
title: LangGraph BaseStore
tags: [langgraph, memory, concept]
summary: LangGraph's cross-thread persistent key-value store with optional vector search — the standard backend for episodic, semantic, and procedural agent memory.
updated: 2026-10-17
sources:
  - data/raw/articles/2026-07-19-long-term-agentic-memory-langgraph.md
  - data/raw/claude-docs/playground/docs/archived/librarian-stack-audit.md
  - data/raw/claude-docs/playground/docs/archived/rag-agent-template-research.md
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

## Namespace Design and Background Consolidation

- **Checkpointer = session memory; BaseStore = cross-session memory.** Confusing the two is
  the commonest architecture error.
- **Namespaces are the key design decision.** `(user_id, memory_type)` tuples partition
  per-user facts, per-conversation preferences and shared world knowledge in one store. A
  wrong namespace leaks across users (a privacy failure) or pollutes reasoning with another
  session's context.
- **Consolidate after the conversation, not during it.** A background node triggered on
  conversation completion extracts key facts and writes them to the store, so extraction
  never adds live latency (the same sleep-time pattern as
  [[MemGPT / Letta Virtual Context Memory]]'s consolidation, moved out of the turn).
- **With a vector-capable backend** (Postgres + pgvector, in-memory with numpy), personal
  memory becomes a private RAG store: retrieve from BaseStore and from the shared corpus,
  reason over both.

## See Also
- [[Agent Memory Types]]
- [[LangGraph Advanced Patterns]]
- [[Production Hardening Patterns]]
- [[MemGPT / Letta Virtual Context Memory]] — alternative-to (in-turn agent-managed paging vs post-session consolidation)
