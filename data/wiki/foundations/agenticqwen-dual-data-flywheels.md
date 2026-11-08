---
title: AgenticQwen Dual Data Flywheels
tags: [foundations, llm, pattern]
summary: "AgenticQwen trains small tool-use models with GRPO over three rounds on data from two loops, one that expands failed math problems and one that grows tool workflows into behaviour trees; the 8B model averaged 47.4 against 23.8 for its base (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-lyu-2026-agenticqwen.md
---

# AgenticQwen Dual Data Flywheels

AgenticQwen (Alibaba, an April 2026 preprint) is a recipe for small agentic models. Its premise, asserted rather than ablated, is that a single RL round on a large static synthetic set saturates because the samples are homogeneous. It instead regenerates data each round from the current model's failures.

## The two flywheels

- **Reasoning flywheel.** Collect problems the model fails, expand only the math ones with self-instruct and persona injection, and keep a new problem only if a 235B model gives the same answer in all three solves.
- **Agentic flywheel.** Start from a linear tool workflow, have a larger LLM expand it into a behaviour tree, invert each branch into a task, and add an adversarial mock user who pushes toward a non-compliant path. A synthesized task is retained only if a strong model solves it in the simulated environment along the intended branch.
- **Reward and optimiser.** The reward is the fraction of rubric subgoals completed, scored in [0,1] by the 235B model; GRPO is the optimiser. About 100K training samples; three rounds, after which the authors stop because gains diminish.

## Results (self-reported)

Setup: non-thinking mode with tools; three tau2 domains (about 300 tasks, Avg@4) and BFCL-V4 multi-turn (about 800 tasks); average over seven columns.

- 8B: 47.4 against 23.8 for Qwen3-8B and 52.0 for Qwen3-235B-A22B. 30B-A3B: 50.2 against 36.2.
- The 30B-A3B beats the 235B on three BFCL columns (for example Miss Func 52.0 vs 47.5); the authors note it is an MoE model with 3B active parameters.
- Deep-search pilot with under 10K search examples: XBench 47.0 against 30.0 for the vanilla 30B and 48.0 for the 235B; GAIA 41.7, 37.3 and 48.5 for the same three models in that order.
- On GAIA the 30B ran in 344.1 s against 449.5 s for the 235B; the "fewer unnecessary steps" explanation is the authors' guess.

## Limits

- No ablations: no single-round or static-data control, no run without the adversarial user, no flywheel-by-flywheel split. Round 0 is the untrained model, so the round curve cannot separate more rounds from harder data.
- The 235B model is synthesizer, user and tool simulator, and grader, so "approaching the strong model" is partly circular; the authors concede model-family bias. Baselines are only vanilla Qwen3 models; tau2 samples are small and unreplicated.
- The production pilot is internal and routes only tasks predicted to be in range. Open-ended and long-context tasks stay hard under a 40K-token limit.

## See Also

- [[Post-Training for Agents]] — prerequisite-for
- [[FrogNano Online Task Synthesis]] — alternative-to (regenerates tasks to match the policy's solve rate)
- [[APIGen]] — prerequisite-for
- [[DreamGym Synthetic Experience RL]] — related
