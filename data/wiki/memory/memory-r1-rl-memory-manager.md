---
title: "Memory-R1 RL Memory Manager"
tags: [memory, pattern]
summary: "Memory-R1 trains a Memory Manager that picks ADD, UPDATE, DELETE or NOOP using only downstream answer exact match as reward, plus an Answer Agent that distills retrieved memories; F1 45.02 against 35.04 for the strongest baseline on LoCoMo (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-yan-2025-memory-r1.md
---

# Memory-R1 RL Memory Manager

Two agents are trained with reinforcement learning (PPO and GRPO variants), one at a time with the other frozen.
- The Memory Manager chooses among ADD, UPDATE, DELETE and NOOP for each new fact. Its reward is outcome-only: exact match of a frozen Answer Agent's answer, so no operation labels are needed.
- Before answering, the Answer Agent filters 60 retrieved memories down to the relevant ones (memory distillation).

A vanilla in-context manager, given "adopted Buddy" then "adopted Scout", issues DELETE plus ADD, while the trained manager issues one UPDATE (anecdotal, two cases).

## Results (self-reported)

Setup: LoCoMo without the adversarial subset (1307 questions in the test set) using LLaMA-3.1-8B-Instruct at temperature 0; baselines were reimplemented by the authors.
- The GRPO variant scored F1 45.02, B1 37.51 and J 62.74 overall, against 35.04, 27.99, 48.20 for MemoryOS (+28.5% relative F1). Training used 152 QA pairs (81 validation).
- Behaviour cloning from teacher trajectories scored J 58.76 against 62.74 for GRPO; on a 7B Qwen model they nearly tied (61.13 against 61.51).
- Removing the RL-trained manager cost about 6-8 points; memory distillation helped, especially under GRPO (F1 41.0 to 45.0).
- Zero-shot on LongMemEval after LoCoMo-only training, GRPO scored best in the table, but its J lead over one baseline on LLaMA is only 1.2 points.
- An answer-judge reward made answers verbose (F1 33.69), so exact match was used. Gains at scale: J 41.24 to 57.92 (3B) and 50.80 to 63.50 (14B), but 58.38 to 57.46 at 7B, a drop.

## Limits

- Dialogue only; multimodal untested. Manager and Answer Agent are trained separately because rewards are sparse; end-to-end training is future work.
- Internal inconsistencies in the extraction: the abstract and introduction name Mem0 as the baseline for the headline gain while Section 4.2 names MemoryOS; split sizes and turn counts differ between sections (24 against 50); some ablation values behave oddly.
- Baselines were re-implemented by the authors; training data is small.

## See Also
- [[Memory Lifecycle]] — prerequisite-for
- [[Memory Store Operations]] — prerequisite-for
- [[Designed Memory vs Raw-Record Search]] — related
- [[Multi-Session Agent Benchmarks]] — related
