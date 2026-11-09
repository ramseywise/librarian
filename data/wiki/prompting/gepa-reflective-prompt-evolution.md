---
title: GEPA Reflective Prompt Evolution
tags: [prompting, pattern]
summary: "GEPA is a prompt optimizer for multi-module LLM systems that has a reflection model read run traces and textual feedback, rewrite one module's prompt, and keep candidates on a per-instance Pareto frontier; the paper reports it beating GRPO on five of six tasks with far fewer rollouts (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-agrawal-2025-gepa.md
---

# GEPA Reflective Prompt Evolution

GEPA asks whether adapting an LLM system through natural-language reflection on its own trajectories can match weight-space reinforcement learning (GRPO) with far fewer rollouts. The paper (ICLR 2026 oral per the extraction) calls the target a **compound AI system**: any modular system of one or more language-model calls, possibly interleaved with tool calls, under arbitrary control flow. Its premise is that language carries more learning signal than a sparse scalar reward. The method needs a **feedback function** that returns textual evaluation traces alongside the score, and the paper's gains rely on it.

## Mechanism

GEPA keeps a pool of candidate prompt sets. Each iteration it:

1. Chooses a parent by sampling over the frontier kept for each validation instance, so a candidate that is best on a single instance remains in the pool.
2. Picks one module, round-robin, and runs the candidate on a minibatch of 3 training examples.
3. Has a reflection model read the traces and feedback and rewrite that module's prompt.
4. Retains the child only when it beats its parent on the minibatch; retained children are then evaluated on the full validation set that defines the frontier.

An optional System-aware Merge step combines modules from two lineages.

## Results

All numbers are the paper's own (self-reported) and come from single runs.

- Qwen3 8B on six tasks (HotpotQA, IFBench, HoVer, PUPA, AIME-2025 and LiveBench-Math), compared with GRPO with LoRA at 24,000 rollouts: GEPA outperformed GRPO by 6% on average (up to 20%) while using as many as 35x fewer rollouts. Aggregate test scores were 45.23 for the baseline, 48.91 for GRPO and 47.84 for MIPROv2.
- Qwen3 8B, IFBench test set: GEPA reached 38.61 after 678 rollouts, against GRPO's 35.88 at 24,000.
- Qwen3 8B, AIME-2025 (30 problems, 5 repeats): GRPO scored 38.00 and GEPA 32.00, the one task of six where GRPO won.
- GPT-4.1 Mini, six benchmarks, equal rollout budget: aggregate gain over baseline was +5.64 for MIPROv2, +6.11 for TextGrad and +3.27 for Trace.
- Qwen3 8B, four tasks, evolution harness fixed: Pareto-based selection gave +12.44 aggregate against +6.05 for always taking the best candidate and +5.11 for beam search with width 4.
- Prompts tuned for Qwen3 8B, then transferred unchanged to GPT-4.1 Mini, outperformed baselines tuned on GPT-4.1 Mini itself.
- Prompts from GEPA and GEPA+Merge were shorter than MIPROv2 prompts by as much as 9.2x.
- Total cost of every GPT-4.1 mini experiment in the main table was under $500; GEPA's own runs cost $86 and MIPROv2's $76.
- Preliminary uses as inference-time search: GPT-4o mean NPU vector utilisation rose from 4.25% to 30.52% on an early NPUEval version, and fast_1 on a 35-task KernelBench subset (V100, GPT-4o) rose from near 0% to above 20%. Adversarial search over AIME 2022-2024 prompts drove pass@1 for GPT-5 Mini on AIME-2025 down from 76% to 10% (5 runs per problem).

## Limits

- The paper reports no seeds, variance or significance tests; each cell is one number.
- GEPA+Merge hurt Qwen3 8B (IFBench 28.23 against 38.61 for GEPA alone; aggregate 52.40 against 54.85); the authors say both models shared one merge configuration and that when to merge needs study.
- Validation scoring consumes the bulk of GEPA's rollouts; the authors name smaller or dynamic validation sets as a future direction.
- GRPO hyperparameters were tuned by hand and its budget is fixed at 24,000 rollouts with LoRA.
- The inference-time search and adversarial results are preliminary.
- The extraction does not name the reflection model.

## See Also
- [[Prompt Optimization]] — prerequisite-for
- [[DSPy]] — related (the benchmark systems were implemented in it)
- [[Coding-Agent Skill Distillation (CASD)]] — alternative-to (compares against GEPA under a shared static rollout pool)
- [[Evaluating Prompts]] — prerequisite-for
- [[Reflexion]] — related (reflection on trajectories in language)
- [[SkillOpt Agent Skill Optimization]] — alternative-to (gated, bounded-edit optimizer for skills)
- [[Harness-R1 Learned Harness Editing]] — related
