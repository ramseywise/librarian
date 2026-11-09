---
title: Conductor Learned Orchestration
tags: [harness, pattern]
summary: The Conductor is a 7B model trained with GRPO on correctness alone to write a whole multi-agent workflow in natural language (a subtask, a worker id and an access list per step); it scored 77.27 average against GPT-5's 74.78 on its authors' table, with gains of a few points on unseen tasks (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-nielsen-2025-learning-orchestrate-agents-natural-language.md
---

# Conductor Learned Orchestration

Nielsen et al. (Sakana AI and universities, arXiv 2512.04388 v5, ICLR 2026) train a small model to
design the workflow that a pool of stronger worker models executes. Selecting among routers or
aggregation baselines (MoA, MASRouter and similar) is covered elsewhere; the point here is the output
format and the training signal.

## Mechanism

A Qwen2.5-7B base model emits up to five steps. Each step has a free-text subtask string, an
integer worker id, and an access list naming which earlier steps' outputs the worker sees (all or
none in the chosen version, so a tree is a run of empty-list workers followed by an aggregator
with the list "all"). Training is 200 GRPO iterations on 960 problems drawn from MATH, MMLU, RLPR and
LiveCodeBench v1, rewarding correctness only, with no cost term, on 2 H100 GPUs. The worker pool of 7
consists of three proprietary models (GPT-5, Claude Sonnet 4, Gemini 2.5 Pro) and open ones (R1-Distill-Qwen-32B, Gemma3-27B, Qwen3-32B), run in thinking
and in non-thinking modes. A recursive variant can list itself among the workers and is shown its earlier
output; returning three empty lists accepts the prior answer.

## Results (self-reported)

- **Main table.** Average 77.27 against GPT-5 at 74.78, including LiveCodeBench 83.93, GPQA-Diamond
  87.5 and AIME25 93.3. For baselines the authors took the best of their own re-evaluations, private
  implementations and leaderboards, and the leaderboard figures may involve undisclosed prompting. The authors tie the
  AIME25 and GPQA gains to a range near 3%; those sets have 30 and 198 questions.
- **Controlled setting.** Workers capped at 4096 tokens (the setting used in training), over four
  tasks, up to 16 repeats: average 72.35 against MoA 62.13, MASRouter 56.89, the best single worker 64.14
  and best 5x self-reflection 64.52. It used about three steps on average, with no length penalty.
- **Cost.** On MMLU alone: it scored 93.14 at $0.009 per sample (735.2 tokens), while GPT-5 5x consensus scored 91.30 using 1376.3
  tokens and $0.0138. Two of the multi-agent baselines cost less, so it is not the
  cheapest.
- **Learned shapes.** Mostly chains, trees and plan-implement-verify sequences, with step count
  growing with difficulty (MMLU typically 2 agents, LiveCodeBench 3 or 4); categories were assigned
  by hand and called rough.
- **Ablations (single runs, no standard errors).** LiveCodeBench 64.29 full, 58.62 without subtasks and
  54.86 without few-shot examples. A finer access list gave 61.24 against 64.29. Out-of-domain
  few-shot examples scored 64.29 against 58.32 for in-domain, with the authors' hypothesis being more
  exploration. A prompted Gemini 2.5 Pro as orchestrator scored 70.29 on LiveCodeBench against 83.93.
- **Recursion.** Average 61.93 to 63.00 in the constrained setting after 20 further iterations on 350 samples.
- 3B and 7B Conductors converged on similar worker distributions; the authors attribute the 7B's
  edge to better subtask prompts.

## Limits

- Table 1 mixes baseline sources, so it does not compare like with like; the controlled tables are
  the fairer ones. The method relies on expensive frontier workers, which the authors concede.
- Topology is sequential steps with all-or-nothing context. Training covers 960 problems in four
  families and evaluates reasoning, coding and QA only, with no tool-using agents. The paper says little
  about how the learned topologies fail beyond verifier formatting failures and MoA
  being misled.
- No fixed generate-then-verify topology designed by hand is compared on the same workers,
  apart from MoA. Workers are 2025 models.
- Internal inconsistencies noted by the extraction: GPT-5's average is 51.73 in one table and 51.07 in
  another; the Conductor's average is 72.89 in one table and 75.65 in another (different task sets);
  row labels in the orchestrator-comparison table do not match its text labels.
- Figure values (including the open-models-only result "almost 10%" over Claude Sonnet 4) were not extracted.

## See Also
- [[Harness Orchestration]] — prerequisite-for
- [[Multi-Agent Topology Patterns]] — prerequisite-for
- [[SALE Strategy Auction]] — alternative-to (a different way to assign agents to tasks)
- [[Task Decomposition Patterns]] — related
- [[Sakana Fugu Learned Orchestration]] — alternative-to (learned orchestrator, different training)
- [[AgentConductor Topology Evolution]] — alternative-to
