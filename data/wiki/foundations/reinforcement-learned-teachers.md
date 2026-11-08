---
title: Reinforcement-Learned Teachers
tags: [foundations, pattern]
summary: "Train a small model with RL to write explanations for known question-solution pairs, rewarded by how well a student can reproduce the solution from them; in the paper a 7B teacher's raw traces gave better student models than traces distilled from much larger reasoners."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-cetin-2025-reinforcement-learning-teachers-test-time.md
---

# Reinforcement-Learned Teachers

Reinforcement-Learned Teachers (RLTs; Cetin et al., Sakana AI, NeurIPS 2025, arXiv 2506.08388) change what RL optimises. A normal reasoning model must solve a problem from scratch. An RLT is shown the question and the correct solution, and writes an explanation that becomes the reasoning trace used to train a student. The reward is r = r_SS minus lambda times r_KL. The first term combines the student's mean and minimum log-probability on the solution, conditioned on the question plus the teacher's explanation. The second is the KL divergence between teacher and student over the explanation tokens, with lambda = 3 and alpha = 0.01. The authors call the signal dense because it ranks outputs before the teacher has any task skill. Training used GRPO for 125 steps (batch 1024, group 64, context 16384), after a short SFT on open traces; the reward student was Bespoke-Stratos-7B.

## Results (self-reported)

- **Distillation.** A Qwen2.5-7B-Instruct teacher, 17K question-solution pairs, one sample per question, average of AIME24, MATH500 and GPQA Diamond: 7B student 49.50 against 46.60 for R1-trace distillation (Bespoke), 32B student 73.23 against 71.47. Baseline numbers were mostly copied from prior work.
- **1K samples.** 32B student 71.37 against 65.60 for Bespoke-32B-1K.
- **Cold start for RL.** RLT-7B then one RL epoch on a small set: 50.53, against 48.30 for the Bespoke cold start and 40.77 with no cold start. On GPQA the Bespoke cold start was ahead (45.40 against 40.90).
- **Ablations.** Without the KL term the student scored 34.10 (base 39.17); without min/max reduction 47.43. A 3B teacher gave students of 46.50 (7B) and 63.90 (32B).
- **Cost.** 280.4 H100 hours to train the RLT and 6.7 to generate data. The R1 figure is a rough estimate, which the authors call a lower bound.
- **Transfer.** On automatically generated Countdown problems, students distilled from RLT traces beat direct RL by the authors' account; the values appear only in a bar plot.
- **Reward predicts quality.** Sixteen datasets ranked by pre-RL reward gave a Pearson correlation above 0.89 with student results.

## Limits

- Needs ground-truth solutions, a warm start on pre-collected traces, and a student to compute the reward (training time is over 90% generation).
- It produces traces, not a problem solver, so it does not replace RL for final capability. Context capped at 16384, 7B teachers only; evaluation is math, science, coding and Olympiad tasks.
- Single run and single sample per evaluation with no error bars, so gaps such as 49.5 against 48.8 are weak evidence (the extraction's observation). The R1 comparison uses different post-processing pipelines.
- Baselines date from early 2025 (Qwen2.5, R1, Bespoke).

## See Also
- [[Post-Training for Agents]] — prerequisite-for
- [[On-Policy Distillation]] — alternative-to (another dense teacher signal for the student)
- [[DualDistill Agentic-R1]] — related (also builds a small student's training traces from teachers)
- [[Preference Optimization Algorithms]] — prerequisite-for
- [[DAPO]] — related (both use GRPO-style RL)
