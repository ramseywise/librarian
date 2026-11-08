---
title: Mixture-of-Transformers
tags: [foundations, concept]
summary: "A multimodal architecture that gives each modality its own non-embedding weights (feed-forward, attention projections, norms) with shared global attention and a fixed modality tag as the router; matches a dense Chameleon 7B with 55.8% of FLOPs (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-liang-2024-mixture-transformers.md
---

# Mixture-of-Transformers

Liang et al. (arXiv 2411.04996, TMLR 2025) build a sparse multimodal transformer where the routing is decided by the token's modality, not by a learned router. All non-embedding weights are separate per modality: feed-forward layers, the query/key/value/output projections and the layer norms. Self-attention is global, so tokens of every modality still attend to each other. FLOPs per token equal those of the dense model.

## Reported results

- **Chameleon 7B (text and image):** MoT matches the dense model with 55.8% of the FLOPs. With speech added, the speech loss is matched at 37.2% of FLOPs (self-reported).
- **Transfusion:** at half the FLOPs, a 760M MoT scores better than a dense 1.4B model on FID, CLIP and CIDEr (self-reported).
- **Wall-clock:** 47.2% of the dense model's time for image loss on 256 A100 GPUs, measured on one cluster (self-reported).
- **Ablations:** a four-expert MoE gains vanish at 7B for image. Untying the feed-forward layers matters most; untying the layer norms adds nothing (self-reported).

## Limits

- Comparisons are step-matched on training loss, not downstream accuracy, except in Transfusion, where the text gain is marginal or absent.
- The 7B image FID comparison (8.14 against 9.22) is not matched: the dense baseline used 1T tokens and richer data.
- The extraction notes that the abstract's "one third of FLOPs" corresponds to a figure of 30% of steps, and that 45.5% (steps) and 55.8% (FLOPs) are different metrics.

## See Also
- [[Vision-Language Model Training Families]] — prerequisite-for (the dense multimodal designs this replaces)
- [[MoE-LLaVA and MoE-Tuning]] — alternative-to (learned top-2 routing for a vision-language model)
- [[Transformer Architecture]] — prerequisite-for
- [[Real-Time Multimodal Agents]] — related
