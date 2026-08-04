---
title: Agent Management Layer
tags: [infra, eval, agents, reference]
summary: "The six systems a production agent needs beyond the agent itself — evals, fallback/escalation, drift monitoring, HITL checkpoints, audit logging, handoff protocol — argued as 60% of the deployment, not 10%."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--eval-harness.md
---

# Agent Management Layer

> The agent itself — the model, the prompts, the tool integrations — is maybe **40%** of
> what a production deployment actually requires. The other **60%** is the system that keeps
> the agent honest, visible, and recoverable when things go sideways.

The split is the claim worth arguing with, and it holds up better than it first sounds. Each
of the six items below exists because an agent *fails differently* from a service: not by
crashing, but by continuing to run while producing worse output. None of the six are
detectable from uptime.

> Organizations that treat agent deployment as a build-and-ship exercise will spend the next
> six months doing manual cleanup on failures they could have prevented.

## The six

### 1. Evaluation frameworks

Structured suites run on a **regular cadence**, scoring accuracy, relevance, and task
completion across realistic scenarios. Good suites mix **deterministic checks** (did it call
the right tool with the right parameters?) with **judgment-based scoring** (was the response
actually useful?) — the layered-graders point in [[Eval Maturity Ladder]].

Evaluation has to be **continuous** — in CI *and* against live traffic, because data drifts.
Anthropic's framing: eval suites are **living artifacts**, with a dedicated team owning the
infrastructure while **domain experts contribute tasks and run the tests themselves**. That
ownership split is the operational half of [[Eval Suite Maintenance]] — an eval suite with no
domain-expert contributor slowly becomes a test of what the platform team can imagine.

### 2. Fallback and escalation logic

Two layers, often conflated:

- **Fallback** defines the *boundaries* — what happens when the agent cannot proceed.
- **Escalation** layers **severity awareness** on top — not just *stop*, but *stop and route
  to whom, how urgently*.

Built **before** deployment and treated as **load-bearing architecture**, not error handling
bolted on later.

### 3. Drift monitoring

Tracks the gap between how the agent performed at validation and how it performs now.
Mechanism and causes in [[Online Eval Sampling]]. The property that makes it mandatory:
**none of the causes involve a change to your code**, so nothing in CI will ever fire.

### 4. Human-in-the-loop checkpoints

Structured moments where a person reviews, approves, or redirects agent output before it
reaches a user or triggers a downstream action.

The second-order effect is the one people miss: **checkpoints are a training-data pipeline.**
Every human correction is a labeled signal about where the agent is weak — *but only if it is
logged*, which is why items 4 and 5 are effectively one system.

### 5. Logging for auditability

Full execution logging: chain of reasoning, tool invocations, retrieved context, intermediate
outputs, final actions — every run. Three purposes, and they have different retention and
access requirements:

| Purpose | What it needs |
|---|---|
| **Debugging** | Depth and recency |
| **Compliance** | Immutability and retention |
| **Improvement** | Queryability across runs |

See [[Observability and Runtime Patterns]] for span structure.

### 6. A defined handoff protocol

Every transition — agent→agent, agent→user — is a potential failure point. A protocol
specifies four things:

1. What information transfers with the task
2. What context the receiving party needs
3. What constitutes a **successful** handoff versus a dropped one
4. **Who owns the outcome** after the transition

Point 3 is the one usually left implicit, and implicit success criteria are how work gets
silently dropped between agents. Point 4 is its organizational twin. Compare the explicit
edge contracts in [[Graph Engineering]] — a handoff protocol is that discipline applied
across a boundary the graph does not own.

## See Also
- [[Eval Maturity Ladder]] — depends-on (items 1 and 3 are its levels 3 and 4)
- [[Online Eval Sampling]] — instance-of (the drift-monitoring mechanism)
- [[Eval Suite Maintenance]] — extends (evals as living artifacts, and who owns them)
- [[Observability and Runtime Patterns]] — implements (item 5)
- [[Production Hardening Patterns]] — complements (system-specific checklist under this generic frame)
- [[Graph Engineering]] — complements (handoff protocol as an edge contract across an ownership boundary)
- [[Safeguards Architecture — Five Protection Layers]] — complements (fallback and escalation as defence layers)
