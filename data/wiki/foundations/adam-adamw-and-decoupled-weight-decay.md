---
title: "Adam, AdamW and Decoupled Weight Decay"
tags: [foundations, comparison]
summary: "L2 regularisation inside Adam is not weight decay (weight_decay 0.1 collapsed to chance while AdamW trained fine), and learning rate matters more than optimiser choice: a sweep by factors of ten moves accuracy from 0.174 to 0.961 on one model."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--notes--02-optimisation-and-regularisation.md
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--README.md
---

# Adam, AdamW and Decoupled Weight Decay

## Optimiser comparison

MLP on 8x8 digits, 10 epochs, 5 seeds, test accuracy: plain SGD 0.428, SGD with momentum 0.934, RMSprop 0.957, Adam 0.952, AdamW 0.952. Lion at lr 1e-3 gave 0.956 but 0.890 at 3e-4 and 0.690 at 1e-4: Lion is sign-based, so it recommends a learning rate 3-10x smaller and weight decay 3-10x larger than AdamW, and its gain grows with batch size. Adam defaults: alpha 1e-3, beta1 0.9, beta2 0.999. Comparisons are only meaningful when each optimiser is tuned (the AlgoPerf benchmark measures time to a target with tuned instances); the original Adam paper reported training cost only.

## L2 is not weight decay inside Adam

Adam rescales gradients per parameter, so an L2 term added to the loss is rescaled too and no longer shrinks weights uniformly. With weight_decay=0.1: Adam ended at test 0.102 with weight norm 0.02; AdamW (decay applied directly to the weights, decoupled from the gradient) reached 0.972 with norm 13.57. The AdamW paper reported about 15% relative error reduction on ResNets on CIFAR-10. Default to AdamW. See [[Regularisation as a Prior]] for the penalty-as-prior reading of L2.

## Learning rate first

Adam, 10 epochs, digits: 1e-5 gave 0.174, 1e-4 0.647, 1e-3 0.956, 1e-2 0.961, 1e-1 0.847, 1.0 0.100. Sweep by factors of ten before changing optimiser. A cosine schedule reached 0.970 against 0.963 for a constant lr of 0.01. An adaptive learning-rate method (D-Adaptation) failed on 1 of 5 seeds (0.102), so check seeds before trusting a new method.

## See Also
- [[Weight Initialisation and Activation Scale]] — prerequisite-for
- [[Regularisation Under Noisy Labels]] — related
- [[Regularisation as a Prior]] — related
