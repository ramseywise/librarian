---
title: Inverse Scaling in Test-Time Compute
tags: [foundations, concept]
summary: "Gema et al. find tasks where giving a reasoning model a longer budget lowers accuracy, with distractor, spurious-feature and constraint-tracking failure modes, so test-time compute is not monotone."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-gema-2025-inverse-scaling-test-time-compute.md
---

# Inverse Scaling in Test-Time Compute

Gema et al. (2025) build tasks on which accuracy falls as the reasoning budget grows: Misleading Math and Misleading Python (a simple question wrapped in distracting detail), a regression task with spurious features, and Zebra-style constraint puzzles.

## Reported findings

- Claude Opus 4 dropped from roughly 100% to 85-90% on the distractor tasks as the budget rose (self-reported). DeepSeek R1 fell from about 70% to about 30% under natural (uncontrolled) overthinking on one setup (self-reported).
- Few-shot examples repaired the regression task, whereas stating a prior in the prompt did not (self-reported).
- Safety-relevant behaviours showed mostly noisy signals, with the authors reporting changes in some models.

## Reading it

The result sits beside [[Overthinking and Concise Reasoning]]: both say longer traces can be worse. Here the cause is probed with constructed tasks rather than observed on natural questions.

## Limits

- Constructed tasks; how often real workloads look like them is not measured.
- Safety signals are noisy, and the paper treats them as preliminary.
- Model coverage is limited to the reasoning models tested at the time.

## See Also
- [[Prompting Reasoning Models]] — prerequisite-for
- [[Overthinking and Concise Reasoning]] — related
- [[Adaptive Branching MCTS]] — related (spending budget wider rather than longer)
- [[Few-Shot Prompting]] — related (examples fixed the regression task)
- [[Price Reversal in Reasoning-Model Costs]] — related
