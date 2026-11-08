---
title: J1 Reinforcement-Learned Judge
tags: [eval, llm, pattern]
summary: "J1 trains a judge to write out its reasoning before a verdict using online reinforcement learning with a reward for matching the known-better response, plus a consistency reward for answer-order swaps; its 32B model scored 76.8 on PPE Correctness, 10.3 above its base model (self-reported), yet trained pairwise judges still flipped verdicts on 14.5-21.9% of swapped pairs."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-whitehouse-2025-j1.md
---

# J1 Reinforcement-Learned Judge

Whitehouse et al. (arXiv 2505.10320, FAIR at Meta, 2025) ask whether a judge that thinks before
it decides can be trained with online reinforcement learning (compared against offline DPO). In J1 the model reads a pair of responses (or one response), writes a
chain of thought, and gets a reward when its verdict matches the known-better response. Training
uses GRPO with five rollouts per prompt on 22K synthetic preference pairs, and both answer
orders go into every batch.

## The reward design

- **Correctness reward** for a verdict that matches the label.
- **Consistency reward** for giving the same verdict when the two answers are swapped.
- **Pointwise variant.** One response is scored on its own; the score is trained only through
  how it ranks a pair (distant supervision), so absolute score calibration is untested.
- Reward ablation on pairwise J1-Llama-8B: a positive-only reward was best (overall 61.8), with
  a negative reward at 60.4, a format reward at 61.0 and a plan-and-execute seed prompt at 62.1.

## Results (self-reported)

- **PPE Correctness** (12.7K pairs drawn from MMLU-Pro, MATH, GPQA, MBPP-Plus and IFEval;
  accuracy averaged over random response order): the 32B multitask judge scored 76.8 against 66.5 for base Qwen3-32B.
- **Online RL against offline DPO** on the same 22K pairs: J1-Llama-70B 72.9 against 70.2 for
  EvalPlanner-Llama-70B and 59.8 for DeepSeek-GRM-27B trained on 237K pairs; the DeepSeek-GRM row
  is copied from another paper.
- **Five benchmarks** (PPE, RewardBench, RM-Bench, JudgeBench, FollowBenchEval): the 32B judge
  averaged 80.8 against o1-mini 72.7, o3 77.4 and DeepSeek-R1 78.4, but lost individual
  benchmarks (PPE 71.8 against 72.1 and 72.3; JudgeBench 71.4 against 75.7 for o3).
- **Position flips.** J1-Llama-70B on PPE Correctness with greedy decoding: 72.9 and 72.3
  per-order accuracy, but 61.2 position-consistent accuracy and 21.9% flips. Untrained
  Llama-3.1-8B flipped on 44.1% of pairs; training on single-order or both-order data left flips at
  36.7% and 36.8%, and the consistency reward brought them to 28.7%.
- **Pointwise against pairwise.** Pointwise won under the strict consistent metric and
  pairwise under random ordering; the multitask model beat both. Sampling 32 judgments lifted
  pointwise mean-score from 65.0 to 74.8 but pairwise majority vote only from 72.9 to 73.7.
- **Generative against scalar.** On Llama-3.1-8B with the same data, a generative judge
  scored 69.2 overall against 66.6 for a Bradley-Terry scalar reward model, though that
  table's numbers disagree with Table 2.
- **Cost.** Thoughts settled near 500 tokens (pairwise) and 300-400 (pointwise); training used
  8 to 64 A100s.

## Limits

The paper has no limitations section. It reports accuracy against benchmark labels, not
agreement with human raters, and does not break out the human-preference portion of PPE. Only position
bias is measured; for length and name bias the prompt is the sole safeguard. There is no
cost or latency comparison with API judges and no model or code release is stated. JudgeBench
(350 pairs) and FollowBenchEval (205) are small with no intervals, and RewardBench was also the
checkpoint-selection set, so the 0.1-point lead there is weak evidence. The paper's own tables
disagree in places (for example 76.6 against 76.8, and different overall figures for the same
8B row), so per-table numbers should be quoted from the table cited. Baselines are 2024-25 models.

## See Also
- [[LLM-as-Judge Evaluation]] — extends (a trained judge)
- [[LLM Judge Biases]] — related (position bias and its measurement)
- [[Direct Preference Optimization]] — alternative-to (the offline baseline J1 compares against)
- [[Bradley-Terry Preference Model]] — alternative-to (the scalar reward-model baseline)
- [[Prometheus 2 Evaluator Models]] — related (another open judge trained for evaluation)
- [[TIR-Judge]] — extends (adds code execution to a reinforcement-learned judge)
- [[Self-Taught Evaluators]] — alternative-to (rejection-sampled fine-tuning on synthetic pairs)
