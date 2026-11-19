---
title: PAPO Process Rewards for Diffusion LLMs
tags: [llm, reinforcement-learning, concept]
summary: "PAPO gives each denoising step of a diffusion LLM a reward (the task reward of the one-step denoised completion) and updates the policy on states re-enacted from the real rollout, applied as GRPO-style RL to LLaDA-8B-Instruct."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-06-shao-2026-back-track.md
---

# PAPO Process Rewards for Diffusion LLMs

Shao (2026, preprint, arXiv 2606.08501v2) applies GRPO-style RL to diffusion LLMs, where the paper says sparse terminal rewards are assigned indiscriminately to all intermediate generation steps. PAPO combines two pieces. **Step-Aware Process Rewards (SPR)** give denoising step t the reward `Rp_t = R(x0_hat(t))`, i.e. the task reward evaluated on the one-step denoised completion drawn from the old policy; the final outcome reward is topped up with it, with no separate learned reward or value model. **Entropy-Guided Historical Re-enactment (EHR)** fits the policy on states drawn from the actual rollout, drawing them with probability proportional to step entropy to the power alpha (alpha 0 means uniform; a larger alpha leans toward uncertain steps). Per the extraction, this process reward is just the outcome reward computed on a one-step guess and does not verify that a step is correct.

## Setup and results (self-reported)

Setup: LLaDA-8B-Instruct trained by RL with no SFT stage, LoRA rank 128, on 8 A100-80G GPUs. Rollouts are 256 long and evaluation uses lengths 128, 256 and 512. Other settings are alpha 1, mu 12, learning rate 3e-6 and 8000 steps (6000 on Sudoku).

- The paper states a mean absolute gain of 16.9% over the base model. Table 1 gives gains at lengths 128, 256 and 512 (in that order) for four tasks. Sudoku: +15.5, +18.3, +14.7. Countdown: +31.3, +46.1, +49.2. MATH500: +7.4, +3.2, +3.8. GSM8K: +5.1, +5.7, +2.6.
- Countdown at length 256 puts PAPO at 65.6, ahead of UniGRPO (53.9), SAPO (52.0), diffu-GRPO (31.3) and the base (19.5). PAPO is not best everywhere: SAPO beats it on GSM8K at 512 (82.4 to 80.8) and on MATH500 at 256 (40.0 to 35.6).
- Ablation on Countdown at 256: SPR alone 55.5; uniform historical states alone 56.6; EHR alone 57.5; uniform states with SPR 60.6; EHR with SPR 65.6.
- GSM8K at length 128: 16-step lookahead gives +1.6% for +44% GPU hours, so one-step SPR is the paper's trade-off.
- On LLaDA-1.5 Countdown at 256, PAPO 68.8 against diffu-GRPO 29.7; on an SDAR block-diffusion model a task score rises from 2.65% to 19.99% against 13.32% for diffu-GRPO.

## Limits

- The authors admit the process reward relies on the one-step denoised prediction, which may break down for few-step or fast decoders; only text benchmarks were run.
- Checkpoint choice comes from evaluating every 100 steps starting at step 600, which introduces selection effects. There is one 8B base with LoRA, apparently one seed, and no variance reported.
- The abstract's 42.2 and 16.1 gains correspond to no single delta in Table 1, and the extraction could not reconcile them.
- UniGRPO and diffu-GRPO on 9x9 Sudoku are the authors' re-implementations; efficiency claims are curves only; the SPR synergy argument is prose with no separate control.

## See Also
- [[GRPO Group Relative Policy Optimization]] — prerequisite-for (the base algorithm)
- [[Outcome vs Process Reward Models]] — related (step-level reward, here not a learned model)
- [[SDPO Self-Distillation Policy Optimization]] — related (another dense-credit alternative to scalar rewards)
- [[LLaDA Large Language Diffusion Model]] — related
- [[Block Diffusion Language Models]] — related
