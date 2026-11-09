---
title: VIOLET Masked Visual-Token Modeling
tags: [multimodal, concept]
summary: "VIOLET is an end-to-end video-language transformer that uses a Video Swin encoder for temporal modelling and masked visual-token modeling over dVAE tokens as a pretraining task."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-fu-2021-violet.md
---

# VIOLET Masked Visual-Token Modeling

VIOLET argues that mean-pooling or concatenating a handful of frame features loses temporal information (the paper's term for this is "imagify"). T sparsely sampled frames go through a Video Swin Transformer; the per-frame features join BERT word embeddings in a cross-modal transformer. Pretraining combines VTM, MLM and the new masked visual-token modeling (MVM), which recovers the discrete DALL-E dVAE tokens of masked video patches, using blockwise and attention-guided masking. T is 4 during pretraining and 5 downstream.

## Reported results (self-reported)

- Table 3 (WebVid pretraining, MSRVTT retrieval R@1): Video Swin beats mean pooling (20.8) and concatenation (23.5), both using ResNet-50 frame features, so encoder and temporal modelling are confounded.
- MVM is best among masked visual modelling variants on MSRVTT R@1; VTM plus MLM alone gives 24.4 and no pretraining 13.0. Blockwise plus attention masking is best on TGIF-Action; random masking gives 83.7.
- Using MVM as the only objective over the whole of YT-Temporal, pretraining reaches 21.6% MVM accuracy and adds 2.3 points on TGIF-Action (self-reported).
- With 5 frames it beats ClipBERT (16 frames, 22.0) by roughly 10 R@1 points on both MSRVTT and DiDeMo (self-reported), though data and encoder differ. Zero-shot MSRVTT R@1 is compared with Frozen at 24.7 and CLIP at 31.2. Clip4Clip, pretrained on 400M CLIP pairs, stays far ahead on fine-tuned MSRVTT.
- Video QA against MERLOT on MSRVTT-QA (43.1) uses far less pretraining compute: about 2,240 V100 GPU hours against 30,720 TPU hours. It trails MERLOT on TGIF-Action (94.0). On VCR Q to A at 224x224 it matches MERLOT (75.1 at 384x704).
- Pretraining on WebVid plus CC (5.5M) gives much better retrieval than YT-Temporal (180M, 25.4).

## Limits

- No frame-count ablation. Retrieval is a per-pair cross-encoder, and corpus-scale cost is not discussed.
- No seeds, variance, batch size or schedule. Densely sampled long videos and audio are left as future work.

## See Also
- [[Contrastive and Masked Vision-Language Pretraining]] — related (the family comparison)
- [[BEiT Masked Image Modeling with Visual Tokens]] — prerequisite-for (the discrete-token target idea)
- [[Swin Transformer Shifted Windows]] — prerequisite-for (video variant as encoder)
- [[MERLOT Multimodal Script Knowledge]] — alternative-to
