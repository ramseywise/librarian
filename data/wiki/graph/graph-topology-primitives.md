---
title: Graph Topology Primitives
tags: [llm, agents, langgraph, infra, reference]
summary: "The four things a graph is made of — nodes that spend agency, edges that route, state that carries the coupling, and checkpointers that make interrupts and crash-resume the same mechanism."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph--graph-engineering.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph-engineering--notes--02-graph-primitives.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph-engineering--notes--03-state-and-reducers.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph-engineering--notes--04-durable-execution-and-interrupts.md
---

# Graph Topology Primitives

The primitives of [[Graph Engineering]]. Each is a decision surface, not just an API.

## Nodes — the agency budget

> **"Nodes do work. A node can be deterministic code, a single LLM call, a tool call, or a
> full agent with its own internal loop."**

The heterogeneity is the point, not an implementation detail. LangChain's docs-agent
example deliberately mixes node types — a fixed API call, a single LLM call with no tools,
and a full agent node for the open-ended part — producing a system that is *"predictable,
powerful, and efficient."*

> The design skill is deciding, **per node, how much agency to spend.** Every node that
> could be deterministic code and isn't is a node you pay tokens and variance for.

| Node kind | Purpose | Determinism | Cost |
|---|---|---|---|
| Deterministic function | Parsing, validation, formatting, API calls | Total | Compute only |
| Router | Classify and dispatch | Medium (rules or one LLM call) | One call at most |
| Single LLM call | One bounded transformation: summarise, extract, draft | Medium | One call |
| Agent | Open-ended reasoning with its own tool loop | Low | Many calls, variable |
| Human checkpoint | Approval before a consequential action | External | Latency |

The **single LLM call** row is the one teams forget exists between "code" and "agent".

**Specialization is prompt-only by default.** The [[n8n AI Workflow Builder]] runs every
node on the same model at temperature 0 and differentiates roles entirely by system
prompt — the cheapest form of node specialization, and the right starting point. Separate
models per node is an optimization to justify, not a default.

## Edges — where the control lives

Edges define which node executes next. Some are deterministic (always A → B); others are
**conditional**, reading node results or accumulated state to choose:

```python
add_conditional_edges(source_node, routing_function, {result_value: target_node})
```

Conditional edges are what buy you:

- **Adaptive branching** — route to a specialist based on intent classification.
- **Error paths** — route to a retry or repair node on tool failure.
- **Approval gates** — route to a human-in-the-loop node before an irreversible action.
- **Early exit** — route straight to `END` when a stopping condition is met.
- **Cycles** — route back to an earlier node to revise. **Every back-edge needs a counter in
  state or a recursion limit**; a cycle without a bound is an infinite loop.

A node can also return `Command(goto="node_b", update={...})`, combining a state update and a
routing decision. Use it when only the working node knows where to go next; prefer a separate
router when the routing logic should be testable on its own. **Handoffs live in state:** an
agent signals completion by writing a status key that a conditional edge reads, so agents can
be swapped without touching their neighbours. Before drawing an edge as sequential, apply the
true-dependency test — *does the next step actually read the previous step's output?* — the
incidental ones belong in a fan-out.

Static edges alone are insufficient in production, because **the set of nodes to run is
often unknown until runtime** — fan out over N retrieved documents, spawn one reviewer per
changed file. That gap is what [[Send API Fan-out]] closes.

## State — the substrate that replaces message passing

State is a shared data structure persisting across node executions within a run. **Nodes
transform state; edges route on it.** The framework is *"a state machine where the graph
defines the workflow, the state that moves through it, and the transitions between
steps."*

- **Short-term** — working memory for reasoning within a run.
- **Long-term** — persistence across sessions; runs resume after interruption or failure.
- **Reducers** — control how state merges when multiple branches write the same key.

**Reducers are the concurrency primitive.** Without one, parallel fan-out into a single key
is a race. This is where the single-writer rule bites hardest: designate one writer per
key, or use a reducer that makes multi-writer merging explicit. See
[[LangGraph State Reducers]].

The [[n8n AI Workflow Builder]] enforces the same rule for *concurrent user edits* with
optimistic locking (`versionId` + `expectedChecksum`) — **the single-writer rule enforced
by compare-and-swap instead of by convention.**

## Durable execution and interrupts

Human-in-the-loop is a **first-class graph primitive, not a UI feature**: the graph pauses
at a designated node, a human inspects and may modify state, execution resumes.

This requires **stateful persistence across the pause** — a capability loops alone cannot
provide, *because a loop that pauses has nowhere to put its stack*. That is the sharpest
argument for a graph over a loop when approval is required mid-execution.

> Checkpointers are what make interrupts, resume-after-crash, and time-travel debugging
> **all the same mechanism**.

A checkpoint is only as useful as the state schema: it must hold the plan, completed steps,
intermediate outputs and run metadata (attempt counts, budget used) — anything held only in a
Python variable or open connection is lost on resume.

**Where approval gates go.** Consequence concentrates at a few edges — sending, publishing,
paying, deleting, deploying — so put the gate *there*, not on every node; a gate everywhere
trains the human to click approve without reading. Gate before irreversible actions, before
actions crossing a trust boundary (external API, another tenant), and on low-confidence router
decisions. The [[n8n AI Workflow Builder]] puts its one gate after the planner, because the
plan is the cheapest thing to correct.

## Typed edges — the knowledge-graph side

On the [[Knowledge Graph Retrieval]] side of the discipline the claim is stronger:

> **"The edge type IS the knowledge."**

Untyped edges carry minimal reasoning value. Six edge types claimed as the production
minimum:

| Edge type | Meaning |
|---|---|
| `SUPERSEDES` | this replaces that |
| `DEPENDS_ON` | this needs that |
| `DECIDED_BY` | this was chosen because |
| `CAUSED` | this created that |
| `IMPLEMENTS` | this realises that |
| `REFERENCES` | this mentions that |

Adding relationship semantics is reported to improve reasoning accuracy by ~18%. **Treat
the number as vendor-adjacent, the principle as sound** — it is the same reason this wiki's
`## See Also` entries carry a `— type` suffix rather than bare links.

## Iteration bounds belong per node

The [[n8n AI Workflow Builder]] bounds every node independently (Discovery at 50
iterations, Builder at 100 per session) rather than capping the graph as a whole. Per-node
bounds are [[Loop Termination Design]] applied at each node, and they localize the blast
radius of a stuck node instead of letting it consume the whole run's budget.

## See Also
- [[Graph Engineering]] — extends
- [[Send API Fan-out]] — prerequisite-for (dynamic edges when N is unknown at compile time)
- [[LangGraph State Reducers]] — prerequisite-for (the fan-in concurrency primitive)
- [[Loop Termination Design]] — extends (per-node bounds vs per-loop bounds)
- [[Knowledge Graph Retrieval]] — prerequisite-for (typed edges on the retrieval side)
- [[n8n AI Workflow Builder]] — prerequisite-for
- [[Multi-Agent Topology Patterns]] — prerequisite-for
- [[LangGraph Advanced Patterns]] — prerequisite-for
- [[Graph Governance and Attribution]] — prerequisite-for
