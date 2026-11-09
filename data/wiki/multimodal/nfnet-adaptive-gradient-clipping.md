---
title: NFNet Adaptive Gradient Clipping
tags: [multimodal, concept]
summary: "NFNets are normalizer-free ResNets trained with unit-wise Adaptive Gradient Clipping, which lets them train at large batch and strong augmentation; the paper reports F1 matching EfficientNet-B7 about 8.7x faster and 86.5% ImageNet top-1 without extra data (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-brock-2021-high-performance-large-scale-image.md
---

# NFNet Adaptive Gradient Clipping

Brock et al. (arXiv:2102.06171v1, no venue in the PDF) examine whether deep ResNets with no normalization layer at all can match batch-normalized networks and EfficientNets on ImageNet, when batches are large and augmentation is strong.

## Mechanism

- **Base recipe:** the NF-ResNet design (residual branches scaled down for variance, Scaled Weight Standardization, a SkipInit-style gain initialised at zero), applied to an SE-ResNeXt-D. It comes with a new width and depth pattern and an added second 3x3 grouped convolution.
- **Adaptive Gradient Clipping (AGC):** the gradient of each unit, one row of the layer gradient, is rescaled whenever the norm ratio of gradient to that unit's weights is above a threshold lambda, and the weight norm is floored at 1e-3 (self-reported). Larger batches call for smaller thresholds; the paper uses lambda 0.01 at batch sizes from 1024 to 4096 (self-reported).
- Training uses MixUp, RandAugment, CutMix and dropout; the largest variants use sharpness-aware minimisation with the ascent step on 20% of the batch, costing 20 to 40% extra latency rather than 100% (self-reported).

## Results (self-reported)

- Speed (ImageNet val, single crop, TPUv3 step latency, 32 per device): F1 takes 158.5 ms against 1397.0 ms for EfficientNet-B7 at matched top-1, about 8.7x faster. F5 without SAM reaches 86.0% at similar latency to B7; F6 with SAM sets 86.5% without extra data.
- Transfer: F4+ pre-trained 20 epochs on JFT-300M and fine-tuned reaches 89.2% top-1 (1.86k TPUv3-core-days). In a 10-epoch JFT-300M transfer study (single seed), NF-ResNets beat batch-normalized counterparts in every case, typically by about 1%.
- Versions of the NFNet architectures with batch normalization trained 20 to 40% slower and scored slightly lower, and F4 and F5 turned unstable with batch norm. For F0, architecture and augmentation changes lift 80.4 to 83.6 (3-seed mean, 360 epochs, batch 4096). From batch 4096 upward, NF-ResNets without AGC trail batch-normalized ones.
- Large weight decay hurts large-scale pre-training and Adam is worse than SGD, which the authors note contradicts findings in the ViT paper.

## Limits

- The AGC ablations (Figures 2 and 7) are shown only as plots, and the best lambda may vary with optimizer, learning rate and batch size.
- Latency is tuned to TPUv3 and V100 dense compute; NFNets are competitive in FLOPs but not in parameters against accuracy. Transfer uses one seed per model and a private dataset, so it is not reproducible.
- F4 and F5 instability is attributed to bfloat16 but not tested. Attention variants were not tried, and finer recipe details live only in the source code.

## See Also
- [[Batch Normalization]] — prerequisite-for
- [[ILSVRC ImageNet Challenge]] — related
- [[Swin Transformer Shifted Windows]] — alternative-to
