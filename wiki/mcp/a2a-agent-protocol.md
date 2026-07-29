---
title: A2A Agent Protocol
tags: [mcp, infra, concept]
summary: Google's Agent-to-Agent open specification for inter-agent communication — task lifecycle, agent cards, and how it maps to LangGraph primitives.
updated: 2026-04-24
sources:
  - raw/playground-docs/agentic-rag-copilot-research.md
---

# A2A Agent Protocol

Google published the A2A (Agent-to-Agent) open specification in April 2025. It defines how agents from different frameworks, vendors, and deployments communicate. For multi-agent systems where the Librarian is one node, A2A is the standard that makes each agent independently deployable and discoverable.

## Core Concepts

### Agent Card (`/.well-known/agent.json`)

```json
{
  "name": "librarian",
  "description": "RAG retrieval and Q&A over document corpus",
  "url": "https://your-service/a2a",
  "version": "1.0",
  "capabilities": {
    "streaming": true,
    "pushNotifications": true
  },
  "skills": [
    {
      "id": "query",
      "name": "Query knowledge base",
      "inputModes": ["text"],
      "outputModes": ["text", "data"]
    }
  ],
  "authentication": { "schemes": ["Bearer"] }
}
```

### Task Lifecycle

```
submitted → working → (input-required ←→ working) → completed | failed | cancelled
```

Tasks are long-lived. The caller can poll or receive a webhook. For SSE-streaming agents, `working` emits incremental updates.

**Message modalities:** text, files (base64 or URL reference), structured data (JSON) — not just strings. An agent can return a chart spec, a file download, or a Pydantic model.

## LangGraph ↔ A2A Mapping

| A2A concept | LangGraph equivalent |
|---|---|
| Task ID | `thread_id` (checkpointer key) |
| Task state | Checkpointer state at latest checkpoint |
| `input-required` | `interrupt()` (human-in-the-loop) |
| Streaming updates | `.astream_events()` → SSE |
| Push notification | Webhook callback after `END` node |

The mapping is natural. The main addition is an HTTP wrapper: a FastAPI endpoint that accepts A2A JSON-RPC requests and translates them into `graph.ainvoke()` or `graph.astream_events()` calls.

## Minimal Implementation

```
src/
  interfaces/
    a2a/
      agent_card.py    # Serve /.well-known/agent.json (static JSON from settings)
      router.py        # POST /a2a — parse A2A JSON-RPC, route to graph
      task_store.py    # Track task lifecycle (task_id → thread_id mapping)
      models.py        # Pydantic models for A2A request/response envelopes
```

**Approach:** don't implement the full spec up-front. Start with:
1. Agent Card served at `/.well-known/agent.json`
2. `POST /a2a` accepting `{"method": "tasks/send", "params": {...}}`
3. SSE streaming response for the `working` state
4. Webhook notification on task completion (optional)

**Python SDK:** `google-adk` 1.0+ includes A2A client/server support. For LangGraph agents, use the spec directly via FastAPI — no ADK dependency required.

## Why It Matters for Playground

Playground has three agents: researcher, presenter, cartographer. Currently they run in-process as CLI tools. A2A is the standard that makes each independently deployable and discoverable without tight coupling. With A2A:
- Each agent becomes a service with its own agent card
- The orchestrator discovers capabilities at runtime
- Protocol-safe composition across frameworks and vendors

**Priority:** implement after the base copilot is proven — items 1–4 (breakpoints, plan-and-execute, Send API, episodic memory) first.

## See Also
- [[MCP Protocol]]
- [[LangGraph Advanced Patterns]]
- [[Librarian RAG Architecture]]
