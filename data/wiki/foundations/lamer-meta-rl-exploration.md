---
title: LaMer Meta-RL Exploration
tags: [foundations, llm, pattern]
summary: "LaMer trains a language agent on trials of several sequential episodes with a reflection written after each failure, optimising a cross-episode return; pass@3 beat GiGPO on Sokoban, MineSweeper and Webshop (self-reported) while first-attempt success was mixed."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-jiang-2025-meta-rl-induces-exploration-language.md
---

# LaMer Meta-RL Exploration

LaMer (an ICLR 2026 paper from EPFL and ETH Zurich) targets a known weakness of RL-trained agents: independent rollouts reward immediate success, so the policy narrows and stops exploring. It turns one training unit into a trial of N sequential episodes from the same start.

## Mechanism

- When an episode fails the agent writes a tagged reflection; the reflection is itself trained, receiving credit via the next episode's reward. The trial ends early on success.
- The objective is a cross-episode return: each episode's return adds discounted returns of later episodes, with a discount (gamma_traj) set to 0.6 by default. A small value favours quick exploitation, a larger one favours early exploration.
- Optimisation uses ordinary policy gradients (GiGPO by default). Adaptation at test time happens in context; no gradient step is taken.
- Compute matching: RL uses group size 24 and LaMer uses 3 episodes times group 8. LaMer takes about twice the wall-clock because episodes are sampled in sequence.

## Results (self-reported)

Setup: Qwen3-4B non-thinking, 3 episodes per trial, pass@k meaning k sequential attempts with reflection; single reported values, no seeds.

- Pass@3 compared with GiGPO: Sokoban 55.9 against 44.1; MineSweeper 74.4 against 55.1; Webshop 89.1 against 75.2.
- Pass@1 against GiGPO: 42.4 vs 41.6, 44.1 vs 52.0, 67.8 vs 73.4, so the gain comes from later attempts.
- Giving GiGPO agents memory at test time helped little (pass@3 Sokoban 47.9 vs LaMer 55.9), suggesting the training objective matters.
- Reflection-only memory matched or beat history plus reflection (56.4 / 80.5 / 92.8 pass@3).
- Held-out ALFWorld task types: Cool 81.0 vs 58.1, Pick2 50.2 vs 36.0. A Llama3.1-8B check covered two environments only.

## Limits

- The extraction flags that the abstract's 11, 14 and 19 point gains are listed in a different environment order than Table 1 (11.8 Sokoban, 19.3 MineSweeper, 13.9 Webshop); the table matches the body text. The ALFWorld table also does not state whether it is pass@1 or pass@3.
- The authors concede about 2x training time, untested stronger reasoning models, and transfer only to similar or harder tasks. No dense-reward tasks, no seeds, no models above 8B.
- RL baselines had no cross-episode memory during training; Reflexion and ReAct baselines are untrained prompts.

## See Also

- [[Post-Training for Agents]] — prerequisite-for
- [[DAPO]] — related (also guards against policy collapse)
- [[Self-Learning Agents]] — related
