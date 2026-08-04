---
title: Multi-Step Graph Orchestration
tags: [llm, pattern, langgraph]
summary: A directed graph of processing nodes with explicit transitions, where the LLM executes within nodes but you control flow between them — the pattern for branching, human gates, and retry loops, with a concrete refactor trigger for when to adopt it.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/skills/project-discovery/reference/agent-orchestration.md
---

# Multi-Step Graph Orchestration

You define a directed graph of processing steps (nodes) with explicit transitions (edges).
The LLM executes within nodes but **you** control the flow between them. Supports
branching, loops, parallel execution, and human-in-the-loop gates.

**Use when** the process has clear phases; branching depends on intermediate results;
human approval is needed at specific checkpoints; retry/reflection loops are required
(*grade your own output, retry if below threshold*); or fan-out/fan-in parallelism applies.

**Avoid when** simple tool-calling suffices (over-engineering); the team can't maintain
graph complexity; or you're still figuring out what the steps should be — prototype first,
graph later.

## The refactor trigger

The clearest adoption signal in the source is behavioral rather than architectural:

> *"Start with a single agent. If you find yourself writing 'if the tool result shows X,
> then call tool Y' — that's a graph wanting to exist. Refactor into LangGraph then, not
> before."*

Control logic accumulating in your own code around the agent loop **is** the graph, just
implicitly and without checkpointing. Adopting the pattern makes it explicit.

## Complexity

**Multi-sprint to semester** — needs state schema design, node implementation, edge logic,
per-node error handling, and checkpointing for resumability.

## Example

A housing org's intake pipeline: client submits form → extract structured data → validate
against known records → if match, merge; if not, create → assign case worker by caseload →
**human review gate** (case manager confirms) → send confirmation.

## Scaffold mapping

| Parameter | Value | Rationale |
|---|---|---|
| `project_type` | `workflow` or `agent` | Graph-based orchestration |
| `primary_chat_agent` | `lg_agent` | LangGraph provides graph primitives |
| `human_approval` | `sometimes` or `always` | Nodes become interrupt points |
| `agent_memory` | `long_term` | State persists across interrupts |
| `vector_backend` | `postgres` | Postgres checkpointer for durable state |

## Trade-offs

**Pro:** full control over flow; explicit per-step error handling; human gates at precise
points; resumable via checkpointed state.
**Con:** more code to write and maintain; graph design is its own skill; harder to modify
once built; overkill for simple tasks.

## See Also
- [[Graph Engineering]] <!-- auto-linked -->
- [[Chain of Thought]] <!-- auto-linked -->
- [[Agent Orchestration Patterns]] — part-of
- [[Single Agent With Tools]] — upgrade-from
- [[Multi-Agent Role Specialization]] — upgrade-path
- [[Agentic Workflow Patterns]] — related (evaluator-optimizer, parallelization)
