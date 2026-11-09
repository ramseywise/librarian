---
title: Swin Transformer Shifted Windows
tags: [multimodal, concept]
summary: "Swin builds a hierarchical vision transformer with patch merging and window self-attention whose windows shift between blocks, giving cost linear in image size and strong dense-prediction results."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-liu-2021-swin-transformer.md
---

# Swin Transformer Shifted Windows

Swin is designed as a general-purpose backbone for classification, detection and segmentation. The image is split into 4x4 patches and passes through four stages of window-attention blocks, with 2x2 patch merging (concatenate, then a linear layer to 2C) between stages to form a feature hierarchy. Regular windowed attention (W-MSA, default window size 7) alternates with a shifted configuration (SW-MSA) so information crosses window borders; a cyclic shift with masking keeps batching efficient. A learnable relative position bias is added to the attention logits. For a fixed window size, window attention cost grows linearly with patch count, where global attention grows quadratically.

## Reported results (self-reported)

- Swin-L pretrained on ImageNet-22K at 384 reaches 87.3% ImageNet-1K top-1; HTC++ with multi-scale testing gives a box AP of 58.7 and a mask AP of 51.1 on COCO test-dev; on ADE20K val, UperNet reaches an mIoU of 53.5, an improvement of 3.2 over SETR (self-reported).
- Swin-T is 1.5 points above DeiT-S on ImageNet-1K (from scratch, 300 epochs, 224); 22K pretraining adds 1.8 to 1.9 points for Swin-B; Swin-B 22K at 384 gets 86.4 against 84.0 for ViT-B/16 at similar throughput (self-reported).
- Shifting windows adds 1.1 top-1 (ImageNet), 2.8 box AP (COCO) and 2.8 mIoU (ADE20K) for Swin-T over single-window partitioning. Absolute position embedding adds 0.4 on ImageNet but hurts detection and segmentation.
- The cyclic shift speeds Swin-T/S/B by 13%, 18% and 18% over padding on a V100, and is 4.1x and 1.5x faster than naive and kernel sliding windows for Swin-T at similar accuracy (81.3 against 81.4).
- Across four detection frameworks Swin-T gains +3.4 to +4.2 box AP over ResNet-50. Hierarchy and shifted windows lift an all-MLP model from 76.4 to 81.3 (self-reported).

## Limits

- The implementation uses unoptimised PyTorch functions, while ResNe(X)t uses tuned cuDNN kernels.
- No seeds or variance; training compute is unstated. The comparison tables mix models pretrained on 22K with 1K-only ones, and use different test-time tricks, so gaps between leaderboard entries do not compare like with like. DeiT in detection needs deconvolution layers, which may disadvantage it.
- Numbers are from 2021 and have been superseded.

## See Also
- [[Contrastive and Masked Vision-Language Pretraining]] — related (the family comparison)
- [[Florence UniCL Vision Foundation Model]] — extends (CoSwin encoder)
- [[VIOLET Masked Visual-Token Modeling]] — extends (Video Swin encoder)
- [[NFNet Adaptive Gradient Clipping]] — alternative-to
- [[V-MoE Sparse Mixture of Experts for Vision]] — related
