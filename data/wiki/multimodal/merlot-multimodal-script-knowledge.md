---
title: MERLOT Multimodal Script Knowledge
tags: [multimodal, concept]
summary: "MERLOT pretrains on YT-Temporal-180M, 180M frame and ASR-segment pairs from 6M YouTube videos, with contrastive matching, attention-masked language modeling and frame reordering to learn script knowledge."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-zellers-2021-merlot.md
---

# MERLOT Multimodal Script Knowledge

MERLOT asks whether commonsense knowledge of how events unfold (script knowledge) can be learned from unlabeled YouTube videos and their ASR transcripts, and whether it transfers to video QA and static-image reasoning. An image encoder (ResNet-50 plus 12-layer ViT, from scratch) and a 12-layer joint transformer initialised from RoBERTa-base are trained on YT-Temporal-180M, built from a filtered set of 6M videos. Three objectives apply: contrastive frame-transcript matching, attention-masked language modeling (half the time, highly attended tokens are masked, as a stand-in for visually grounded words) and temporal frame reordering. Fine-tuning uses a 2-layer MLP on the CLS token; story ordering is evaluated zero-shot. Pretraining ran on a TPU v3-1024 with batch 1024 sequences.

## Reported results (self-reported)

The extraction gives mostly directions.

- The base-size model does better than image-caption models of the same size on VCR and sets state of the art on TGIF-Transition, with results also on TGIF-Action, TVQA and MSRVTT-QA (self-reported).
- Zero-shot SIND story unscrambling (5K stories) beats CLIP.
- Ablations (self-reported): removing the contrastive loss drops VCR sharply; static caption pretraining (Conceptual Captions plus COCO) gives poor VCR; pretraining on HowTo100M alone is 6.5 VCR points under the diverse corpus at equal steps; raw ASR is worse than denoised ASR; VCR improves with epochs (75.2 at 5 epochs) and had not plateaued at 40.
- Frame reordering helps TVQA but slightly lowers VCR (75.5 without against 75.2 with).
- A UCF-101 linear probe on the visual branch trails CLIP ViT-B/16.

## Limits

- English-only data and base-size models only; frame ordering is a coarse temporal objective.
- The corpus is skewed (about 30% local broadcast news, crime topics) and the authors do not advocate deployed use. Only video IDs are released, so the corpus is hard to reproduce.
- There are no seeds or variance; ablation gaps of roughly 1 point are single runs.

## See Also
- [[Contrastive and Masked Vision-Language Pretraining]] — related (the family comparison)
- [[VIOLET Masked Visual-Token Modeling]] — alternative-to
- [[CLIP Contrastive Language-Image Pretraining]] — related (zero-shot and linear-probe baseline)
