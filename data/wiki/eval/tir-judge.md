---
title: TIR-Judge
tags: [eval, llm, pattern]
summary: "TIR-Judge trains a judge that writes and runs Python while judging, using end-to-end reinforcement learning; on RewardBench2 listwise best-of-4 its 8B Zero variant averaged 73.4 against 76.5 for Claude-Opus-4 (self-reported), while merely prompting Qwen3 with the same code tool gave negligible or negative gains."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-xu-2025-incentivizing-agentic-reasoning-llm-judges.md
---

# TIR-Judge

Xu et al. (arXiv 2510.23038, 2025, preprint) train a judge model that writes and runs Python code during judging, so that counting words or letters, checking constraints, arithmetic and running tests are done exactly by code. The model is also trained to skip the tool where it does not help, such as safety and general helpfulness prompts. The authors' motivation is that most judges rely on text-only reasoning, which limits verification of complex constraints and exact computation.

## Variants

- **TIR-Judge-Zero:** no distillation; a loop of reinforcement learning, rejection sampling, supervised fine-tuning, then reinforcement learning again.
- **TIR-Judge-Distill:** supervised fine-tuning on about 10k Gemini-2.5-Flash tool trajectories, then reinforcement learning.

Both use Qwen3-8B or Qwen3-4B-Instruct-2507 backbones and about 26k training pairs (26,361). The reference answer is unseen at evaluation time.

## Results (self-reported)

- **Headline.** The abstract claims gains over strong reasoning-based judges of up to 6.4% (pointwise) and 7.7% (pairwise) across seven benchmarks; see Limits on the unit.
- **PPE Correctness.** It beats similar-size baselines by 4.8 to 9.9% pointwise and 4.5 to 8.8% pairwise, and matches RRM-32B on PPE and RewardBench with a quarter to an eighth of the parameters.
- **RewardBench2, listwise best-of-4, 5 subsets.** Zero 8B averaged 73.4; Claude-Opus-4 76.5, Gemini-2.5-flash-Preview 75.9, Distill 8B 71.6, GPT-4.1 69.7, Claude-Sonnet-4 69.5, GPT-4o 64.9. On the IF subset Distill 8B scored 58.1 against 41.9 for Opus-4; Opus-4 led on Fact, 82.7 against 64.8 for Zero 8B.
- **Tool alone.** Prompting Qwen3 with the same code tool gave negligible (under 1%) or negative gains; Qwen3-8B-Tool averaged 59.4 pointwise against 64.9 for plain Qwen3-8B. The authors conclude that reinforcement learning is what unlocks tool use.
- **Best-of-N.** On AIME and BigCodeBench, Zero gained 3.9 to 6.7% absolute over RRM-7B (16 samples per problem, 16k token limit). On BigCodeBench Deepseek-Coder (1,139 problems), 285 pass at Pass@1, 328 with majority vote over 16, and 435 with the 4B pointwise Zero judge.
- **Cost, 8xH100.** Zero took 29.0 hours and about $690; Distill 11.0 hours and about $340 ($210 compute plus $130 teacher API).

## Limits

Tools are code execution only, and gains concentrate in verifiable tasks (instruction following, math, code); text-only judges did slightly better on Chat and Safety in RM-Bench. Gemini-2.5-Flash sometimes got worse with tools because of the max-turn limit and runaway tool calls. Accuracy only: no evaluation of bias, position bias or calibration, and pairwise uses a single random ordering. Training data includes synthetic pairs from Qwen3 and Gemma, labelled with the benchmark's ground-truth reward model; eight-gram decontamination was applied. Only Qwen3 4B and 8B; some baseline numbers are copied from other papers; several baselines above 10B still score higher on many benchmarks. The authors do not claim a way to detect when a tool is needed beyond a no-tool format heuristic for safety and helpfulness. Single run, no variance reported.

Internal inconsistencies: the paper does not say whether the 6.4% and 7.7% are absolute points or relative. Its introduction says Zero gains 1.2% over Distill at 4B, but Table 1's 4B pairwise averages (73.7 against 70.5) do not match that figure, and at 8B pairwise Distill leads (72.6 against 72.0); check the 1.2% before citing it.

## See Also
- [[J1 Reinforcement-Learned Judge]] — alternative-to (a reinforcement-learned text-only judge)
- [[LLM-as-Judge Evaluation]] — extends (a judge that runs code)
- [[Tool-Augmented Factuality Checking]] — related (checking with tools instead of text reasoning alone)
- [[LLM Judge Biases]] — related (bias was not evaluated here)
