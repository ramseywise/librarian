---
title: Multi-Agent Orchestration Patterns
tags: [adk, langgraph, deep-agents, concept]
summary: Multi-agent architecture patterns — supervisor/handoff/parallel swarm trade-offs, try-agent history for fallback routing, tool count budget, and the Shine ADK POC selection rationale.
updated: 2026-04-26
sources:
  - raw/gdrive/2026-04-15-adk-overview-poc-architecture.md
  - raw/claude-docs/playground/docs/research/agentic-ai/orchestration-patterns.md
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

v2 introduces an A2UI MCP pattern — a FastAPI layer that translates agent responses into structured UI events. See `agents/adk-agent-pocs/a2ui_mcp/` for the reference implementation.

## Relation to Other Patterns

| Pattern | Closest wiki concept |
|---|---|
| Manager / Experts as Tools | [[A2A Agent Protocol]] (tool-based delegation) |
| Manager / Experts | Supervisor pattern in [[LangGraph Advanced Patterns]] |
| Router / Orchestrator | [[Plan and Execute Pattern]] |
| Agent with Skills & Compaction | [[ADK Context Engineering]] + [[SKILL.md Pattern]] |

## Supervisor vs Handoff vs Parallel Swarm

Beyond the four Shine POC patterns, three general multi-agent topologies for VA agents:

| Topology | Mechanism | Best for | Watch out for |
|----------|-----------|----------|---------------|
| **Supervisor** | Central LLM routes to subagents, aggregates results | Well-defined domains, ordered workflows | Supervisor becomes a bottleneck; one extra LLM call per turn |
| **Handoff** | Agent transfers control directly to next agent with full context | Sequential pipelines, specialist chains | Context grows with each handoff; hard to recover from mid-chain failures |
| **Parallel Swarm** | Multiple agents work concurrently on sub-tasks, results merged | Broad research, multi-source tasks | Fan-out cost, result merging complexity |

**Supervisor is the most common VA pattern** — it maps cleanly to domain splitting (billing, analytics, support subagents).

## Try-Agent History (Fallback Routing)

When a subagent can't handle a query, the supervisor should not re-route to the same agent. Track which agents have been tried:

```python
class AgentState(TypedDict):
    messages: list[BaseMessage]
    next_agent: str
    tried_agents: list[str]   # agents already attempted this turn

async def supervisor_node(state: AgentState) -> dict:
    tried = state.get("tried_agents", [])
    chosen = await classify_intent(
        state["messages"],
        exclude=tried  # pass tried list to routing prompt
    )
    return {
        "next_agent": chosen,
        "tried_agents": tried + [chosen],
    }
```

**Routing prompt addition:**
```
Already tried: {tried_agents}. Do NOT route to these again. Choose a different agent or respond directly.
```

## Tool Count and Domain Split Signal

Tool count directly affects routing quality. See [[VA Product Design Patterns]] for the full budget table.

**Split signal:** at 20+ tools, split into domain sub-agents. Each stays under 12 tools; the supervisor routes between them.

## Typed I/O Contracts Between Agents

In a multi-agent topology, define typed input/output contracts for each agent. The supervisor passes a typed state dict, not raw messages:

```python
class InvoiceAgentInput(TypedDict):
    invoice_id: str | None
    customer_name: str | None
    conversation_history: list[BaseMessage]

class InvoiceAgentOutput(TypedDict):
    result: str
    confidence: float
    tools_called: list[str]
```

This prevents schema drift as agents evolve independently.

## See Also
- [[ADK Context Engineering]]
- [[SKILL.md Pattern]]
- [[Prefix Caching]]
- [[ADK vs LangGraph Comparison]]
- [[LangGraph Advanced Patterns]]
- [[VA Product Design Patterns]]
- [[Runtime Topology and Checkpointer Alignment]]
