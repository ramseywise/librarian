---
title: Agent Retry Taxonomy
tags: [llm, agents, infra, reference]
summary: "Not all failures are retryable — a per-failure-mode response table, retry at both call and node level, and the move that makes a retry a re-plan: feed the error back as context."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness--notes--05-verification-loops.md
---

# Agent Retry Taxonomy

**Not all failures are retryable.** Treating them uniformly is how a rate limit and a model
refusal get the same three attempts.

## The Table

| Failure | Response |
|---|---|
| **Transient** (network, rate limit) | Retry with exponential backoff (2×, jitter ±20%), max 3 |
| **Tool error** | Retry once, then escalate |
| **Model refusal** | **Never retry** — it will refuse again |
| **Schema violation** | Return the validation error; retry once with it in context |
| **Context exhaustion** | Compact or reset, then resume — see [[Long-Horizon Execution]] |
| **Fatal** | Stop; surface the error |

Two budget rules:

- **Retry budget is per-invocation, not per-tool** — otherwise five tools with three retries
  each become **fifteen attempts**.
- **Circuit-break after 5 consecutive failures** with a 60s cooldown, then fail fast.

> **Degrade loudly.** A partial result carries a `degraded: true` flag. **Silent degradation
> is worse than failure because it looks like success.**

## Retry at Two Levels

A single retry tier is too coarse for a multi-step workflow. Retry at **both the individual
LLM call and the logical node** — the whole step in the agent's plan:

- **Call-level** absorbs transient noise: a timeout, a rate limit, a malformed response.
  *Nothing about the plan was wrong.*
- **Node-level** re-runs the step. Use it when **the call succeeded but the step didn't
  achieve its purpose.**

**Retrying the wrong level wastes the attempt.** Re-issuing a call cannot fix a step whose
*approach* was wrong; re-running a whole node to recover from a rate limit **pays again for
work that already succeeded**.

## Feed the Error Back as Context

The move that makes retries more than repetition:

> **Give the agent the error, not just another attempt.**

An identical retry re-runs the reasoning that just failed and **tends to fail identically**.
Pass the failure back in — the database error message, the generated query, and the original
context all return to the model, which then produces a *corrected* query rather than the
same one. Cap at 3 attempts, after which the tool **reports failure honestly**.

This generalizes the schema-violation row above to every retryable failure, and **it is what
makes a retry a re-plan**.

It also explains why the two-retry rule holds: **once the error is already in context,
further attempts add no new information**, so a third failure genuinely indicates a bad spec
rather than bad luck. See [[Loop Detection and the Two-Retry Rule]].

## See Also
- [[Verification Loops]] — complements
- [[Loop Detection and the Two-Retry Rule]] — extends
- [[Execution Boundaries and Guardrails]] — complements
- [[Harness Engineering]] — part-of
