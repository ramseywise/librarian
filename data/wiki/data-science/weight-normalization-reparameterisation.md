---
title: Weight Normalization Reparameterisation
tags: [data-science, concept]
summary: "Weight normalization writes each weight vector as w = g v/||v|| and runs SGD on g and v; on its own it matched the ordinary parameterization on CIFAR-10, but paired with mean-only batch normalization it gave the paper's best error and it worked for DQN where batch norm did not."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-salimans-2016-weight-normalization.md
---

# Weight Normalization Reparameterisation

Salimans and Kingma test whether factoring every weight vector into a length and a direction can speed up SGD while costing less, and adding less noise, than batch normalization. Results are the paper's own (self-reported).

## Mechanism

- Reparameterise each neuron's weight vector as w = (g/||v||) v and run SGD on the scalar g and the vector v.
- The authors' hypothesis is that separating length from direction conditions the optimisation problem better, and unlike batch norm it does not depend on the minibatch.
- **Data-dependent initialisation:** set g = 1/sigma and b = -mu/sigma from one minibatch so pre-activations start at zero mean and unit variance. It cannot be used for RNN/LSTM, which use standard initialisation.
- **Mean-only batch normalization:** centre each pre-activation using the minibatch mean but skip the division by standard deviation; the paper pairs it with weight normalization.
- The authors argue the method is forgiving about the learning rate since the length of v keeps growing until the effective rate suits; no experiment tests this, and that argument is exact for plain SGD alone, and does not cover Adam or momentum.

## Results

Setup for CIFAR-10: a CNN based on ConvPool-CNN-C, without augmentation, trained with Adam for 200 epochs at batch 100, taking the best of four learning rates (0.0003 to 0.01).

| Variant | Test error |
|---|---|
| Weight norm + mean-only batch norm | 7.31% |
| Full batch norm | 8.05% |
| Weight norm alone | 8.46% |
| Normal parameterization | 8.43% |
| Mean-only batch norm, normal parameterization | 8.52% |

- In the authors' Theano code, batch norm ran about 16% slower than the standard parameterization, while weight norm showed no noticeable slowdown.
- DQN on Atari (Adamax, batch 64): maximum scores with weight norm against the normal parameterization were Space Invaders 2,179 against 1,779, Enduro 1,448 against 1,250, Seaquest 7,375 against 7,188 and Breakout 403 against 410. The authors say they could not get batch norm working for DQN unless the minibatch was impractically large.
- The convolutional VAE (MNIST, CIFAR-10) showed lower variance and a better optimum, read from a figure with no number; DRAW on MNIST converged faster without retuning, though 100 epochs were not enough to converge.

## Limits

- Each CIFAR-10 setting was run once, with no seeds or significance tests.
- The explanations for the mean-only batch norm gain (kurtosis of noise) are untested hypotheses.
- No ImageNet or large-scale language results, and no learning-rate robustness experiment.
- The CVAE CIFAR-10 architecture is deferred to an unpublished manuscript; the DQN comparison with Mnih et al. is confounded by reimplementation differences.

## See Also
- [[Batch Normalization]] — prerequisite-for
- [[Spectral Normalization for GANs]] — related
- [[Weight Initialisation and Activation Scale]] — related
