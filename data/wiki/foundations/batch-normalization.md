---
title: Batch Normalization
tags: [foundations, concept]
summary: Batch Normalization (Ioffe & Szegedy, 2015) normalizes layer inputs using mini-batch statistics during training to reduce internal covariate shift — enables higher learning rates, reduces sensitivity to initialization, and acts as a regularizer. Rethinking BatchNorm (Wu & Johnson, 2021) exposes pitfalls with EMA population statistics, train/inference inconsistency, and domain shift.
updated: 2026-07-19
sources:
  - raw/pdfs/2015-02-11-batch-normalization.md
  - raw/pdfs/2021-05-01-rethinking-batch-norm.md
---

# Batch Normalization

Batch Normalization (BN) normalizes the inputs to each layer using statistics computed over the mini-batch, stabilizing the distribution of activations during training.

## Core Algorithm

For each activation x(k) in a mini-batch B = {x_1, ..., x_m}:

1. Compute mini-batch mean: mu_B = (1/m) * sum(x_i)
2. Compute mini-batch variance: sigma_B^2 = (1/m) * sum((x_i - mu_B)^2)
3. Normalize: x_hat = (x - mu_B) / sqrt(sigma_B^2 + epsilon)
4. Scale and shift: y = gamma * x_hat + beta (learned parameters)

The learned gamma and beta allow BN to represent the identity transform — ensuring BN doesn't reduce the network's representation capacity.

## Why It Works

**Internal covariate shift**: the distribution of each layer's inputs changes during training as parameters of preceding layers change. This slows training by requiring lower learning rates and careful initialization.

BN addresses this by:
- **Stabilizing distributions**: layer inputs have fixed mean (0) and variance (1)
- **Enabling higher learning rates**: normalization prevents gradient explosion/vanishing from large parameter scales. BN(Wu) = BN((aW)u) — the scale doesn't affect the layer Jacobian
- **Regularization effect**: mini-batch statistics inject noise, reducing the need for Dropout
- **Enabling saturating nonlinearities**: BN-x5-Sigmoid achieved 69.8% accuracy where the same network without BN never exceeded 0.1%

## Key Results (Ioffe & Szegedy, 2015)

- BN-Baseline matches Inception accuracy in **less than half** the training steps
- BN-x5 (5x learning rate): reaches same accuracy in **14x fewer steps**
- BN-x30: reaches **74.8%** accuracy (vs 72.2% for Inception) in 5x fewer steps
- Ensemble: **4.9% top-5 validation error** on ImageNet, exceeding human raters

## Inference vs Training

During training: normalize with mini-batch statistics.
During inference: normalize with population statistics (mean/variance over the entire training set), making output deterministic.

Population statistics are typically estimated via Exponential Moving Average (EMA) during training.

## Rethinking BatchNorm (Wu & Johnson, 2021)

A thorough review of hidden caveats in BN, organized around choices for the "batch":

### EMA Inaccuracy
EMA population statistics can be inaccurate because:
- **Slow convergence**: large momentum (lambda) means many updates needed
- **Lagging behind**: EMA is dominated by historical features from earlier in training, not the current model state

**PreciseBN** alternative: after training, apply the fixed model to many mini-batches and aggregate batch statistics directly — more accurate than EMA.

### Train/Inference Inconsistency
BN uses mini-batch statistics during training but population statistics during inference. This mismatch can cause:
- Unstable validation performance
- Cases where using mini-batch statistics at inference (or population statistics during training) actually works better

### Domain Shift
When inputs come from different domains (multiple datasets, shared layers):
- Computing BN statistics from mixed domains causes domain shift
- Solution: compute separate BN statistics per domain

### Information Leakage
Mini-batch statistics create subtle information leakage between training samples within a batch.

## BN vs Layer Normalization

The [[Transformer Architecture]] uses Layer Normalization instead of BN — normalizing across features within a single sample rather than across the batch. This avoids batch-size dependency and is better suited to variable-length sequences.

## See Also
- [[Transformer Architecture]] — extends (uses layer norm, the successor to BN)
- [[LLM Fundamentals Interview Study Guide]] — instance-of
