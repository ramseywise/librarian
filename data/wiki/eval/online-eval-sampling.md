---
title: Online Eval Sampling
tags: [eval, infra, llm, pattern]
summary: "Score 10–20% of production traces by rule rather than at random — negative feedback, high-cost dialogues, time windows, and a full 48-hour review after any model or prompt change."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--eval-harness.md
---

# Online Eval Sampling

Offline evals measure the tasks you thought of. Online evaluation scores **live traffic**,
which is where the discovery rows in [[Eval Suite Maintenance]] actually come from.

Scoring every trace is unaffordable; scoring a random sample wastes the budget on
uninformative runs. The recommendation is **10–20% of traces, sampled by rule.**

## The four sampling rules

| Rule | Trigger | Why it earns its slot |
|---|---|---|
| **Negative feedback** | User explicitly expresses dissatisfaction | A labeled failure, free |
| **High-cost dialogues** | Token consumption over threshold | *"Often indicates the agent is circling around"* |
| **Time window** | Random sample at fixed daily intervals | Maintains coverage of **normal** traffic |
| **Post-change** | Any model or prompt change | **Full review within the first 48 hours** |

The high-cost rule is the non-obvious one: **cost is a proxy for thrashing**. An expensive
run is usually a run where the loop failed to converge, which makes token spend a free
failure detector requiring no user signal at all. The same reasoning appears as
steps-to-completion in [[Eval Maturity Ladder]] and as stall detection in
[[Loop Termination Design]].

Note the third rule exists to correct the first two. Rules 1, 2, and 4 all sample
**anomalies** — a suite fed only by them develops a distorted picture of the system, because
nothing in the sample represents ordinary successful traffic. Time-window sampling is the
control group.

## Two-layer evaluation

Online scoring runs as two layers that **must be used together**:

| Layer | Method | Coverage | Role |
|---|---|---|---|
| **1** | Manual sampling and labeling — error cases, long dialogues, negative feedback | Narrow | Identify failure patterns; produce **calibration data** for layer 2 |
| **2** | LLM-as-judge over a much wider slice of traces | Broad | Full coverage, calibrated by layer 1's labels |

Why neither works alone:

> Running **only layer 2** makes the scoring criteria prone to **drift**. Relying **only on
> layer 1** doesn't cover real-world traffic at scale.

Layer 1 is a **calibration sample, not a review queue** — the 5–10% human spot-check in
[[Eval Maturity Ladder]], whose job is to tell you whether the judge can still be trusted.
An LLM judge with no human calibration behind it is in the `experimental` grader state and
must never gate a release.

## Drift monitoring

The continuous form: capture **baseline metrics during the evaluation phase**, then run the
same scoring pipeline against production traffic on an ongoing basis. Divergence from
baseline beyond an acceptable margin is a concrete signal to investigate.

Causes worth expecting: model updates, shifts in input data, upstream API changes, seasonal
variation in user behavior. **None of these involve a change to your code**, which is why
drift is invisible to CI and only online evaluation catches it.

## See Also
- [[Eval vs Test Distinction]] <!-- auto-linked -->
- [[Eval Suite Maintenance]] — part-of (the source of rolling discovery rows)
- [[Eval Maturity Ladder]] — instance-of (level 4: continuous sampling with drift alerts)
- [[LLM-as-Judge Evaluation]] — depends-on (layer 2, and its calibration requirement)
- [[Observability and Runtime Patterns]] — depends-on (traces are the sampling substrate)
- [[User Feedback Loops]] — complements (negative feedback as a sampling trigger)
- [[Loop Termination Design]] — complements (cost as a thrashing proxy)
- [[Experiment Tracking Schemas]] — depends-on (prompt_version + git_commit + model as the attribution key for a drift signal)
