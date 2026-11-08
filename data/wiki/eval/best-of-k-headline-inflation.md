---
title: Best-of-k Headline Inflation
tags: [eval, concept]
summary: "Agent benchmarks often headline the best of several runs, which can sit far above what one run delivers: ScienceAgentBench's o1 scores 42.2% best-of-3 but 27.1% averaged over runs, and MLE-bench's medal rate doubles from pass@1 to pass@8; check which number is reported and how the best run was chosen."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-chan-2024-mle-bench.md
  - data/raw/papers/2026-11-05-chen-2024-scienceagentbench.md
---

# Best-of-k Headline Inflation

pass@k, the chance that at least one of k attempts succeeds, is a legitimate metric
([[Eval Non-Determinism]]). The trouble starts when a best-of-k number is read as what the
agent does in one run.

## Two examples

- **[[ScienceAgentBench]]** reports each configuration's best of three runs, picked by success
  first, then executability, then code similarity, then cost. The best non-reasoning agent
  scores 32.4% this way and 22.9% averaged over the three runs; o1 scores 42.2% against
  27.1%. The best-of-3 number is about one and a half times the mean.
- **[[MLE-bench]]** headlines pass@1 and reports the scaling separately: o1-preview with AIDE
  goes from a 16.9% medal rate at one attempt to 34.1% at eight, and GPT-4o at six attempts
  (17.0%) matched o1-preview at one.

## Why the distinction matters

- **Selection uses the grader.** The MLE-bench extraction notes that pass@k credits a run whenever
  one of its k attempts medals on the test-set grading, a choice the agent has no way to make
  itself, and that the paper does not discuss this.
- **Cost scales with k.** A best-of-3 result costs three runs, yet ScienceAgentBench reports
  the cost of the selected run only.

## How to read and report

1. For any agent benchmark number, find out whether it is a single run, a mean, or a best-of-k.
2. Report the mean with a confidence interval as the main number, and pass@k beside it as the
   ceiling that selection could reach ([[Eval Error Bars and Sample Size]]).
3. If you report best-of-k, also report the total cost of all k runs and how the best was
   picked.

## Limits

MLE-bench measures how pass@k scales with k but not how an agent could choose among its own
attempts; it gives no dollar cost and does not say how its standard error is pooled.
ScienceAgentBench reports best-of-3 without studying the choice, and its cost figure covers
the selected run only. The models in both are 2024 vintage.

## See Also
- [[Eval Non-Determinism]] — prerequisite-for (pass@k and pass^k definitions)
- [[MLE-bench]] — instance-of
- [[ScienceAgentBench]] — instance-of
- [[Eval Error Bars and Sample Size]] — related
- [[Validated Concept vs Unmeasured System]] — related
