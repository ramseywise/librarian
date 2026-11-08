---
title: A2A Agent Protocol
tags: [mcp, infra, concept]
summary: Google's Agent-to-Agent open specification for inter-agent communication — task lifecycle, agent cards, and how it maps to LangGraph primitives.
updated: 2026-11-08
sources:
  - data/raw/claude-docs/playground/docs/archived/agentic-rag-copilot-research.md
  - data/raw/papers/2026-11-06-chen-2024-internet-agents.md
  - data/raw/papers/2026-11-06-ren-2025-anemoi.md
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

## Two research systems built on agent-to-agent messaging (self-reported)

- **Internet of Agents** (Chen et al., arXiv 2407.07061 v2, "work in progress"): a messaging layer where third-party agents join through client wrappers, discover each other, and hold group chats governed by a finite-state machine, with nested teams argued (by formula, not measurement) to cut channels. With a GPT-3.5 core on four retrieval QA sets, a two-agent homogeneous team scored 0.652 overall and a three-agent one 0.671 against 0.611 for GPT-4; the heterogeneous two-agent team scored 0.610 and lost on HotpotQA (0.478 against GPT-4's 0.566). Debate baselines scored 0.507 and 0.529, below single-model GPT-4. On 153 open-ended tasks (GPT-4 judge, order-swapped) it won 76.5% of comparisons with AutoGPT and 63.4% with Open Interpreter; on GAIA validation it scored 40.00 against AutoGen 39.39, with no variance. The communication layer cost $0.53 per task ($0.28 after the authors' manual removal of repeated text), more than either worker, and agents often restated earlier messages. The extraction notes the paper's own caption overstates the QA table and the introduction's "66 to 76%" does not match 63.4%.
- **Anemoi** (Ren et al., Coral Protocol, arXiv 2508.17068, vendor-authored preprint): a planner writes the initial plan, then agents coordinate over a thread-based server with a critique agent and a consensus vote. On GAIA validation at pass@3 with a GPT-4.1-mini planner and GPT-4o workers it scored 52.73% against 43.64% for a reproduced OWL (47.27% as originally reported). Its own error analysis credits 52% of its 25 unique wins to collaborative refinement and 40% to stochastic worker behaviour; 90% of the 10 OWL-only wins were stochastic. Level 3 was below OWL's original score, no ablation isolates the channel, critique or vote, no cost numbers are given, and a busy worker caused a deadlock-like loop in the appendix transcript. The authors did not try a GPT-4o-mini planner, judging it too weak to use the server's toolkits reliably, which the extraction reads as a capability floor for the protocol.

## See Also
- [[MCP Protocol]]
- [[LangGraph Advanced Patterns]]
- [[Librarian RAG Architecture]]
- [[Agent Interoperability Protocol Stack]] — related (part of; A2A's place alongside MCP, A2UI, AP2, and UCP)
- [[Coordination Network Measurement in Multi-Agent Coding]] — related (measured message traffic between agents)
- [[Aegean Stability-Horizon Consensus]] — related (consensus among agents)
- [[Agent Communication Protocol Taxonomy]] — related
