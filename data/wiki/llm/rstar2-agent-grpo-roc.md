---
title: rStar2-Agent GRPO-RoC
tags: [llm, agent-training, pattern]
summary: "Resample-on-Correct keeps a binary answer-only reward for tool-integrated math RL and cleans up trajectory quality by choosing which rollouts to train on; a 14B model trained this way reports frontier-level AIME pass@1 in 510 steps (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-06-shang-2025-rstar2-agent.md
---

# rStar2-Agent GRPO-RoC

rStar2-Agent (Microsoft Research, August 2025) trains a model to reason with a Python tool over multiple turns. Its central design choice is to leave the reward alone and change which rollouts reach the gradient. The reward is binary and answer-only: a rule-based math checker scores the `\boxed{}` answer, and only integer-answer problems are used because verifiers fail on equivalent algebraic expressions.

## The problem with an outcome-only reward

A trajectory whose tool calls failed still earns reward 1 if its final answer is right. Under naive GRPO with a Python tool, the share of tool errors inside positively rewarded trajectories falls at first and then plateaus: about 15% for Qwen2.5-32B and about 10% for Qwen3-14B. The authors reject step-level rewards and tool-error penalties. Their reasons are tuning and reward-model complexity and reward-hacking risk, and they note that early in training such penalties can block exploration.

## GRPO-RoC (Resample-on-Correct)

1. Oversample 2G rollouts per prompt (32) and keep G (16).
2. Downsample the negative rollouts uniformly, which preserves the variety of failures.
3. Positive rollouts are drawn with a probability that shrinks as the penalty `p_total` (the sum `p_err + p_format`) grows. `p_err` is the fraction of tool calls that errored, and it defaults to 0.5 for a trajectory with no tool calls to encourage tool use. `p_format` penalises several `<answer>` tags, and a missing tag gets the maximum downsampling weight.

Half of the positives are drawn this way, so the kept positives are cleaner trajectories while the reward stays 0/1.

## Other recipe changes

- GRPO is modified by removing the KL penalty, raising the upper clip bound from 0.2 to 0.28 (the Clip-Higher idea from [[DAPO]]) and dropping the entropy loss; training samples at temperature 1.0.
- Tool interface: function calls are JSON wrapped in `<tool_call>` tags, answered inside `<tool_response>` tags. One of four outcomes comes back (stdout, success with no output, an error with traceback, or a timeout), and malformed JSON yields a parse error. A maximum turn count T bounds a rollout.
- Schedule: non-reasoning SFT first (165K function-call, 30K instruction-following and 27K chat examples), then three RL stages with max response lengths 8K, 12K and 12K tokens. Stage 3 drops problems the model solved 8 of 8 times, leaving 17.3K of the 42K curated problems. The RL pool was cleaned from over 100K problems using Qwen3-32B with 16 samples each.
- Two tried-and-dropped ideas: n-gram repetition detection as a scoring term hurt response length and reasoning because it flagged legitimate repeated verification calls, and DAPO-style overlong filtering gave no benefit and raised the overlong ratio, whereas keeping truncated rollouts with negative reward helped.
- Infrastructure: an isolated code-execution service serves up to 45K tool calls per step, 0.3 s on average per call (the paper's text prints "45 calls per step", probably a typo), and a scheduler assigns rollouts by available KV-cache capacity instead of evenly, because an even split leaves GPUs idle behind the longest rollout and makes SGLang evict and recompute in-progress rollouts. Built on VERL and SGLang.

## Reported results (self-reported)

Setup: Qwen3-14B-Base, trained for 510 RL steps over about a week on 64 MI300X GPUs, 16 samples per question, average pass@1, 30K max tokens, temperature 0.6.

| Benchmark | rStar2-Agent-14B | o3-mini | DeepSeek-R1 |
|---|---|---|---|
| AIME24 | 80.6 | 79.6 | 79.8 |
| AIME25 | 69.8 | 77.0 | 70.0 |
| HMMT25 | 52.7 | 53.0 | 44.4 |

- Average response length on AIME24/AIME25 is 9,339.7 / 10,943.4 tokens against 14,747.6 / 17,521.9 for Qwen3-14B.
- Against no-tool DAPO at the same base, Qwen3-14B: DAPO after 2,000 steps scores 45.2 / 38.1 on AIME24/25, the tool-using model after 510 steps 80.6 / 69.8. On Qwen2.5-32B (stages 1-2 only, 700 steps) the model scores 94.8 MATH-500, 69.4 AIME24 and 57.3 AIME25, against 93.4 / 67.0 / 49.3 for ReTool-32B at 400 steps.
- Stage 1 alone lifts AIME24 from 3.3% (post-SFT) to 72.1%.
- Math-only RL transferred to GPQA-Diamond (42.1 to 60.9) but not to tool use or alignment: BFCL v3 went from 63.1 to 60.8, IFEval 83.7 to 83.4, Arena-Hard 86.8 to 86.6.
- Qualitative entropy analysis: high-entropy tokens are forking phrases ("But before", "double-check") and reflections on tool responses; the tool-call code itself is low entropy.

## Limits

- Only math was tested, with Python as the one tool; whether it carries to other tools is stated as open. Integer answers only.
- Stage 3 saturates and collapses after about 510 steps. Raising temperature to 1.2, lengthening responses, raising T from 10 to 20, raising the clip bound and resetting the optimizer all failed to prevent it; the cause is only hypothesised (a capacity ceiling).
- The RoC ablation is 300 steps in one setup with no seeds, and no test separates `p_err` from `p_format`. The cost of generating 2G rollouts and the scheduler's speed-up are not quantified.
- Comparisons across papers differ in step counts and settings. o3-mini beats it on AIME25 and HMMT25. The introduction claims strong agentic tool use on BFCL v3, yet the score fell from 63.1 after SFT to 60.8 (it still exceeds DeepSeek-V3's 57.6).
- Published August 2025; later results may have passed these standings.

## See Also
- [[DAPO]] — prerequisite-for
- [[GRPO Group Relative Policy Optimization]] — prerequisite-for
- [[Post-Training for Agents]] — prerequisite-for
- [[Tool-N1 Binary-Reward Tool-Calling RL]] — alternative-to (binary reward; this page filters rollouts instead)
- [[Outcome vs Process Reward Models]] — related
- [[RL Training Frameworks for LLMs]] — related
