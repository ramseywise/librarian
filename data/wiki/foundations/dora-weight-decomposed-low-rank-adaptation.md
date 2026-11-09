---
title: DoRA Weight-Decomposed Low-Rank Adaptation
tags: [foundations, concept]
summary: "DoRA splits a pretrained weight into a magnitude vector and a direction, trains the magnitude directly and the direction with LoRA, and merges back with no inference overhead; commonsense-8 average on LLaMA-7B 74.7 to 78.4 over LoRA (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-liu-2024-dora.md
---

# DoRA Weight-Decomposed Low-Rank Adaptation

Liu et al. (arXiv 2402.09353, ICML 2024) propose DoRA as a variant of LoRA. The adapted weight is W' = m * (W0 + BA) / ||W0 + BA||_c: a trainable magnitude m times a direction that is normalised column-wise, where the direction is updated through the usual low-rank product BA.

## Mechanism

- The magnitude is a free vector; only the direction goes through the low-rank update.
- After training the pieces are merged into one weight, so inference costs the same as the base model.
- **Detach trick.** Treating the norm as a constant in the backward pass cuts training memory by 24.4% on LLaMA-7B and 12.4% on VL-BART (self-reported).
- The authors analyse the change in magnitude against the change in direction. The correlation between the two is -0.62 for full fine-tuning, -0.31 for DoRA and 0.83 for LoRA on VL-BART (self-reported). They read DoRA as closer to full fine-tuning's pattern.

## Reported results

Setup: eight commonsense reasoning tasks, average accuracy against LoRA at the same rank. LLaMA-7B rises from 74.7 to 78.4, LLaMA-13B from 80.5 to 81.5, LLaMA2-7B from 77.6 to 79.7, and LLaMA3-8B from 80.8 to 85.2 (self-reported). A half-rank DoRA also beats full-rank LoRA. In a rank sweep, LoRA at r=8 scores 40.74% against 77.96% for DoRA; the extraction notes the LoRA cells look like unstable runs. QDoRA, the quantized variant, was run by Answer.AI, a third party, and only an initial result is cited.

## Limits

- One seed per cell; no time or memory comparison against LoRA is reported.
- The LoRA baselines on LLaMA2 and LLaMA3 were rerun with earlier hyperparameters.
- Internal inconsistency noted by the extraction: LLaMA-7B DoRA is 78.4 in Table 1 but 78.1 in Table 6, and Table 7 gives 78.1 or 78.3.

## See Also
- [[Doc-to-LoRA]] — related (another use of LoRA weights, generated rather than trained)
- [[Vision-Language Model Training Families]] — related (parameter-efficient adaptation options)
- [[PCA, NMF and Low-Rank Factorisation]] — prerequisite-for (the low-rank idea underneath)
- [[CALM Composition to Augment LLMs]] — alternative-to (added cross-attention to a second model instead of low-rank updates)
- [[Intrinsic Dimension of Objective Landscapes]] — related (why few trainable parameters can suffice)
