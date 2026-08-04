---
title: Loop Detection and the Two-Retry Rule
tags: [llm, agents, infra, pattern]
summary: "The doom loop produces ten mutations of a broken solution — detection tracks per-file edit counts and forces re-planning rather than repair, because past two failures the problem is the spec, not the execution."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness--notes--05-verification-loops.md
---

# Loop Detection and the Two-Retry Rule

## The Doom Loop

An agent produces **10+ variations of a broken solution**, each a small mutation of the
last, **converging on nothing**.

It is expensive precisely because nothing stops it — which is why it belongs in the same
family as the cost envelope in [[Execution Boundaries and Guardrails]].

## Detection

Loop-detection middleware tracks **per-file edit counts** and triggers a *"reconsider your
approach"* prompt after N edits.

> **The intervention is deliberately not a hard stop.** It forces **re-planning rather than
> repair** — which is the actual missing move.

An agent in a doom loop is not short of attempts; it is short of a different approach. A
hard stop ends the run without producing the thing that would fix it.

## The Two-Retry Rule

> **Cap retries at two per gate failure. Beyond that, the problem is in the context or the
> specification — not the execution.**

Three failures on the same gate means **the agent lacks information or the spec is wrong**.
More attempts spend money to confirm that.

The rule is load-bearing only when paired with feeding the error back as context (see
[[Agent Retry Taxonomy]]): **once the error is already in context, further attempts add no
new information**, so the third failure is genuine signal rather than bad luck.

## Reasoning Budgets

Where models expose reasoning-effort tiers, spend asymmetrically — the **reasoning
sandwich**:

```
planning:     extra-high
execution:    high
verification: extra-high
```

**High effort at the ends, where decisions are made and checked; moderate through the
middle, where work is mechanical.** This split avoids timeouts while preserving quality.

The shape mirrors asymmetric QA in [[Verification Loops]] — **pay for judgment, economize on
labor.**

## See Also
- [[Agent Retry Taxonomy]] — extends
- [[Verification Loops]] — complements
- [[Execution Boundaries and Guardrails]] — complements
- [[Harness Engineering]] — part-of
