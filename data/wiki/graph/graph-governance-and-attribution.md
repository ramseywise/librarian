---
title: Graph Governance and Attribution
tags: [infra, agents, llm, reference]
summary: "Once work fans out across nodes, \"the graph did it\" is not an acceptable audit answer — identity propagation, per-node cost attribution, and approval gates placed where consequence concentrates."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph--graph-engineering.md
---

# Graph Governance and Attribution

The enterprise layer of [[Graph Engineering]]. The whole discipline reduces to one
problem: **once work fans out across nodes, "the graph did it" is not an acceptable audit
answer.**

## Identity and tracing

Every independently governed caller needs a **resolved identity**. Gateway-mediated model
and MCP calls must carry stable `graph_id`, `run_id`, and `node_id` identifiers so
orchestration traces correlate with gateway records for cost, policy, latency, and tool
use.

> That propagation is what makes **node-level cost attribution possible at all**. Without
> it you have a total bill and no way to know which node earned it.

This extends the tracing architecture in [[Observability and Runtime Patterns]] with a
third identifier: a trace tells you *what happened in one run*; graph/run/node identifiers
tell you *which node in which topology* — the attribution axis a flat trace lacks.

## Record the runtime graph, not the declared one

The checklist item most often skipped:

> Does the orchestrator record the **actual runtime work graph**, not just the declared
> one?

With dynamic fan-out ([[Send API Fan-out]]) and conditionally-spawned subtasks, the graph
that ran is not the graph you wrote. **Auditing the declared topology audits your
intentions, not your system.**

## Cost control

Work graphs amplify spend through fan-out, retries, and dynamically spawned subtasks.
Budget rules need to operate at **tenant/team scope** with separate limits per virtual
account or metadata value.

> **A per-run cap is not enough when one run can spawn fifty nodes.**

## Structural checkpoints

Human approval checkpoints before configured sensitive tool calls — placed *"at exactly
the edges where consequence concentrates."*

> The insight is that **consequence concentrates at specific edges**, so that's where the
> gate belongs — not uniformly across every node.

Uniform gating is the failure mode on both sides: it makes the graph unusable *and* trains
reviewers to approve reflexively, which means the one gate that mattered gets rubber-
stamped along with the ninety that didn't. This is the graph-scale version of the
execution-boundary argument in [[Execution Boundaries and Guardrails]].

## Production checklist

1. Does every independently governed caller have a resolved identity?
2. Do gateway-mediated model and MCP calls carry stable graph, run, and node identifiers?
3. Does the orchestrator record the **actual runtime work graph** (not just the declared one)?
4. Can orchestration traces be correlated with gateway cost, policy, latency, and tool records?
5. Are graph- or node-associated budget rules mapped through virtual accounts or metadata?
6. Are sensitive tool actions protected by explicit approval checkpoints?
7. Are model changes isolated behind virtual-model routing?

> Production readiness requires *"explicit ownership across orchestration, identity,
> policy, budgets, approvals, and evidence."*

Note what "ownership" means here: **each of the six has a named owner**, not a mechanism.
An unowned budget rule is a budget rule nobody raises when it starts firing.

## See Also
- [[Graph Engineering]] — part-of
- [[Observability and Runtime Patterns]] — extends (adds the node attribution axis to tracing)
- [[Execution Boundaries and Guardrails]] — complements (gating placed by consequence, not uniformly)
- [[Graph Topology Primitives]] — depends-on
- [[Send API Fan-out]] — complements (dynamic fan-out is why declared ≠ runtime graph)
