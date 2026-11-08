---
title: FrogNano Online Task Synthesis
tags: [foundations, pattern]
summary: Train a 4B coding agent with RL on synthetic tasks regenerated each iteration to match the current policy's solve rate (TaskPilot); five iterations of 300 tasks took SWE-bench Verified from 39.4% to 61.5% with no distillation of trajectories.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-kim-2026-frognano.md
---

# FrogNano Online Task Synthesis

FrogNano (Froggy Team, Microsoft Research Montreal, an October 2026 preprint) trains Qwen3.5-4B as a coding agent. Its data loop is TaskPilot: a stronger model generates a problem statement, a gold patch, plus hidden tests that fail before the fix and pass after it; rollouts from the current policy estimate each task's resolve rate; candidates are then refined, kept or discarded. Iterations 1 to 4 aim at a 0.5 resolve rate. In iteration 5 a stronger generator is used with a band from 0 to 0.5, because a first attempt at iteration 5 gave weaker gains.

## Recipe for the RL updates

DPPO with asymmetric trajectory importance sampling (a token is dropped once its probability has moved more than 0.2 along the direction its advantage favours), a binary test reward, zero-variance groups discarded, and no KL term, entropy bonus or reference model. A success-gated log-length penalty from iteration 3 limits growth in assistant tokens; truncated-but-correct trajectories get 0.5. Each update is 32 tasks with 8 samples; 200 updates per iteration.

## Results (self-reported)

Setup: Qwen3.5-4B, the authors' Leaf harness (five typed tools, natural termination), 150 steps, 131k context, mean of 3 seeds. SWE-bench Verified is also the validation set.

- Verified solve rate over five iterations of 300 tasks each: 39.4 at the start, after iteration one 49.1, after two 53.1, after three 56.7, after four 59.1, and 61.5 at the end. Held-out scores: SWE-bench Pro 37.6%, Terminal-Bench 2.0 31.1%, and PatchEval-Verified 47.3%.
- About 300 real SWE-rebench tasks chosen by the same learnability criterion reached 48.0%. The text does not specify which synthetic iteration this is set against.
- Harness effect: Qwen3.5-4B scored 8.3% under the R2E-Gym harness and 37.2% under Leaf (about 96% of its R2E-Gym trajectories hit the turn limit); MiniMax-M2.5 scored 66.5% on both.
- Run inside mini-SWE-agent, which has one bash tool, FrogNano rose from 43.8% to 56.4%; Leaf was 5.2 points higher.
- Test-time scaling with 3 candidates: a round-robin verifier 62.8% against 61.4% for one verifier call and 61.53% for random choice.
- Of failures on Verified, 90.8% were reasoning gaps and 7% were early stops. A regex pass flagged 21.3% of trajectories and a three-judge majority confirmed 2.5% as attempted hacks; the scaffold blocked all of them.
- Cost about $0.21 per task at 131k context and 53.5 steps, estimated from a token-budget model and list prices rather than billing.

## Limits

- English tasks and Python-heavy repositories; generalisation to other languages, tool interfaces or budgets is not established. Tests cover part of program behaviour, so a passing patch can be wrong or insecure.
- No ablation separating learnability-frontier calibration from plain difficulty filtering, nor DPPO against GRPO or the length penalty in numbers. No error bars in the text.
- Gains at iteration 5 cannot be separated from the new generator and the changed target band. Verified is both validation set and checkpoint-selection set, so selection leakage is possible.
- Comparisons use the authors' Leaf harness; frontier numbers come from reports. Task content comes from stronger models, so only trajectories are distillation-free.
- By the authors own account, no single piece of the RL setup is new.

## See Also

- [[Post-Training for Agents]] — prerequisite-for
- [[DAPO]] — related
- [[Composer 2 Training Recipe]] — related
- [[Tool Design as Harness Surface]] — related
- [[DreamGym Synthetic Experience RL]] — alternative-to
- [[AutoGym Blueprint-First Verifiable Gyms]] — alternative-to
- [[AgenticQwen Dual Data Flywheels]] — alternative-to
