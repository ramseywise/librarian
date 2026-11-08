---
title: VERA Co-Evolving Model and Harness
tags: [foundations, llm, pattern]
summary: "VERA alternates RL on the model with verified edits to its harness, using thousands of environments with rubric stage rewards; at 9B the full loop beat either axis alone, and at 27B it came within a point or two of frontier models on the benchmarks' default runners (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-liu-2026-vera.md
---

# VERA Co-Evolving Model and Harness

VERA (an October 2026 preprint led from UC Santa Cruz with NVIDIA) treats the model weights and the harness around them as two things to improve together, each round, inside many verifiable environments.

## Mechanism

- **Auto-Rubric environments.** More than 9,000 open environments are built from benchmark trajectories (terminal, software-engineering, ML-engineering and medical sources). Each workflow is cut into five stages that can be restarted independently (plan, setup, verify, execute, submit). Rubrics are yes/no items; where code can check an item, its result beats the judge's score; an agent judge also inspects the workspace.
- **Reward.** Rubric stage scores combine into an end-to-end reward weighted between process and completion; a verified hack zeroes it (a hard gate). Optimisation is GRPO.
- **Acceptance gates.** A new checkpoint is rejected if its development score falls by more than 20% against the last accepted checkpoint. A harness edit must pass a paired rerun showing a gain of at least 5 points, no end-to-end regression and clean safety checks, and each round accepts three edits at most.
- **Rounds.** Five 100-update rounds in the matched baselines.

## Results (self-reported)

Setup: Qwen3.5-9B on the authors' coworker and medical benchmarks (Overall averages agentic and task scores); seed count for the main table unstated.

- Full loop 31.0 (coworker) and 69.1 (medical); harness-only 18.2 and 56.1; model-only 18.9 and 43.3; the strongest single-axis baseline (an automated harness-search method) 20.7 and 55.5; base 4.2 and 19.9.
- Outcome-only GRPO at matched 500 updates collapsed on the coworker benchmark (5.8).
- At 27B with benchmark-default runners: 71.6 against 72.6 for one frontier model on the coworker benchmark, and 80.7 against 81.9 for another on the medical one. Rankings flip with the harness.
- General-capability retention depends on scale: 9B and 4B lose heavily (one math score fell from 92.5 to 36.7), 27B mostly improves.

## Limits

- The extraction notes the abstract's "surpasses" holds against one frontier model only. The harness-search baseline was degenerate (all 27 candidates scored zero, so the first was taken), the COS-PLAY comparison is a scaled-down adaptation, and the harness case study is 1 task of 6 against 0 of 6.
- No seeds or intervals for the main table; judge, verifier and attribution all use one model and its sensitivity is untested; full baselines exist only at 9B; model families differ between 9B and 27B; benchmarks are the authors' own and the Lite core is 40 tasks. The cost curves are illustrative, not measured spend.

## See Also

- [[Post-Training for Agents]] — prerequisite-for
- [[Harness Continual Learning]] — prerequisite-for
- [[AutoHarness Synthesized Code Harness]] — alternative-to
- [[Agent Lightning v1.0 Harnessed Agentic RL]] — related
