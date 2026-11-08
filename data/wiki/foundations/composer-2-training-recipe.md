---
title: Composer 2 Training Recipe
tags: [foundations, concept]
summary: "Cursor's coding model: continued pretraining of Kimi K2.5, then RL in the production harness with Dr. GRPO-style updates, self-summarization trained end to end and a length penalty; scored on the internal CursorBench-3."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-research-2026-composer-2-technical-report.md
---

# Composer 2 Training Recipe

Composer 2 (Cursor Research, a March 2026 technical report) starts from Kimi K2.5, a 1.04T-parameter mixture-of-experts model with 32B active. Base-model choice used FreshBench, state tracking and codebase perplexity rather than agent benchmarks, because the authors say agentic ability changes a lot during RL.

## Stages

- **Continued pretraining:** most compute at 32k sequence length, a stretch to 256k context, and finally a brief SFT pass on coding tasks. Layers that predict several tokens at once are trained with self-distillation, which serves speculative decoding. On a different model (Qwen3-Coder-30B-A3B), three compute levels showed post-SFT loss predicting RL reward; the paper calls the link an active research area.
- **RL:** policy gradient with a fixed group size and a single epoch, following Dr. GRPO (no length normalisation, no division by group standard deviation, overlong rollouts not masked), with the k1 KL estimator rather than k3. Async stability comes from fast weight sync, in-flight weight updates and MoE router replay.
- **Self-summarization:** one rollout chains several generations linked by summaries, and the final reward reaches every token including summary tokens. The authors report it reduces error against separate prompt-based compaction with fewer tokens, with no number given.
- **Train-test match:** RL runs in the same Cursor harness and tools as production, on real session categories, in Firecracker VMs.
- **Behaviour shaping:** auxiliary rewards for style and communication, penalties for poor tool use, and a concave increasing length penalty over a weighted mix of token and call counts; its hyperparameters are not given.

## Results (self-reported)

Composer models are scored in Cursor's own harness. Composer 2 scored 61.3 on CursorBench-3 and 61.7 on Terminal-Bench, plus 73.7 on SWE-bench Multilingual, against 44.2, 47.9 and 65.9 respectively for Composer 1.5. Kimi K2.5 scored 36.0 on CursorBench and 47.3 on Terminal-Bench; GPT-5.4 scored 63.9 on CursorBench and Opus 4.6 High 58.2, with refused GPT problems scored as 0. RL raised both average reward and best-of-K, shown as curves only. CursorBench-3 is internal; its median edit is 181 changed lines against 7 to 10 for the public SWE-bench variants.

## Limits

- No ablations: nothing separates continued pretraining from RL, and the algorithm choices have no numeric training curves. RL compute, steps and group size are not given.
- CursorBench is internal and unreleased; headline gaps to other models are a few points, and third-party runs scored refusals as 0.
- The best-of-K claim has no numbers or baseline RL recipe. Scores are valid as of March 2026.

## See Also

- [[Post-Training for Agents]] — prerequisite-for
- [[DAPO]] — related
- [[FrogNano Online Task Synthesis]] — related
- [[Harness Engineering]] — related
- [[AgenticQwen Dual Data Flywheels]] — related
- [[KARL Multi-Task RL Knowledge Agents]] — related
