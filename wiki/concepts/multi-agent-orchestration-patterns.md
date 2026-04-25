---
title: Multi-Agent Orchestration Patterns
tags: [adk, langgraph, deep-agents, concept]
summary: Four multi-agent architecture patterns evaluated for the Shine ADK POC — trade-offs between coordination overhead, latency, domain separation, and context efficiency.
updated: 2026-04-25
sources:
  - raw/gdrive/2026-04-15-adk-overview-poc-architecture.md
---

# Multi-Agent Orchestration Patterns

Four patterns were evaluated for the Shine ADK POC (April 2026). The design goals were **fast** (minimize LLM calls, prefix caching) and **scalable** (across domains and teams).

## The Four Patterns

### 1. Manager / Experts as Tools
Each expert is exposed as a tool that the manager agent calls.

**Pros:** Clear boundaries, multi-model flexibility, framework-agnostic A2A
**Cons:** More LLM calls (each tool invocation is a round-trip), higher latency

**Best for:** Open-ended tasks where the manager needs to combine experts dynamically and latency is acceptable.

### 2. Manager / Experts
Classic multi-agent hierarchy — manager delegates to expert sub-agents.

**Pros:** Strong domain separation, multi-model flexibility
**Cons:** Coordination overhead, more complex handoffs between agents

**Best for:** Well-defined domain boundaries where experts rarely need to collaborate directly.

### 3. Router / Experts / Orchestrator
A dedicated router classifies intent and dispatches to specialist experts; an orchestrator handles synthesis.

**Pros:** Strong domain separation, efficient routing, multi-model flexibility
**Cons:** Coordination complexity, harder to govern (who owns the orchestrator?)

**Best for:** High-volume systems with clearly separated domains and predictable routing patterns.

### 4. Agent with Skills & Compaction ← Selected for Shine POC
A single agent with dynamically loaded skills; context compaction keeps the prompt lean.

**Pros:** Domain separation, minimal coordination overhead, lean context via dynamic tools
**Cons:** Less explicit orchestration, softer domain boundaries, limited per-domain model specialization

**Best for:** When minimizing LLM calls and prompt size matter most. The [[SKILL.md Pattern]] and [[Prefix Caching]] optimization work best here — skills are loaded into the context only when needed (compaction), and the static prefix can be cached aggressively.

## Why Pattern 4 Was Selected

The Shine POC explicitly optimized for:
1. **Minimize LLM calls** — Patterns 1–3 all require additional routing/orchestration calls. Pattern 4 routes via skill selection without a separate LLM call.
2. **Prefix caching at scale** — A single agent with a stable system prompt prefix is more cache-friendly than a multi-agent topology where each agent gets its own context.
3. **Team scalability** — Skills are independently owned files (SKILL.md format), not separate agent deployments. Teams can add skills without coordinating on agent topology.

## POC Stack (Shine, April 2026)

**v1 (static HTML client):**
```
FastMCP → FastAPI → DB / RAG → Static HTML (Python/JavaScript test app)
```

**v2 (React/Vite + A2UI):**
```
FastMCP → FastAPI → DB / RAG → React/Vite (TypeScript)
          FastAPI (a2ui)
```

v2 introduces the [[A2UI MCP Pattern]] — a FastAPI layer that translates agent responses into structured UI events. See `agents/adk-agent-pocs/a2ui_mcp/` for the reference implementation.

## Relation to Other Patterns

| Pattern | Closest wiki concept |
|---|---|
| Manager / Experts as Tools | [[A2A Agent Protocol]] (tool-based delegation) |
| Manager / Experts | Supervisor pattern in [[LangGraph Advanced Patterns]] |
| Router / Orchestrator | [[Plan and Execute Pattern]] |
| Agent with Skills & Compaction | [[ADK Context Engineering]] + [[SKILL.md Pattern]] |

## See Also
- [[ADK Context Engineering]]
- [[SKILL.md Pattern]]
- [[Prefix Caching]]
- [[ADK vs LangGraph Comparison]]
- [[LangGraph Advanced Patterns]]
