---
title: "ResNeXt Cardinality in Residual Blocks"
tags: [data-science, pattern]
summary: "ResNeXt replaces each ResNet bottleneck with C parallel low-dimensional paths of the same shape, summed and implemented as grouped convolution; the paper reports that raising cardinality beats going deeper or wider at matched FLOPs on ImageNet-1K (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-xie-2017-aggregated-residual-transformations-deep-neural.md
---

# ResNeXt Cardinality in Residual Blocks

Xie, Girshick, Dollar and colleagues (CVPR 2017) ask whether a homogeneous multi-branch residual block can add accuracy along a new dimension, cardinality, beyond depth and width. Cardinality is the size of the set of transformations the block aggregates. Their hypothesis is that raising it is a more effective route to accuracy than going deeper or wider.

## Mechanism

Each ResNet bottleneck block is replaced by C parallel paths, all with the same low-dimensional bottleneck topology, whose outputs are summed with the shortcut: y = x + sum over i of T_i(x). The authors show equivalent forms, including early concatenation and grouped convolution, and the model is implemented as grouped convolution. The design has few hyperparameters, and complexity is held roughly constant when comparing against ResNet.

## Results (self-reported)

All ImageNet-1K numbers are validation error with a single 224 crop unless stated.

- At matched complexity (roughly 4.1B FLOPs, 25M parameters, 90 epochs) the 32x4d ResNeXt-50 outperforms ResNet-50.
- ResNeXt-101 32x4d beats ResNet-101 at the same complexity of about 7.8B FLOPs.
- At twice ResNet-101's FLOPs (about 15B), doubling cardinality to a 64x4d ResNeXt-101 beats going deeper (ResNet-200, 21.7) or wider (a wider ResNet-101, 21.3).
- Trained on ImageNet-5K (6.8M images) and tested on the 1K validation set as a 5K-way task, ResNeXt-50 has lower top-1 error than ResNet-50 (45.5).
- Taking out the shortcuts degrades ResNet-50 much more than ResNeXt-50; ResNet-50 without them scores 31.2.
- On COCO minival with Faster R-CNN and an ImageNet-1K-pretrained backbone, ResNeXt-50 improves AP over ResNet-50 (26.5) and AP@0.5 to 49.7 from 47.6.
- On CIFAR, ResNeXt-29 16x64d (68.1M parameters, mean of 10 runs) is compared with Wide ResNet at 4.17 (CIFAR-10) and 20.50 (CIFAR-100) test error.

Training cost: with Torch's built-in grouped convolution on 8 M40 GPUs, a ResNeXt-101 32x4d mini-batch takes 0.95 s against 0.70 s for ResNet-101, and the 64x4d ResNeXt-101 takes 1.7 s per mini-batch, about 10 days on 8 GPUs. The paper also reports second place in ILSVRC 2016 classification.

## Limits

- ImageNet gains are single runs, and no variance is given.
- The margin narrows with a 101-layer ResNet (0.8 points) and for COCO with a 101-layer backbone.
- The grouped-convolution implementation is brute force, hence the 0.95 s against 0.70 s timing.
- Accuracy saturates as width falls below 4d, and the authors do not go below it.
- Applying the idea outside vision is anticipated by the authors but not tried.
- Complexity is preserved only approximately.

## See Also
- [[Residual Connections and the Degradation Problem]] — prerequisite-for
- [[Compound Scaling of Depth, Width and Resolution (EfficientNet)]] — related (scales depth, width and resolution; compares B3 with ResNeXt-101)
- [[VGG Depth with Stacked 3x3 Filters]] — related (the depth axis)
- [[Faster R-CNN]] — related (the COCO detector used here)
