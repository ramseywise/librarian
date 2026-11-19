---
title: GDPO Decoupled Reward Normalization
tags: [llm, reinforcement-learning, concept]
summary: "GDPO normalises each reward separately within the rollout group, sums the per-reward advantages, then normalises over the batch, because summing rewards before GRPO's group normalisation collapses distinct reward combinations into identical advantages."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-liu-2026-gdpo.md
---

# GDPO Decoupled Reward Normalization

Liu et al. (2026, preprint) ask whether GRPO suits multi-reward RL. Their hypothesis is that summing rewards before group normalisation maps different reward combinations to the same advantage, and that normalising each reward on its own restores the distinction. In their worked example (two binary rewards, two rollouts), GRPO maps the six reward combinations onto just two distinct advantage groups, whereas GDPO yields three.

## Mechanism

1. For each reward k, subtract the group mean and divide by the group standard deviation.
2. Add the resulting per-reward advantages together, with optional weights w_k.
3. Standardise that sum across the batch (subtract the batch mean, divide by the batch standard deviation plus a small epsilon).

A conditioned reward counts reward k only if another reward r_l is at least a threshold t, and is 0 otherwise; the paper takes its conditioned length reward from earlier work. Baseline GRPO is [[GRPO Group Relative Policy Optimization]]; the paper's runs use the verl framework.

## Results (self-reported)

- Tool calling (Qwen2.5-Instruct 1.5B and 3B, 100 steps, 5 runs): GDPO is ahead of GRPO on mean BFCL-v3 accuracy. A GRPO variant without std normalisation reached 0% format correctness despite a similar correctness reward.
- Length-constrained math (DeepSeek-R1-1.5B, 4000-token target, 500 steps): AIME accuracy is 29.8 for the base model, 23.1 for GRPO and about the base level for GDPO. The share of AIME answers over the length limit drops from 91.5% (base) to 6.5% under GDPO, 10.8% under GRPO.
- DeepSeek-R1-7B (500 steps) scores 55.4 base, 50.2 with GRPO, 53.1 with GDPO; Qwen3-4B-Instruct scores 63.7, 54.6 and 56.9 in the same order.
- Coding (DeepSeek-R1-7B trained on Eurus-2-RL for 400 steps): with two rewards GDPO lifts the Taco pass rate over GRPO; with three it reduces Codeforces over-length and bug ratios at a comparable pass rate.
- In tool calling over 100 steps, dropping the batch-level normalisation makes GDPO sometimes fail to converge.
- Lowering the length-reward weight to 0.75 or 0.5 hardly moves the over-length ratio, so the weights are an unreliable priority control when the objectives differ in difficulty.

## Limits

- Only three task families and models of at most 7B, all run in verl; the math and coding runs state no seeds and there are no significance tests.
- In the length-constrained math setting both methods end below the untrained model on AIME.
- The batch-norm epsilon, optimizer, hardware and compute are missing.
- GRPO's collapse near step 400 appears on one family of training curves, and the text discusses only the 1.5B one.

## See Also
- [[GRPO Group Relative Policy Optimization]] — prerequisite-for (the group normalisation GDPO splits per reward)
- [[DAPO]] — related (its dynamic sampling, clip-higher and token-mean loss are used in the paper's setup)
- [[GSPO Group Sequence Policy Optimization]] — alternative-to (changes the importance ratio, not the advantage)
- [[Tool-N1 Binary-Reward Tool-Calling RL]] — related (tool-calling RL with a binary reward)
