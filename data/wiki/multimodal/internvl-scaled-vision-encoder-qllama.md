---
title: InternVL Scaled Vision Encoder with QLLaMA
tags: [multimodal, concept]
summary: "InternVL scales the vision encoder to 5.9B parameters and bridges it to an LLM through QLLaMA, a LLaMA-initialised middleware with 96 queries, using contrastive-then-generative alignment (all numbers self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-chen-2024-intern-vl.md
---

# InternVL Scaled Vision Encoder with QLLaMA

Chen et al. (2024, arXiv v3) ask whether one vision encoder with 6B parameters, aligned step by step to a language middleware initialised from an LLM using web-scale data, can handle contrastive and generative vision-language tasks alike. They hypothesise that bringing the encoder up to LLM scale narrows the gap in size and representation that thin glue layers leave open.

## Mechanism

- **InternViT-6B** is a vanilla ViT of 5.9B parameters. **QLLaMA** is an 8B middleware initialised from multilingual LLaMA-7B; its 8B total is 42 times the Q-Former's size. It brings 96 learnable queries along with 1B newly added cross-attention parameters.
- Stage 1 trains contrastively from scratch on 4.98B pairs (cleaned from 6.03B). Stage 2 trains only the new queries and cross-attention generatively on 1.03B filtered pairs. Stage 3 is SFT on about 4M samples, with an MLP linking the encoder to Vicuna or InternLM.
- **InternVL-C** uses attention-pooled InternViT features; **InternVL-G** also passes them through QLLaMA queries.

## Results (self-reported)

- The ImageNet-1K linear-probe top-1 is 88.2, the best result that avoids JFT; zero-shot top-1 is 83.2 for InternVL-C. ADE20K linear probing gives 47.2 mIoU, 12.6 above ViT-22B (self-reported).
- On Flickr30K image-to-text, InternVL-G's zero-shot R@1 is 95.7 and multilingual XTD recall@10 averages 96.6 over 8 languages (self-reported).
- InternVL-Chat (Vicuna-13B, 336px) scores MME 1586.4 and POPE 87.6 against 1531.3 and 85.9 for LLaVA-1.5-13B (self-reported). The same InternViT-6B with plain MLP glue reaches MME 1546.9, also above LLaVA-1.5, so part of the gain comes from the encoder alone (self-reported).
- On one A100 (batch 128, bf16, unoptimised), encoding an image takes 15.5 ms at 224 and 66.9 ms at 448, so image size dominates cost (self-reported).
- Depth, head dimension and MLP ratio matter little for accuracy at fixed parameters; the deepest variant ran at 16.9 images per second against 28.0 for the chosen one (self-reported).

## Limits

- Efficiency covers only encoding at three resolutions, with no memory numbers or accuracy-versus-resolution curve; throughput includes text encoding.
- Resolution is not ablated for accuracy, and the glue-layer comparison mixes data, LLM and glue changes.
- No seeds, error bars, GPU-hours or most SFT hyperparameters; starred benchmarks saw their training annotations, so competitor comparisons are not like for like.

## See Also
- [[Vision-Language Model Architectures]] — related
- [[BLIP-2 Q-Former Bridging]] — alternative-to
- [[CLIP Contrastive Language-Image Pretraining]] — prerequisite-for
- [[LLaVA Visual Instruction Tuning]] — related
- [[Segment Anything SAM and SA-1B]] — related
- [[DINOv2 Curated-Data Self-Supervised Features]] — related
- [[EVA Masked CLIP-Feature Regression]] — related
