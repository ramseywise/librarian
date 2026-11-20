---
title: Dropout, Thinned Networks and Weight Scaling
tags: [data-science, deep-learning, concept]
summary: "Srivastava et al.'s dropout samples a thinned network per training case with Bernoulli masks and approximates averaging them at test time by scaling outgoing weights by p; gains appear across MNIST, SVHN, CIFAR, ImageNet and TIMIT but not on very small or very large data."
updated: 2026-11-20
sources:
  - data/raw/papers/2026-11-08-srivastava-2014-dropout.md
---

# Dropout, Thinned Networks and Weight Scaling

Srivastava, Hinton, Krizhevsky and co-authors propose dropping units at random during training to prevent co-adaptation and to cheaply approximate an average over exponentially many networks. All numbers are the paper's own (self-reported).

## Mechanism

- Each training case uses a **thinned network**: every unit in a layer is kept with Bernoulli(p) mask r, so the layer's output is r times y, and the rest of the forward pass is unchanged.
- At test time the unthinned network is used with outgoing weights multiplied by p (W_test = pW). The inverted variant multiplies retained activations by 1/p in training and leaves test weights alone.
- Monte-Carlo averaging of sampled thinned networks matched weight scaling at about k=50 samples (MNIST).
- Marginalised over the mask, dropout in linear regression turns into a ridge-style penalty: squared error against pXw plus p(1-p) times the squared norm of Gamma w, where Gamma is the square root of the diagonal of X^T X; no closed form is given for deep nets. See [[Dropout and Input Distortion as Ridge Regression]].
- Gaussian multiplicative noise with sigma = sqrt((1-p)/p) did slightly better than Bernoulli on MNIST (0.95 against 1.08, 2x1024, 10 seeds), described as preliminary.

## Reported results

- MNIST (permutation-invariant): standard 3x1024 logistic net 1.60% error against 1.35% with dropout (p=0.5 hidden, 0.8 input); ReLU with max-norm 1.06%; a 2x8192 net with over 65M parameters 0.95% without early stopping; DBM-pretrained net with dropout finetuning 0.79%. On a 784-1024-1024-2048-10 ReLU net dropout plus max-norm gave 1.05% against 1.62% for L2 alone.
- SVHN convnet: 3.95% to 3.02% (dropout in the fully connected layers) to 2.55% (all layers). CIFAR-10 without augmentation: 15.60 to 12.61; CIFAR-100: 43.48 to 37.20.
- ImageNet: the dropout convnet that won ILSVRC-2012 had about 16% top-5 error against about 26% for standard vision features; on ILSVRC-2010 it had 37.5 top-1 and 17.0 top-5 against 45.7 and 25.7 for SIFT plus Fisher vectors (reported).
- TIMIT phone error: 23.4% to 21.8% (6-layer net); pretrained nets 22.7% to 19.7%. Reuters-RCV1 gain was small (31.05% to 29.62%).
- Mean hidden activation in a 256-unit ReLU autoencoder dropped to about 0.7 from about 2.0, a sparser code.
- With n held constant (784-2048-2048-2048-10), test error stays level for p between 0.4 and 0.8, so p=0.5 is close to best. Holding pn constant instead, error at p=0.1 dropped from 2.7% to 1.7%.
- Dropout did nothing with 100 or 500 training examples; its benefit grows with data and then fades.

## Practical guide

The authors advise keeping hidden units with p=0.5 and real-valued inputs with p near 0.8; at least n/p hidden units in a layer; a learning rate 10-100x higher with momentum 0.95-0.99; max-norm with c of 3 to 4; for finetuning a pretrained net, scale its weights by 1/p first and use smaller learning rates.

## Limits

- Training with dropout runs two to three times slower than the same net without it, because the gradient updates are noisy.
- A Bayesian neural net beat dropout on the small alternative-splicing data (623 against 567 bits of code quality).
- Gains are slight on a large dataset such as Reuters and absent with only 100-500 MNIST examples.
- The ridge equivalence is derived only for linear regression.
- Batch size, seeds and compute are mostly unreported, and the networks are MNIST-scale MLPs and convnets, with no transformer or attention models.

## See Also
- [[Dropout and Input Distortion as Ridge Regression]] — related
- [[Early and Late Dropout]] — related
- [[Regularisation Knobs and Early Stopping]] — related
- [[AlexNet ReLU, Dropout and the Two-GPU ConvNet]] — related
