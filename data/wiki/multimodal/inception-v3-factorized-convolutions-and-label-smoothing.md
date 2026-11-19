---
title: Inception-v3 Factorized Convolutions and Label Smoothing
tags: [multimodal, vision-backbones, concept]
summary: "Inception-v3 scales a GoogLeNet-style convnet with factorized convolutions, efficient grid reduction, a batch-normalised auxiliary head and label smoothing, reaching 21.2% top-1 and 5.6% top-5 single-crop on ILSVRC 2012 at 4.8 billion operations."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-szegedy-2016-rethinking-inception-architecture-computer-vision.md
---

# Inception-v3 Factorized Convolutions and Label Smoothing

Szegedy, Vanhoucke, Ioffe and colleagues ask how to scale a convnet so added computation is used well. They give four design principles, which they call speculative: avoid early representational bottlenecks, use higher-dimensional local representations, aggregate spatially over reduced embeddings, and balance width and depth. Figures are self-reported on the ILSVRC 2012 validation set (48,238 examples used).

## Mechanisms

- **Factorized convolutions.** Replacing a 5x5 by two 3x3 convolutions saves 28% of computation and parameters (equal filters). An n x n becomes 1 x n then n x 1; a 3x1 followed by 1x3 costs a third less than 3x3, whereas two 2x2 convolutions save 11%. In a control, ReLU after both factorized layers did better than a linear layer first.
- **Efficient grid reduction** module, a dedicated block for shrinking the feature-map grid.
- **Auxiliary classifier as regulariser.** The paper reports that removing the lower auxiliary head had no adverse effect, so the heads act as regularisers, not as help for early convergence (this contradicts the GoogLeNet hypothesis); batch-normalising the auxiliary head gave 0.4% absolute top-1.
- **Label-smoothing regularisation.** Instead of a one-hot target, the label distribution mixes the true class with a uniform distribution u over the 1000 classes (u = 1/1000), weighting the true class by 1 - eps and u by eps, with eps = 0.1. Cross entropy against the mixture splits into the same two weighted terms: the ordinary loss and a loss against u. The gain was about 0.2% absolute on top-1 and top-5 alike.

## Results

- Cumulative ablation (single crop): factorizing the first 7x7 convolution left top-1 error at 21.6% where it had been 22.8%, and switching Inception-v2 to RMSProp moved it from 23.4% to 23.1%.
- Final Inception-v3, single crop, 4.8 Bn operations: 21.2% top-1 and 5.6% top-5. Ensemble of four with 144 crops: 17.3% top-1 and 3.5% top-5.
- At constant compute, a 79x79 receptive-field input gave 75.2% top-1 against 76.6% at 299x299.

## Limits

- Results are on the validation set only; test verification was deferred. The ablation is cumulative, single run, no seeds or variance; the 0.2% label-smoothing effect is small and no noise level is reported.
- Label smoothing is tried only with uniform u and eps = 0.1, with no sweep. Augmentation, crop details and training set size are not stated; filter sizes are in a supplement.
- The extracted tables 3 to 5 have garbled or swapped column headers (Table 4 lists top-5 before top-1), and the text calls the model v2 and v3 inconsistently.

## See Also
- [[Batch Normalization]] — prerequisite-for
- [[AlexNet ReLU, Dropout and the Two-GPU ConvNet]] — prerequisite-for
- [[Knowledge Distillation with Soft Targets]] — related (soft-target training)
- [[ILSVRC ImageNet Challenge]] — related
- [[Residual Connections and the Degradation Problem]] — related
