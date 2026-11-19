---
title: GSPO Group Sequence Policy Optimization
tags: [llm, reinforcement-learning, concept]
summary: "GRPO with the importance ratio and clipping moved from tokens to whole responses, proposed to stabilise RL on large mixture-of-experts models without Routing Replay; the evidence is training curves on one Qwen3-30B-A3B-Base run."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-zheng-2025-group-sequence-policy-optimization.md
---

# GSPO Group Sequence Policy Optimization

Zheng et al. (2025, preprint) ask why GRPO becomes unstable when training large mixture-of-experts language models on long responses. Their hypothesis is that the unit of the optimisation objective should match the unit of reward. GSPO replaces GRPO's per-token importance ratio (see [[GRPO Group Relative Policy Optimization]]) with a single ratio per sequence, the likelihood ratio of the whole response raised to 1/|y| (`s_i`, length-normalised), and applies clipping to complete responses instead of individual tokens.

## Variant and routing

GSPO-token is a variant that allows a per-token advantage; it is numerically identical to GSPO when the advantages are equal. Routing Replay is the stabiliser GRPO needs on mixture-of-experts models: it caches the experts activated under the old policy and replays that routing when computing importance ratios. The paper reports that GSPO trains stably without it.

## Results (self-reported)

Every result is a training curve from single runs of a cold-start model derived from Qwen3-30B-A3B-Base:

- After every gradient update, roughly a tenth of the activated experts change for an identical rollout (48-layer model); the authors cite this as what unsettles GRPO's token-level ratios.
- Averaged over training, GSPO clips about 100 times as many tokens as GRPO (0.15 versus 0.0013, taken from figure labels and text) and still trains more efficiently.
- At equal compute GSPO is reported to beat GRPO with Routing Replay on AIME'24, LiveCodeBench, CodeForces and training reward; no numeric table accompanies this.
- GRPO on the mixture-of-experts model does not converge normally when Routing Replay is removed.
- The authors describe GRPO's collapse as permanent, surviving checkpoint reverts and clip-range tuning, and blame misapplied token-level importance weights; no ablation backs this.
- They also propose, without testing it, that GSPO could use inference-engine likelihoods directly and skip recomputation.

## Limits

- One model, curves only: no tables, seeds or error bars.
- The only baseline is GRPO with Routing Replay, so other stabilisers such as [[DAPO]] and dense models are not compared.
- The paper omits learning rate, group size, batch size, step count, data and hardware, and its compute axis has no units.
- The infrastructure benefit is argued rather than measured, and no ablation isolates what causes the collapse.
- GSPO's authors are also the team that used it for Qwen3.

## See Also
- [[GRPO Group Relative Policy Optimization]] — prerequisite-for (the token-level baseline GSPO modifies)
- [[DAPO]] — alternative-to (another GRPO modification, aimed at entropy collapse)
- [[GDPO Decoupled Reward Normalization]] — alternative-to (changes the advantage normalisation, not the ratio)
- [[RL Training Frameworks for LLMs]] — related
