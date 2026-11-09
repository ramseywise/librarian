---
title: DeepSeekMoE Fine-Grained Expert Segmentation
tags: [infra, concept]
summary: "DeepSeekMoE splits each feed-forward expert into many smaller ones, activates proportionally more of them, and keeps a few shared experts always on; the paper reports a 16B model matching dense 7B models at about 40% of the computation."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-dai-2024-deepseekmoe.md
---

# DeepSeekMoE Fine-Grained Expert Segmentation

Dai et al. argue that conventional top-K mixture-of-experts layers (GShard) suffer two problems: knowledge hybridity, where a few experts each receive tokens covering diverse knowledge, and knowledge redundancy, where different experts learn the same common knowledge. Their remedy has two parts.

1. **Fine-grained expert segmentation.** Each feed-forward network is split into m smaller experts and mK are activated instead of K, so total and activated parameters stay fixed while the number of possible expert combinations grows (choosing 2 of 16 allows 120 combinations, while choosing 8 of 64 allows 4,426,165,368).
2. **Shared expert isolation.** Ks experts are always active and absorb common knowledge, leaving the routed experts to specialise. The output sums the shared experts, the gated routed experts and the residual input.

## Results (all self-reported)

- Validation scale (9 layers, hidden 1280, about 2B total and 0.3B activated parameters, 100B tokens, 8K vocabulary): DeepSeekMoE beats GShard on Pile loss at equal parameters and compute, equals GShard with 1.5x the expert parameters and computation, and nearly reaches a Dense x16 upper bound, a dense model with 16 shared experts.
- Removing the shared expert and instead activating an extra routed expert, at equal compute, sharply worsens Pile loss. With only 3 routed experts activated (half the activated expert parameters) it still outperforms GShard when trained from scratch.
- Scaled to 16.4B total and 2.8B activated parameters on 2T tokens: comparable to LLaMA2 7B and DeepSeek 7B dense models at about 40% of the computation (those two take 187.9T and 183.5T in the report's Table 2). The extraction records relative strengths on knowledge tasks (TriviaQA) and code (HumanEval) but not the figures.
- The released 16B checkpoint is deployable on one 40 GB GPU.

## Limits

- Finer segmentation always helped, yet the 16B model settles on moderate granularity since computational efficiency drops at very fine granularity; there is as yet no scaling law for granularity.
- When experts are spread over devices, activating more of them could raise communication across devices; this was not measured.
- The "upper bound" result holds only near 2B parameters and 100B tokens.
- On MMLU the 16B model trails both dense 7B models (which score 45.8 and 48.2), as it does on other multiple-choice tasks; the authors put this down to its limited attention parameters.
- The paper reports no seeds or variance and no throughput, latency or serving numbers, and measures compute in FLOPs alone. The corpus is proprietary and the validation vocabulary (8K) differs from the 16B vocabulary (100K).

## See Also

- [[Multi-Head Latent Attention]] — related (DeepSeek-V2 pairs the two)
- [[MoE Expert Offloading]] — related
- [[MoE-LLaVA and MoE-Tuning]] — related
- [[Transformer Architecture]] — prerequisite-for
