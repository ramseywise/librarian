---
title: "Big Transfer (BiT) Generalist Pretraining"
tags: [data-science, pattern]
summary: "BiT scales supervised pre-training of ResNets with GroupNorm and Weight Standardization, then fine-tunes with a fixed size-based heuristic, BiT-HyperRule, instead of a per-task search."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-kolesnikov-2020-big-transfer-bit.md
---

# Big Transfer (BiT) Generalist Pretraining

The question is whether bigger data, model and schedule in supervised pre-training, paired with one simple fine-tuning rule, produce a single visual representation that transfers to many tasks, low-data ones included, without a hyperparameter search per task.

## Recipe

The network is a ResNet-v2 using GroupNorm and Weight Standardization in place of BatchNorm. SGD pre-training data defines the variant: ILSVRC-2012 for BiT-S, ImageNet-21k for BiT-M, JFT-300M for BiT-L. Fine-tuning uses **BiT-HyperRule**, which sets schedule length, resolution and MixUp use from the task's dataset size and image resolution. The paper calls this a *generalist* representation (pre-training independent of the task), against *specialist* methods that condition pre-training on each task.

## Results (self-reported)

- BiT-L (ResNet152x4, JFT-300M): ILSVRC-2012 top-1 of 87.54% (prior generalist: 86.4), CIFAR-10 99.37%, and 76.29% across the 19 VTAB-1k tasks (1,000 examples each, a single setting) against a previous 70.5.
- ImageNet-21k instead of ILSVRC-2012 for pre-training adds 4.09 points on ILSVRC-2012 (ResNet152x4).
- Few-shot, BiT-L: 72.0% on ILSVRC-2012 with 5 labeled examples per class; 82.6% on CIFAR-100 with 10 per class.
- ObjectNet top-5 80.0% (113 overlapping classes), nearly 25% absolute above the prior best. RetinaNet on COCO-2017 val: 43.8 AP with a BiT-L ResNet-101x3 backbone, against 40.8 for the literature ImageNet baseline.
- Searching hyperparameters per task, 40 random trials on VTAB-1k, raises BiT-L's VTAB-1k score from 76.29% to 78.72%, with the gain levelling off near 20 trials.
- Normalisation, ResNet-50 from scratch on ILSVRC-2012 at batch 4096: GroupNorm alone costs 5.4% top-1 against BatchNorm; with Weight Standardization it reaches 76.0 against 75.6. GN+WS also transferred better to VTAB-1k (70.39 against 67.72).
- Scale: reusing the ILSVRC-2012 training budget (roughly 100 million images seen) on ImageNet-21k hurts, whereas schedules 3x and 10x longer recover and exceed it. A small ResNet-50x1 can do worse on JFT-300M than on ImageNet-21k, so data and model must grow together. In JFT-300M pre-training (Fig 7, right), weight decay 1e-5 starts faster and ends worse than 1e-4.
- Deduplication removed under 50k near-duplicate images from JFT-300M and changed results little (ILSVRC-2012 87.8 full against 87.9 deduplicated).

## Limits

- BiT-L cannot be reproduced outside the authors' lab because JFT-300M is unreleased; the paper promises BiT-M weights only.
- The authors say standard benchmarks look near saturation: in a rater study on BiT-L errors, only 19.21% of ILSVRC-2012 mistakes were clearly the label over the prediction, and about half of CIFAR-10 mistakes were ambiguity or label noise. That study used an earlier BiT-L model.
- BiT-HyperRule is not optimal (78.72 against 76.29 on VTAB-1k with tuning).
- Noisy Student, a specialist method, still beats BiT-L on ILSVRC-2012 (88.4) at a per-task training cost.
- Only SGD was tried; ResNets only; precision and BiT-L pre-training compute not stated.

## See Also
- [[Transfer and Multi-Task Learning Conditions]] — prerequisite-for
- [[Batch Normalization]] — alternative-to (GroupNorm with Weight Standardization replaces it)
- [[Noisy Student Self-Training]] — alternative-to (concurrent specialist method)
- [[Adam, AdamW and Decoupled Weight Decay]] — related (weight decay and effective learning rate)
- [[Instagram Hashtag Weakly Supervised Pretraining]] — related
- [[Vision Transformer ViT Patch Tokens and Scaling]] — alternative-to
