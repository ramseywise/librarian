---
title: "Early and Late Dropout"
tags: [data-science, pattern]
summary: "Liu et al. switch dropout (or stochastic depth) on only for the first epochs to help underfitting vision models, and only after the first epochs for overfitting ones; the reported gains are small against seed noise."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-liu-2023-dropout-reduces-underfitting.md
---

# Early and Late Dropout

Liu, Xu, Jin and colleagues (ICML 2023) test whether dropout, usually a guard against overfitting, can reduce underfitting if it runs only in the early part of training, and whether the reverse timing can reduce overfitting. They expect that early on, dropout makes mini-batch gradient directions vary less and sit closer to the gradient of the whole dataset. All numbers below are the paper's own results for its own method, so they are self-reported.

## Definitions

- **Early dropout** applies dropout up to a chosen iteration and then turns it off. **Late dropout** is the reverse order: off first, on afterwards. Stochastic depth (s.d.) gets the same treatment.
- **Gradient direction variance (GDV)** is the mean pairwise cosine distance between mini-batch gradients. **Gradient direction error (GDE)** is the mean cosine distance between each mini-batch gradient and the gradient over the whole dataset.

## Results

The ImageNet-1K runs train a vision model on that dataset (the COCO and ADE20K results below are transfer runs); the comparisons are a model with no dropout and one with ordinary dropout of rate 0.1.

- ViT-T/16 (basic recipe, 300 epochs, three seeds): early dropout raised top-1 above the no-dropout baseline and lowered train loss, whereas standard dropout at 0.1 cost 6.0 points of accuracy. It also helped under an improved 600-epoch recipe, and every early duration tried, from 5 up to 300 of the 600 epochs, beat the 76.3 baseline.
- Swin-F, basic recipe: +0.4 from early dropout and +0.9 from early s.d.
- With ViT-T under AdamW and dropout 0.1, the area under the GDE curve across the first 1500 iterations fell by 13.60%. The dropout-trained model had less gradient variance and error only until about iteration 1000, and higher error after that.
- At batch size 8192 (ViT-T, linearly scaled learning rate) the gain vanished, which the authors read as fitting the idea that large batches already approximate the full gradient.
- Earlier dropout schedules (increasing, decreasing, curriculum, annealed) did no better than no dropout on underfitting models, and at best matched it; the curriculum schedule scored 70.4 (ViT-T, improved recipe).
- ViT-B, which sits in the overfitting regime, got nothing from early dropout (its baseline is 78.7, with ordinary dropout best at rate 0.1). Late s.d. beat standard s.d. for ViT-B (rate 0.4, off for the first 50 epochs) and for Mixer-B (rate 0.2).
- Transfer: Swin-F box AP on COCO went from 36.4 to 37.1 with early dropout (Mask-RCNN 1x), and ViT-B with late s.d. improved ADE20K mIoU (UperNet, 80k iterations).
- Early dropout did not locate a flatter minimum; curvature was 0.250 against 0.258 (ViT-T). Its training loss was no lower early on and fell sharply once dropout stopped; the run used 50 early epochs at a constant rate.

## Limits

- Only supervised vision tasks were tested; self-supervised pre-training and NLP were not.
- How the effect depends on training length and optimizer is not explored.
- The paper does not explain why training loss falls only after dropout ends; the authors suggest a better local optimum.
- The gains, 0.2 to 0.9 points, are small beside a seed standard deviation near 0.14%.
- Late s.d. brought no gain for ConvNeXt-B or Swin-B.
- For dropout (not s.d.) early use is sensitive to the rate, and it fails for ViT-B.
- Hardware and compute are not stated.
- The regime is defined by outcome: a model that does better with standard dropout counts as overfitting.

## See Also
- [[Regularisation Knobs and Early Stopping]] — prerequisite-for
- [[MC Dropout]] — related
- [[ConvNeXt and ConvNeXt V2 Modernising a ResNet]] — related
- [[Dropout and Input Distortion as Ridge Regression]] — related
