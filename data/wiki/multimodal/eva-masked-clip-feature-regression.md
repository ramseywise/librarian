---
title: EVA Masked CLIP-Feature Regression
tags: [multimodal, concept]
summary: "EVA pretrains a 1.0B vanilla ViT to regress CLIP vision features of masked patches on 29.6M public images, then reuses it to initialise a 1.1B CLIP that trains stably."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-fang-2023-eva.md
---

# EVA Masked CLIP-Feature Regression

EVA asks whether masked image modeling with image-text aligned targets can scale a plain ViT to a billion parameters using public data. A 40-layer ViT-g reconstructs the vision features of OpenAI CLIP-L/14 for 40% of patches (block-wise masking) under a negative cosine loss. Training used 29.6M public images over 150 epochs (128 A100-40GB GPUs, about 14.5 days, fp16, batch 4096). The model is then fine-tuned per task for classification, video, detection and segmentation, and it also initialises the image tower of a 1.1B-parameter CLIP (EVA CLIP-g) trained on LAION-400M.

## Reported results (self-reported)

- ImageNet-1K top-1: 89.7% at 560 px with a linear classifier (ImageNet-21K intermediate fine-tune, then 1K); 89.6% at 336 px, comparable to BEiT-3.
- EVA CLIP-g trains stably in fp16 with a 41k batch on 256 A100-40GB GPUs, where OpenCLIP g/H needed bfloat16 (self-reported).
- Detection and segmentation (self-reported): LVISv1.0 val reaches APbox 62.2 and APmask 55.0 at single scale; COCO test-dev reaches APbox 64.7 with test-time augmentation; ADE20K multi-scale mIoU is 62.3, below BEiT-3's 62.8, using a weakened Mask2Former configuration at 896 px.
- Kinetics-400 top-1 is 89.7% after a K-722 intermediate fine-tune and 88.4% without it.
- A ViT-B pilot reaches 85.5 on ImageNet-1K with direct feature regression at 800 epochs, which the authors take to mean that tokenizing CLIP features is unnecessary.
- EVA shows the smallest gap between ImageNet-1K and the six-variant average at 336 px.

## Limits

- The teacher is OpenAI CLIP-L, which was trained on 400M image-text pairs; the claim of using public data only is therefore conditional, as the authors concede.
- The segmentation setup was weakened to fit GPU memory.
- The zero LVIS-to-COCO mask gap does not mean large-vocabulary detection is solved (rare-class AP 48.3 against 57.4 for frequent).
- Single runs; competitor numbers date from 10 November 2022. EVA CLIP optimizer, learning rate and steps are not stated.
- Internal inconsistencies in the extraction: EVA CLIP-g zero-shot ImageNet is 78.5 in tables but 78.2 in text; the 12-benchmark average is 72.7 in one place and 75.7 in another; samples seen are given as both 11B and 7B.

## See Also
- [[Contrastive and Masked Vision-Language Pretraining]] — related (the family comparison)
- [[Masked Autoencoders Pixel Reconstruction]] — prerequisite-for (masking idea with pixel targets)
- [[CLIP Contrastive Language-Image Pretraining]] — prerequisite-for (teacher and CLIP recipe)
- [[BEiT Masked Image Modeling with Visual Tokens]] — alternative-to
