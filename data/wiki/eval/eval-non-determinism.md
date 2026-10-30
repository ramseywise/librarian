---
title: Eval Non-Determinism
tags: [eval, llm, agents, concept]
summary: "A single trial is an anecdote — run k trials and report pass@k when one success suffices, pass^k when consistency is the product, because a 75% agent passes three consecutive trials only 42% of the time."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--eval-harness.md
  - data/raw/repos/learn-ai-engineering/interviewing--notes--eval-harness.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--06-evaluating-agents.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--09-reading-results.md
---

# Eval Non-Determinism

Agent outputs vary between runs. That makes a single trial an anecdote, not a measurement —
so the unit of evaluation is **a proportion of trials that succeeded**, not a pass/fail.

Run the eval set multiple times and measure **how often** the agent succeeds at a task.

## Two metrics, two different products

| Metric | Measures | Behavior as k rises | Use when |
|---|---|---|---|
| **pass@k** | At least one of k attempts succeeds | **Rises** | One success is enough — the user or a downstream check can pick the winner |
| **pass^k** | *All* k trials succeed | **Falls** | Consistency is the product |

`50% pass@1` means the model succeeds at half the eval tasks on its first try.

**The pass^k arithmetic is the part worth internalizing:**

> A 75% per-trial success rate over 3 trials passes all three with probability
> `0.75³ ≈ 42%`.

An agent you would describe as "right three times out of four" is, from the perspective of
a user who needs it right *every* time across a three-step interaction, **worse than a coin
flip.** This is the same multiplicative compounding as the traversal-depth warning in
[[Knowledge Graph Retrieval]], and it is why per-trial pass rates flatter agents.

## Choosing the metric

The choice is a claim about what you are shipping, not a reporting preference:

- **pass@k for tools** — a code generator whose output a human reviews, a search that
  returns candidates, any surface with a selection step downstream.
- **pass^k for agents** — customer-facing systems where *"users expect reliable behavior
  every time."* Anything running unattended in a [[Loop Engineering]] cycle also belongs
  here, since there is no human to pick the good run.

Choosing k is task-dependent: it should reflect **how many attempts the real deployment
actually affords**, not a round number.

## The consequence for eval design

Multi-trial evaluation multiplies eval cost by k. Two things follow:

1. **Reset the environment between trials.** Otherwise one trial contaminates the next and
   an environment problem reads as an agent failure — see [[Eval Suite Maintenance]].
2. **Reserve high k for the tasks where consistency is the requirement.** Running every
   task at k=10 is a budget decision disguised as rigor.

## Best@k, the unbiased estimator, and per-task distributions

A third metric sits beside pass@k and pass^k: **Best@k** — the score of the best of k trials, for
continuous scores on open-ended tasks ("what's the quality ceiling?"); it rises with k.

When estimating pass@k from *n* samples with *c* correct, use the unbiased estimator
**pass@k = 1 − C(n−c, k) / C(n, k)** (Chen et al. 2021, the Codex paper) rather than plugging the
observed rate into 1 − (1 − p)^k.

Also report the **per-task pass-rate distribution**. A suite at 70% could be "every task passes 70% of
the time" (flaky) or "70% of tasks always pass, 30% never do" (capability gaps) — different fixes.
For the statistics, average the k trials *within* a task first, then treat tasks as the unit of
sampling ([[Eval Error Bars and Sample Size]]).

## See Also
- [[Eval Ladder]] <!-- auto-linked -->
- [[Loop Autonomy Ladder]] <!-- auto-linked -->
- [[Eval-Driven Development (EDD)]] <!-- auto-linked -->
- [[Online Eval Sampling]] <!-- auto-linked -->
- [[Eval Harness Anatomy]] — part-of (the trial is the unit this page measures over)
- [[Eval Suite Maintenance]] — complements (environment reset between trials)
- [[Loop Termination Design]] — complements (per-trial reliability is what a retry cap is compensating for)
- [[Knowledge Graph Retrieval]] — complements (the same multiplicative compounding, applied to traversal depth)
- [[UNGATED Metric Convention]] — prerequisite-for
- [[Simulated User Evaluation]] — extends
- [[Paired Eval Comparison]] — prerequisite-for
