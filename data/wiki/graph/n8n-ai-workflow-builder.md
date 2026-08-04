---
title: n8n AI Workflow Builder
tags: [langgraph, infra, agents, reference]
summary: "A shipped supervisor-pattern LangGraph with published operational constants — five specialist subgraphs, prompt-only specialization, per-node iteration bounds, and an agent never allowed to fill its own context with the artifact it is editing."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph--graph-engineering.md
---

# n8n AI Workflow Builder

A documented, shipped supervisor-pattern graph — valuable because **the operational
constants are published rather than inferred**. Most multi-agent write-ups describe a
topology; this one gives the numbers.

The feature generates n8n workflows from a prompt. Architecture: LangGraph with a
**supervisor routing to five specialist subgraphs**.

## Topology

| Node | Role | Bound |
|---|---|---|
| Supervisor | Routes each message to a subgraph | — |
| Discovery | Explores the node registry | max 50 iterations |
| Planner | Builds a structured plan; pauses for approval (HITL) | — |
| Builder | Executes tool calls | max 100 iterations/session |
| Responder | Renders user-facing Markdown | — |
| Parameter Updater | Surgical edits to existing node params | — |

## Four transferable lessons

### Specialization is prompt-only

Every agent runs the **same model** (Claude Sonnet 4.5, temperature 0); the roles differ
entirely by system prompt.

> This is the cheapest form of node specialization and worth treating as the default.
> **Separate models per node is an optimization to justify, not a starting point.**

### Every node is iteration-bounded

Discovery at 50, Builder at 100 — the [[Loop Termination Design]] cap applied **per node
rather than to the graph as a whole**, which localizes the blast radius of a stuck node
instead of letting it consume the whole run's budget.

### Concurrency by compare-and-swap

LangGraph checkpoints via `MemorySaver` or DB-persisted messages; session key
`workflow-{workflowId}-user-{userId}` with a 24-hour TTL. Concurrent edits use **optimistic
locking** (`versionId` + `expectedChecksum`) — *the single-writer rule enforced by
compare-and-swap instead of by convention* (see [[LangGraph State Reducers]]).

### Validation at the tool boundary

Seven LangChain tools (`add_nodes`, `update_parameters`, `connect_nodes`,
`get_node_details`, `get_execution_logs`, `get_expression_data_mapping`,
`get_node_context`), and *"every mutation is validated before it's applied"* — parameter
schema checks, type compatibility, expression path resolution.

> **The graph the agent is building is itself typed**, so malformed edges are rejected at
> write time rather than discovered at run time.

## Published operational constants

| Constant | Value |
|---|---|
| Context window | 200K tokens |
| Auto-compact threshold | 150K tokens |
| Max prompt length | 5,000 chars |
| Max workflow JSON | 30K tokens |
| Frontend payload cap | 400 KB |
| Request timeout | 180 s |
| IP rate limit | 100 requests/period |

Two of these are the interesting ones:

- **Compact triggers at 75% of the window** — not at exhaustion. See
  [[Context Compaction]].
- **The artifact under construction is capped at 30K**, 15% of the window. **The agent is
  never allowed to fill its own context with the thing it is editing.** That constraint
  generalizes well past workflow JSON — any agent editing a large artifact needs a size
  ceiling on the artifact, not just on the history.

## Deployment surface

Self-hosts via npm, Docker, or Docker Compose, with provider guides for AWS, Azure, GCP,
DigitalOcean, Hetzner, Heroku, and OpenShift. All installations run the same core; without
a license key it runs as the free Community edition. Relevant as the deployment surface for
a graph system you intend to **operate** rather than demo.

## See Also
- [[Graph Engineering]] — instance-of
- [[Graph Topology Primitives]] — instance-of (nodes, bounds, and state discipline in production)
- [[Loop Termination Design]] — complements (per-node caps)
- [[LangGraph State Reducers]] — complements (optimistic locking as single-writer enforcement)
- [[Context Compaction]] — complements (the 75% compact trigger)
