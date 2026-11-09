---
title: "Dr. MAMR Lazy-Agent Multi-Agent RL"
tags: [foundations, pattern]
summary: "Dr. MAMR traces the collapse of trained two-agent reasoning pairs into one working agent to a turn-count normalization in multi-turn GRPO, and fixes it with a debiased loss, a causal-influence reward and a restart reward, scoring above single-agent GRPO on seven math benchmarks (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-zhang-2025-unlocking-power-multi-agent-llm.md
---

# Dr. MAMR Lazy-Agent Multi-Agent RL

Dr. MAMR (a preprint) studies why a trained multi-agent pair can lose to one agent. The baseline, ReMA, pairs two agents that share weights but carry different role prompts: one does meta-thinking and the other does the reasoning. After reinforcement learning the pair behaves like a single agent: the reasoning agent's causal influence, measured by blocking attention to one of its steps and computing the KL divergence at the following step, rises briefly and then decays toward zero while the meta-thinking agent dominates. The authors call this the lazy agent problem. As a data point (self-reported, Sec 4 motivating experiment, MATH500, model size not stated in the extraction), MATH500 accuracy is 75.0 before training and 74.4 once ReMA has been trained.

## Cause and fix

The authors point to a loss bias: multi-turn GRPO scales each trajectory by the count of its turns, so given equal reward the shorter trajectory is favoured, and lazy behaviour such as empty or copied outputs yields shorter trajectories. Theorem 1 states the condition; the evidence is a mean-turns curve over the first twenty steps. The fix has three parts:

- Drop the per-turn normalization.
- Add a causal-influence reward modelled on Shapley values, grouping similar steps at cosine similarity 0.9 or above, with weight 0.1.
- Add a verifiable restart reward, also weighted 0.1, which needs an SFT cold start with noise inserted by GPT-4o.

In the same Sec 4 / Fig 2 comparison on MATH500 (self-reported), a prompt that discourages trivial replies only lifts accuracy from 74.4 to 75.6, against 78.4 for Dr. MAMR.

## Reported results (self-reported)

Setup: Qwen2.5 Instruct, trained on DeepScaleR, pass@1 over seven math benchmarks. Average scores at 7B: Dr. MAMR 58.43, single-agent GRPO 55.08, ReMA 51.97. At 14B the same order holds, with 62.49, 58.05 and 57.24. Ablating the normalization fix, the causal-influence reward or the restart reward each lowers the 7B scores, for example AIME24 from 20.00 to 13.33 without either of the first two. ReMA's training reward collapses to zero after about 150 steps at 7B, and a per-turn process reward model broke down after roughly 30 steps, a failure the authors put down to reward hacking.

## Limits

- Math only, three Qwen2.5 sizes, and both agents share weights, so the pair is neither heterogeneous nor tool-using. Laziness is defined through the attention-suppression KL, and it is an artifact of the training loss, so it says little about prompted multi-agent systems at inference.
- At 14B single-agent GRPO edges Dr. MAMR on two sets: MATH500 by 80.60 to 80.40, and GSM8K by 94.50 to 93.69. There are no seeds, and single AIME24 runs move in steps of 3.33 points.
- Internal inconsistency noted by the extraction: one section says gains grow with base-model size, while an appendix says they are less pronounced at 7B and 14B; the 3B gain is 2.37 and the 7B gain is 3.35.
- The weights are fixed at 0.1 given the compute cost, and no compute-matched comparison against single-agent sampling is reported.

## See Also
- [[Multi-Agent Reinforcement Learning]] — prerequisite-for
- [[Multi-Agent Failure Modes at Scale]] — related
- [[RL Training Frameworks for LLMs]] — related
- [[DAPO]] — related (another GRPO-family fix to length and loss normalization)
