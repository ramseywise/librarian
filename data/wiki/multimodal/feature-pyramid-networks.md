---
title: Feature Pyramid Networks
tags: [multimodal, vision-backbones, concept]
summary: "FPN adds a top-down pathway with lateral connections to a ResNet so every pyramid level has strong semantics from a single input scale; in Faster R-CNN it improves COCO box AP and small-object proposal recall."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-lin-2017-feature-pyramid-networks-object-detection.md
---

# Feature Pyramid Networks

Lin et al. ask whether the multi-scale feature hierarchy that a ConvNet already computes can be turned into a pyramid with strong semantics at all scales, standing in for image pyramids (where each scale of the input is run through the network separately) for little added cost. They propose that merging coarse, semantically strong features with fine, semantically weak ones through a top-down path and lateral links yields strong semantics everywhere and better multi-scale detection, small objects above all.

## Method

The last-stage outputs C2 to C5 of a ResNet backbone (strides 4, 8, 16, 32) are merged along a top-down path built from 2x nearest-neighbour upsampling, a 1x1 lateral convolution and an element-wise sum, then a 3x3 convolution, giving P2 to P5 (and a P6 made by stride-2 subsampling for the region proposal network), each with 256 channels. The same head weights are shared across all levels in RPN and Fast R-CNN. A region of interest of width w and height h is sent to level k = floor(4 + log2(sqrt(w*h)/224)).

## Results (self-reported; COCO)

- Ablation setup throughout: minival, ResNet-50, trained on trainval35k at shorter side 800 px. In RPN, FPN adds 8.0 AR1k over the single-scale C4 baseline, and AR1k for small objects rises by 12.9.
- Faster R-CNN with FPN improves on the authors' own reproduced ResNet-50 baseline by 2.3 AP and on the published He et al. ResNet-50 baseline by 7.6 AP; the authors credit part of that gap to their baselines' choices of 800 px images, 512 RoIs, 5 anchor scales and 1000 test proposals.
- Without lateral connections Fast R-CNN loses roughly 2.6 AP (full FPN scores 33.9 on fixed FPN-RPN proposals) and 10 AR1k in RPN. Using just the finest level P2 is a little worse than the whole pyramid, and without the top-down path Fast R-CNN AP collapses.
- Faster R-CNN with ResNet-101 FPN beats all single-model COCO 2015 and 2016 winners on test-dev AP (single image scale).
- FPN mask proposals (two-layer MLP head, longest schedule) outperform DeepMask and SharpMask in AR while running faster (first 5k COCO val images, 1000 proposals, ResNet-50). The abstract states 6 FPS for single-scale-input FPN on a GPU.

## Limits

- Each configuration was run once, and no variance, seeds or significance tests are reported. By the authors' own account the ResNet-101 model was under-trained at the default schedule, and the feature-sharing version of the submitted model was never evaluated.
- Iterative regression, hard negative mining, context modelling and stronger augmentation are described as complementary but were not tried. Only a plain connection block was used; deeper residual blocks did slightly better yet were left out.
- The reason the top-down path helps (closing semantic gaps) is a conjecture the paper does not test, and its COCO state-of-the-art claims have aged.

## See Also
- [[Faster R-CNN]] — prerequisite-for
- [[Residual Connections and the Degradation Problem]] — prerequisite-for
- [[DETR Set Prediction Object Detection]] — related (the authors of DETR expect FPN-like fixes for small objects)
- [[Object Detection Anchors, Non-Max Suppression and Focal Loss]] — related
- [[Microsoft COCO]] — related
