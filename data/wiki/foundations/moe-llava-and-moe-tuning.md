---
title: MoE-LLaVA and MoE-Tuning
tags: [foundations, concept]
summary: "MoE-LLaVA turns a vision-language model sparse in three stages, copying the feed-forward layer into experts in the last stage; a 3.6B-activated model beats LLaVA-1.5-7B on some benchmarks and POPE against 13B (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-lin-2024-moe-llava.md
---

# MoE-LLaVA and MoE-Tuning

Lin et al. (arXiv 2401.15947, 2024) propose MoE-Tuning, a three-stage recipe for sparse vision-language models.

## Mechanism

1. **Stage I** trains the MLP projector that connects the vision encoder to the language model.
2. **Stage II** trains the dense vision-language model.
3. **Stage III** copies the feed-forward layer into several experts (sparse upcycling) and trains only the mixture-of-experts layers.

The router is linear with top-2 of 4 experts, placed in every other layer, with an auxiliary loss weight of 0.01. The authors' ablation reports that training the mixture directly, without the earlier stages, is worst.

## Reported results

- The 3.6B-activated (5.3B total) model on a Phi-2 backbone scores SQA-I 68.5 against 66.8, POPE 86.3 against 85.9, and MME 1423 against 1510.7 for LLaVA-1.5-7B (self-reported).
- The 1.8B x 4 model beats LLaVA-1.5-13B on POPE (self-reported).
- The OpenChat-7B mixture is worse than its dense base (SQA-I 62.8 against 69.0).
- Routing analysis found that no modality-specific experts emerge.

## Limits

- Training in fp16 was unstable.
- Cost is counted in activated parameters, not latency or memory.
- Internal inconsistencies noted by the extraction: the text says SQA-I +2.7% while the table gives 1.7; the StableLM VQAv2 score is 76.7 in Table 7 and 76.0 in Table 10.

## See Also
- [[Vision-Language Model Training Families]] — prerequisite-for (the dense stages it starts from)
- [[Mixture-of-Transformers]] — alternative-to (fixed per-modality weights instead of a learned router)
- [[MoE Expert Offloading]] — related (mixture-of-experts at inference)
