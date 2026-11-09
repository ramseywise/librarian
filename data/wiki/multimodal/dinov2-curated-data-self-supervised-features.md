---
title: DINOv2 Curated-Data Self-Supervised Features
tags: [multimodal, concept]
summary: "DINOv2 trains a ViT-g/14 on the 142M-image LVD-142M set curated by retrieval, with DINO plus iBOT losses, centering and KoLeo, to give frozen features that match or beat text-supervised OpenCLIP."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-oquab-2023-dinov2.md
---

# DINOv2 Curated-Data Self-Supervised Features

DINOv2 asks whether self-supervised learning on enough curated data gives frozen, general-purpose features that rival text-supervised ones. LVD-142M (142,109,386 images) is built with no text or metadata, by retrieving images close to curated sets from an uncurated pool that was deduplicated down to 744M images; the build took under two days across 20 nodes with 8 V100-32GB each. A ViT-g/14 (1.1B parameters) trains with an image-level DINO loss plus a patch-level iBOT loss, untied heads, Sinkhorn-Knopp centering, the KoLeo regulariser and, at the end, a short phase at 518x518. The smaller ViT-S, ViT-B and ViT-L models are distilled from the ViT-g. The authors report about 2x faster training, using a third of the memory, relative to the iBOT code (self-reported).

## Reported results (self-reported; frozen features, authors' own evaluation code)

- ImageNet-1k linear probe: slightly above OpenCLIP ViT-G/14 (LAION-2B) and 4.2 points above the previous best self-supervised result (iBOT ViT-L/16 on ImageNet-22k). Fine-tuning adds only about 2 points (448 px gives 88.9; linear 86.5 to 86.7).
- Oxford-Hard retrieval (self-reported): ViT-L/14 scores 54.0 mAP, OpenCLIP ViT-G/14 scores 19.7, and the DINOv2 ViT-g/14 scores 52.3. Oxford images were also query sets for building LVD-142M.
- ADE20K linear segmentation: 49.0 mIoU against 39.3 for OpenCLIP. With a frozen backbone, ViT-Adapter and Mask2Former it reaches 60.2 against a 62.9 state of the art. NYUd depth with a DPT decoder gives RMSE 0.279 against 0.414.
- On ImageNet-A it beats OpenCLIP (which scores 63.8) but trails on R and Sketch; it also trails slightly on Places205.
- Ablations: KoLeo lifts Oxford-M from 55.6 to 63.9; the iBOT masked term lifts ADE20K from 44.2 to 47.1; curated data beats uncurated (54.3) and ImageNet-22k (62.5) on Oxford-M. A distilled ViT-L/14 beats one trained from scratch (84.5 against a 86.5 teacher).
- Cost for the ViT-g (self-reported): 22,016 GPU-hours on A100-40GB, 9.7 MWh and 3.7 tCO2eq.

## Limits

- No variance or seeds; linear-probe hyperparameters are chosen on the validation set used for reporting.
- Many evaluation datasets also supplied images used as queries to build LVD-142M, which tunes the data towards those domains.
- Fairness gap on Dollar Street: performance is 25.7% worse on Africa than on Europe, and 31.7% worse for low-income than for high-income households.
- The OpenCLIP comparison is on frozen features and linear heads, and the authors call the carbon comparison unfair since OpenCLIP trains a text encoder too.

## See Also
- [[Contrastive and Masked Vision-Language Pretraining]] — related (the family comparison)
- [[Masked Autoencoders Pixel Reconstruction]] — related (masked baseline)
- [[CLIP Contrastive Language-Image Pretraining]] — alternative-to (text-supervised features)
- [[BYOL Bootstrap Your Own Latent]] — prerequisite-for
- [[DINOv3 Gram Anchoring Self-Supervised Backbone]] — extends
