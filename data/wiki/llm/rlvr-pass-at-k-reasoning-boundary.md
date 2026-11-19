---
title: RLVR Pass@k Reasoning Boundary
tags: [llm, reinforcement-learning, concept]
summary: "Yue et al.'s pass@k study of whether RL with verifiable rewards gives a model reasoning ability beyond its base model: at large k the base model catches up with and overtakes the RL model, and distillation behaves differently."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-yue-2025-does-reinforcement-learning-really-incentivize.md
---

# RLVR Pass@k Reasoning Boundary

Yue et al. (2025, preprint, arXiv v5) test whether RL with verifiable rewards (RLVR: a deterministic verifier returns a binary reward) gives LLMs reasoning ability beyond the base model, or only makes paths the base model already has more likely to be sampled. They hypothesise that RLVR makes sampling more efficient while the ceiling stays set by the base model, which would mean base models equal or exceed RL models at large pass@k. Under pass@k a problem counts 1 when any of its k samples satisfies the verifier; the dataset average is the fraction of problems solved within k attempts. The Sampling Efficiency Gap (delta SE) is the RL model's pass@1 minus the base model's pass@256. Zero RL means RL applied directly to the base model with no SFT.

## Method

Base models are compared against RLVR checkpoints that others released (among them SimpleRLZoo, Oat-Zero, DAPO, Code-R1, DeepCoder and EasyR1) across math, code and visual benchmarks with k reaching 1024. The authors also ran six RL algorithms themselves in VeRL on Qwen2.5-7B, and add analyses of accuracy histograms, overlap between solvable sets, the base model's perplexity on RL responses, and a distillation comparison.

## Results (self-reported)

- Qwen2.5-32B base against a SimpleRLZoo GRPO model on Minerva, temperature 0.6: at k=128 the base solves about 9% more problems.
- SimpleRLZoo Qwen2.5-7B, AIME24, k=1024: 13.3% of problems solved only by the base model, 0.0% only by the RL model. MATH500, k=128: 3.6% only base, 1.0% only RL.
- Own GRPO run, Qwen2.5-7B on Omni-MATH-Train: pass@1 climbs from 26.1 to 42.5 between steps 150 and 450 while pass@256 declines. On Omni-MATH-Test, by step 450, pass@1 has gone from 10.2 to 28.3 yet pass@256 has dropped from 69.1 to 63.9.
- delta SE stays above 40 points for all six algorithms on Omni-MATH-Test.
- On Minerva, the distilled DeepSeek-R1-Distill-Qwen-7B stays above its base Qwen2.5-Math-7B across the pass@k curve, which the RL model does not.
- More rollouts (n=32 against 8) improve pass@k slightly but the base still overtakes. A KL term of 0.001 gives similar pass@1 but much lower pass@128. Matching the RL model's entropy to the base by raising its temperature shrinks the gap without removing it.
- In the VeRL runs DAPO consumed roughly 3 to 6 times the samples per batch of the other algorithms and fell off markedly at k=256.
- Magistral-Medium, trained with RLVR, at k=1 gets about 7 additional AIME24 and 8 additional AIME25 problems right compared with Mistral-Medium-3, and the difference shrinks with larger k (API access, 40k context).
- Manual chain-of-thought check on GSM8K problems whose average accuracy is strictly between 0% and 5%: base 24 of 25 had a correct chain, RL 23 of 25.

Code and visual-reasoning results are reported to follow the math pattern.

## Limits

- Only open-source pure-RLVR models could be tested; the authors note newer techniques may mitigate the findings and that scaling RLVR to pretraining scale is left open.
- Most evidence is released checkpoints whose recipes the authors did not control; their own controlled runs are Qwen2.5-7B on Omni-MATH only.
- Each model was sampled once, with no confidence intervals or seeds. Math pass@k may reward lucky guesses; the authors checked validity by hand on small subsets (25 GSM8K, 7 AIME24 and 8 visual problems).
- DeepSeek-R1-Zero was not evaluated, and the code and vision tasks begin from instruction-tuned models instead of zero RL.

## See Also
- [[GRPO Group Relative Policy Optimization]] — prerequisite-for (the DeepSeekMath paper observed Maj@K up and Pass@K flat on one model)
- [[DAPO]] — related (its checkpoint and algorithm were tested)
- [[Outcome vs Process Reward Models]] — related
- [[Cognitive Behaviors for Self-Improving Reasoners]] — related (which base-model properties let RL help)
- [[Reward Hacking and Overoptimization]] — related
