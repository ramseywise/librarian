---
title: CIFAR-10 and CIFAR-100 with RBM Features
tags: [multimodal, vision-backbones, reference]
summary: "Krizhevsky's 2009 technical report introduces CIFAR-10 (60,000 images, 10 classes) and CIFAR-100 (100 classes in 20 superclasses) from the 80 million tiny images, and shows RBM-pretrained features beat raw pixels on CIFAR-10 (about 64% against 37 to 41% for logistic regression)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-krizhevsky-2024-learning-multiple-layers-features-tiny.md
---

# CIFAR-10 and CIFAR-100 with RBM Features

The report is dated 8 April 2009 (the reading ledger's 2024 is a metadata error). It asks whether features learned by Gaussian-Bernoulli restricted Boltzmann machines (RBMs) on unlabeled 32x32 colour images help a classifier, and defines two labelled subsets of the 80 million tiny images (79,000 search terms, noisy labels from WordNet-based search).

## The datasets

- CIFAR-10: 6,000 images in each of 10 classes, 5,000 per class for training.
- CIFAR-100: 600 images per class over 100 classes grouped into 20 superclasses.

## RBM features

RBMs are fitted with contrastive divergence (CD-1: the hidden units are sampled twice) to roughly 2 million tiny images, after dropping the 1,000 least significant principal components. The accuracies below are CIFAR-10 test accuracy, read off the bar labels of the report's Figure 3.1; self-reported, single runs.

- Logistic regression on raw pixels: 37.32% (whitened), 41.13% (unwhitened). On 10,000 unwhitened RBM features: 63.78%; on whitened-data RBM features: 59.61%.
- A one-hidden-layer net with 10,000 units, started from RBM features and then fine-tuned, reaches 64.84%; the same-sized net from random initialisation reaches 51.53%. RBM-started nets also needed far fewer epochs, leaving out the cost of pretraining.
- Adding a second RBM layer, or training a two-hidden-layer net, did not help (56.62%, 62.20% and 60.34% against 63.78% and 64.84%).
- Whitened 32x32 RBMs only worked after failures: 8,000 hidden units on whitened images gave meaningless filters, while 26 patch RBMs with 300 hidden units learned edge filters. Learning the visible standard deviations (69 fixed) lowered them to about 30 and improved reconstruction but made filters noisier.
- Distributed CD-1: data sent grows linearly, 48(K-1) MB per 8,000-example batch for a binary 8000x20000 RBM; doubling machines nearly doubles speed for binary visible units, and single precision is about 3 times faster than double at first.

## Limits

- Accuracies exist only as bar-chart labels, with no table, variance or repeats. Only CIFAR-10 is used because CIFAR-100 had just been finished.
- Most hyperparameters and compute are not stated. The author concedes that reconstruction error measures fit poorly. The biggest net (near 2x10^8 parameters) overfit and was left untuned.
- Parallel benchmarks use random data, and on binarised MNIST parallelism stopped paying after two machines.
- The source ledger dates the item 2024, but the report itself is dated 8 April 2009.
- RBM pretraining was later displaced by supervised convnets; the lasting contribution is the pair of datasets.

## See Also
- [[ILSVRC ImageNet Challenge]] — related (the larger benchmark that followed)
- [[AlexNet ReLU, Dropout and the Two-GPU ConvNet]] — related
- [[Residual Connections and the Degradation Problem]] — related (CIFAR-10 is the benchmark for its depth experiments)
- [[Convolution, Shift Sensitivity and Parameter Sharing]] — related
