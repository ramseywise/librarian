---
title: Stagewise Recoverability Harness Granularity
tags: [harness, concept]
summary: A theory that a harness has a workflow part and a guidance part, that more structure is not monotonically better, and that scaffolding should stop once the agent can recover on its own, with thin real-benchmark support.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-wang-2026-harnesses-inference-time-alignment-over.md
---

# Stagewise Recoverability Harness Granularity

This paper on inference-time alignment of harnesses (Wang et al., Southern University of Science and Technology, arXiv preprint, May 2026) divides a harness into a workflow, which decomposes into sub-goals, and guidance, which reweights local actions. Its stagewise recoverability model treats success probability as the product of per-stage recoverability probabilities. The authors claim decomposition granularity must match what the agent can control, guidance helps only if it favours evidence-supported trajectories, and scaffolding only the first stages (partial harnessing) can beat a full workflow.

## Reported numbers (self-reported)

- **Terminal-Bench 2 granularity sweep:** the pass rate first rises and then falls as sub-goals are added, peaking at six steps. Setup: a qwen3.5-plus planner writes k-step workflows for k from 1 to 10, GLM-5 solves in Harbor Docker, 50 episodes per run, one attempt per task and k, 36 moderate tasks (32 in the aggregate; 4 returned all zeros). The peak value is only in a figure.
- **Plot hallucination (guidance):** with aligned guidance, hallucination stays near 0.35 whatever the rule count, while with misaligned guidance it climbs from 0.20 to almost 0.90. Setup: 6 chart types, 0 to 10 rules, 3 trials per cell, an LLM judge.
- **Partial harness case study:** a single task (llm-inference-batching-scheduler), on which a partial harness of 3 steps finishes while the full 10-step harness keeps looping on revisions. No pass rates or repeats are given.
- **Synthetic addition task:** the pass rate has a single peak as the number of scaffolded chunks grows, and stronger agents peak sooner. Retries saturate, pruning guidance lowers pass rate, and the unimodal shape persists across chunk sizes.

## Limits

- The authors concede simplified settings. The partial-harness claim on real data rests on one anecdote, which the extraction says the abstract overstates.
- One attempt per cell with no intervals; the sweep varies only step count with fixed guidance, so the link between granularity and capability is demonstrated only on synthetic data.
- Theorems are informal and need strong assumptions; synthetic guidance is action-pool pruning, far from real prompts.
- No harness-component ablation on a real agent, and nothing on multi-agent systems or iterative simplification of a production harness.

## See Also
- [[Harness Anatomy]] — related
- [[Harness Subsystem Attribution]] — related
- [[Long-Horizon Execution]] — related
