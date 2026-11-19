---
title: Batch Normalization
tags: [llm, architecture, concept]
summary: Batch Normalization (Ioffe & Szegedy, 2015) normalizes layer inputs using mini-batch statistics during training to reduce internal covariate shift — enables higher learning rates, reduces sensitivity to initialization, and acts as a regularizer. Rethinking BatchNorm (Wu & Johnson, 2021) exposes pitfalls with EMA population statistics, train/inference inconsistency, and domain shift.
updated: 2026-11-19
sources:
  - data/raw/pdfs/2015-02-11-batch-normalization.md
  - data/raw/pdfs/2021-05-01-rethinking-batch-norm.md
  - data/raw/papers/2026-11-08-fundamentals-of-deep-learning-ch05-convolutional-neural-networks.md
  - data/raw/papers/2026-11-07-ioffe-2015-batch-normalization.md
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
- **Enabling higher learning rates**: normalization prevents gradient explosion/vanishing from large parameter scales. BN(Wu) = BN((aW)u) — the output ignores weight scale (the paper's Jacobian claim is only a conjecture)
- **Regularization effect**: mini-batch statistics inject noise, reducing the need for Dropout
- **Enabling saturating nonlinearities**: BN-x5-Sigmoid achieved 69.8% accuracy where the same network without BN never exceeded 0.1%

## Key Results (Ioffe & Szegedy, 2015)

- BN-Baseline matches Inception accuracy in **less than half** the training steps
- BN-x5 (5x learning rate): reaches same accuracy in **14x fewer steps**
- BN-x30 (initial learning rate 0.045) reaches 74.8% accuracy after 6 million steps, which the paper notes is 5 times fewer steps than Inception needed to reach 72.2% (self-reported)
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

## CIFAR-10 worked example in a textbook (Fundamentals of Deep Learning, chapter 5)

The textbook describes batch norm as normalising each logit component across the minibatch, then restoring expressive power with trainable gamma and beta. It applies it to the logits before the nonlinearity and advises raising the learning rate (10x in its example) and dropping dropout and L2. On CIFAR-10 (two 5x5 conv layers of 64 filters, two max pools, fully connected layers of 384 and 192, softmax, Adam, random 24x24 crops; the batch-norm network uses the 10x learning rate and keep_prob 1), the batch-norm network reaches 96.7% accuracy against 92.3% without. Read from the training curves, it needs about 14,000 minibatches to pass 90% accuracy against over 80,000 without.

## Limits (textbook example)

- These are single runs with no variance; epochs and the base learning rate are not stated.
- The 96.7% figure was described as matching the state of the art, which later work far exceeds.
- The chapter explains batch norm through the internal-covariate-shift intuition.

## Details from the original paper's extraction (Ioffe and Szegedy, 2015)

All figures below are the authors' own results on ImageNet (self-reported).

- **Convolutional layers.** The normalisation pools the batch and every spatial location, with one mean, variance, scale and shift per feature map.
- **Scale invariance.** Multiplying a layer's weights by a constant a leaves the normalised output unchanged, so the gradient reaching those weights shrinks by 1/a. The paper's further claim about the layer Jacobian's singular values is labelled a conjecture, so read the Jacobian remark above with that in mind.
- **What the BN-x5 speedup bundles.** BN-x5 is the baseline plus a 5x learning rate, no Dropout, a fifth of the L2 weight, learning-rate decay 6x faster, no local response normalisation, more thorough shuffling and weaker image distortions. Only the BN-Baseline against BN-x5 contrast was run, so no single change is isolated. Better within-shard shuffling alone was credited with about 1% validation accuracy.
- **Instability without BN.** Raising the learning rate of the plain Inception network 5x from its initial 0.0075 drove its parameters to machine infinity.
- **Single model.** One BN-Inception network scores 25.2% top-1 error with one 224-pixel crop. With 144 crops its top-1 error is 21.99%; the extraction gives no top-5 value for either single-model setting.
- **Ensemble.** Six networks based on BN-x30, evaluated at 144 crops, reach 4.9% top-5 error on the 50,000-image validation set and 4.82% on the test set.

## Limits (original paper)

- Each result is a single run, with no seeds or variance, and progress is measured in training steps rather than wall-clock time.
- Momentum, L2 weight, decay rate, epsilon and hardware are not stated, and no code was released.
- The covariate-shift explanation rests on one activation in a small MNIST network.
- Recurrent networks and domain adaptation are left to future work.

## See Also
- [[Transformer Architecture]] — extends (uses layer norm, the successor to BN)
- [[Batch Norm Eval Mode and Small-Batch Failure]] — extends
- [[Pre-Norm vs Post-Norm and Warm-Up]] — related (where normalisation sits in the layer)
- [[NFNet Adaptive Gradient Clipping]] — alternative-to (trains deep ResNets without normalization)
- [[Big Transfer (BiT) Generalist Pretraining]] — related
- [[Convolution, Shift Sensitivity and Parameter Sharing]] — related (a textbook CNN that uses it)
- [[DCGAN Architectural Constraints for Stable GANs]] — related (uses it as a component)
- [[Weight Normalization Reparameterisation]] — alternative-to
- [[Layer Normalization]] — alternative-to
- [[Inception-v3 Factorized Convolutions and Label Smoothing]] — related
