---
title: DINOv3 Gram Anchoring Self-Supervised Backbone
tags: [multimodal, concept]
summary: "DINOv3 scales DINOv2-style self-supervised training to a 6.7B ViT on 1,689 million curated images and adds Gram anchoring, a loss on patch-similarity structure that repairs dense-feature degradation over long training (all numbers self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-simeoni-2025-dinov3.md
---

# DINOv3 Gram Anchoring Self-Supervised Backbone

Simeoni et al. (2025) ask if self-supervised learning can reach a 7B vision model trained on 1,689 million curated images with dense feature maps still intact, yielding a single frozen backbone that outperforms specialised models. They hypothesise that tying the patch-similarity structure to that of an early teacher stops dense features degrading in long training.

## Mechanism

- A 6.7B ViT with RoPE trains for 1M iterations on the LVD-1689M mixture (curated, retrieval and ImageNet data) with constant hyperparameters. Giving local and global crops their own layer norm added 0.2 to kNN and 1 mIoU to ADE20k late in training (self-reported).
- **Gram anchoring** pulls the student's Gram matrix (the pairwise dot products between patch features) toward the one from an earlier Gram teacher; features are free to change while their similarity pattern is kept. It is applied in a refinement phase after 1M iterations, with a higher-resolution Gram teacher.
- Post-training covers adaptation to high resolution, distillation from the one teacher into several students (ViT and ConvNeXt), and text alignment.

## Results (self-reported)

- For ViT-g and ViT-7B dense quality falls from roughly 200k iterations on, though ImageNet linear accuracy continues to climb. Gram anchoring lifts ADE20k mIoU from 50.3 to 55.7 and lowers NYU RMSE from 0.307 to 0.281, with ImageNet linear dropping from 88.2 to 88.0 (ablation on ViT-7B) (self-reported).
- Frozen 7B with a linear probe gets 55.9 mIoU on ADE20k against 53.0 for AM-RADIOv2.5 and 49.5 for DINOv2; with a Plain-DETR decoder it reaches 66.1 COCO mAP using test-time augmentation; with ViT-Adapter plus Mask2Former it ties the ADE20k state of the art, 63.0 (self-reported).
- The distilled ViT-H+ (840M) comes near its teacher on ADE20k (54.8 against 55.9). Distilled ViT-L reaches 54.9 mIoU against 48.8 for DINOv2 ViT-L (self-reported).
- ImageNet linear probe is 88.4, 0.7 to 0.9 below SigLIP 2 and PE; and the strongest ImageNet-C result, 19.6 mCE. DAVIS J&F is 83.3, 6.7 above DINOv2 (self-reported).
- Pretraining the 7B model on satellite imagery brings Open-Canopy MAE down from 2.42 to 2.02. The ViT-7B run cost 61,440 H100 GPU hours, or 47 MWh, and the full project about 9M GPU hours (self-reported).

## Limits

- OCR-heavy tasks lag the weakly supervised PE-core (for example GTSRB 87.5 against 94.8); the authors link it to the absence of image-text pairs.
- Geographic fairness gaps remain (a 23% drop between low- and high-income buckets).
- Gram anchoring was applied late, the teacher choice matters, and no study covers smaller models. Zero-shot global alignment trails SigLIP 2 and PE; V-JEPA 2 leads on SSv2 video.
- No seeds or variance; most ablations are single runs at 150k to 200k iterations; the training data is not released.
- Outliers in some feature dimensions show up in the 7B model, and the authors recommend a final layer norm or batch norm downstream.

## See Also
- [[Vision-Language Model Architectures]] — related
- [[DINOv2 Curated-Data Self-Supervised Features]] — prerequisite-for
- [[SigLIP Sigmoid Loss for Language-Image Pretraining]] — related
