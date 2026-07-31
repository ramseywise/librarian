---
title: Conversation Repository Pattern
tags: [rag, memory, pattern]
summary: Two-table PostgreSQL schema for persisting multi-turn conversation state — conversations table for sessions, messages table for turns with JSONB trace and sources columns enabling trace-linked retrieval debugging.
updated: 2026-07-06
sources:
  - raw/claude-docs/chat-agent/docs/architecture/conversation_repository.md
---

# Conversation Repository Pattern

A minimal, generic PostgreSQL schema for storing conversational agent sessions and their messages. Suitable for any chatbot or RAG agent where conversations span multiple turns and need to be recoverable across stateless worker instances.

---

## Schema

### `conversations` Table

Stores one row per chat session.

```sql
CREATE TABLE conversations (
    id         TEXT PRIMARY KEY,
    title      TEXT        NOT NULL DEFAULT 'New conversation',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

`id` is the session identifier — use the session token, user ID + timestamp hash, or any stable unique key from the application layer.

---

### `messages` Table

Stores all turns for all conversations.

```sql
CREATE TABLE messages (
    id              BIGSERIAL PRIMARY KEY,
    conversation_id TEXT        NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role            TEXT        NOT NULL CHECK (role IN ('user', 'assistant')),
    content         TEXT        NOT NULL,
    trace           JSONB       NOT NULL DEFAULT '[]',
    sources         JSONB       NOT NULL DEFAULT '[]',
    confidence      TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX messages_conv_idx ON messages (conversation_id, created_at);
```

---

## Key Design Decisions

### JSONB Trace Column

The `trace` column stores the agent's execution trace for each assistant response. This enables:

- **Post-hoc debugging:** Inspect which tools were called, in what order, with what inputs/outputs — without relying on an external observability platform
- **Langfuse linking:** Store the Langfuse trace ID in `trace` metadata, connecting the DB record to the full trace tree
- **RAG path analysis:** Determine whether a response used the happy path or CRAG correction from stored data

### JSONB Sources Column

The `sources` column stores the retrieved chunks that contributed to the response. Enables:

- **Source attribution UI:** Show users which help articles were used
- **Offline evaluation:** Re-run quality scoring on historical responses using the original retrieved context (without hitting the retrieval system again)
- **Retrieval regression detection:** Compare what was retrieved before and after a KB update for the same query

### `ON DELETE CASCADE`

Deleting a conversation automatically removes all its messages. Simplifies session cleanup — no orphaned message rows.

### Chronological Index

```sql
CREATE INDEX messages_conv_idx ON messages (conversation_id, created_at);
```

Supports the primary query pattern: fetch all messages for a conversation in order. Without this index, full-table scans on `messages` degrade as message volume grows.

---

## Query Patterns

```sql
-- Load a conversation (chronological order)
SELECT role, content, trace, sources, confidence, created_at
FROM messages
WHERE conversation_id = $1
ORDER BY created_at ASC;

-- List recent conversations
SELECT id, title, updated_at
FROM conversations
ORDER BY updated_at DESC
LIMIT 20;

-- Delete a conversation (cascades to messages)
DELETE FROM conversations WHERE id = $1;
```

---

## Relationship to Session State

This schema is a **persistence layer** — it stores the durable record of what happened. In-memory session state (active agent runners, pending tool calls) is separate and process-local. The DB allows any Cloud Run worker to resume a conversation without sticky sessions:

1. Client sends `conversation_id` with each request
2. Worker loads message history from DB
3. Reconstructs context window for the agent
4. Appends new user message and assistant response to DB after each turn

---

## See Also
- [[Memory Architecture for VA Agents]]
- [[Cloud Run + Cloud SQL Pattern]]
- [[PGVector Migration Pattern]]
- [[Agent Memory Types]]
- [[Langfuse ADK Tracing Patterns]]
