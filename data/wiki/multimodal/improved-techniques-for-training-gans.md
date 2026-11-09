---
title: Improved Techniques for Training GANs
tags: [multimodal, concept]
summary: "Salimans et al. propose five heuristics for stabilising GAN training, a K+1-class semi-supervised GAN, and the Inception score as an automatic sample-quality metric (self-reported results on MNIST, CIFAR-10 and SVHN)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-salimans-2016-improved-techniques-training-gans.md
---

# Improved Techniques for Training GANs

Salimans et al. (preprint) ask how to make GAN training and samples better and how to score samples without human raters.

## Techniques

- **Feature matching:** the generator is trained by feature matching, which the paper uses for semi-supervised learning.
- **Minibatch discrimination:** the discriminator sees several examples jointly through a tensor and L1 distances across the minibatch.
- **Three stabilising tricks, namely historical averaging, one-sided label smoothing and virtual batch normalization:** virtual batch normalization normalises every example using statistics of a reference batch, picked once at the start of training, combined with the example.
- **Semi-supervised GAN:** the discriminator becomes a classifier over K+1 classes, the K real ones plus a generated class, and learns from supervised cross-entropy alongside the GAN loss.
- **Inception score:** exp of the expected KL divergence between the Inception model's label distribution for a sample and the marginal label distribution; computed over 50,000 samples because it partly measures diversity.

## Results (self-reported)

- MNIST (permutation invariant, feature matching): 200 labels, 90 +/- 4.2 errors (single model, 10 seeds); 100 labels, 93 +/- 6.5 single and 86 +/- 5.6 for a 10-model ensemble, against 96 +/- 2 for an auxiliary deep generative model.
- On CIFAR-10 the error is 18.63% given 4000 labels (15.59% for an ensemble), and 17.72% given 8000. On SVHN given 2000 labels it is 6.16 +/- 0.58% for one model and 5.88 +/- 1.0 for an ensemble.
- Inception scores on 50,000 CIFAR-10 samples: real data reaches 11.24 and the full method 8.09. Without minibatch features it is 3.87. Other ablations give 7.54 (-VBN+BN), 6.86 (-L+HA), 6.83 (-LS) and 4.36 (-L).
- Crowd-platform raters told minibatch-discrimination MNIST samples from real ones 52.4% of the time over 2000 votes, where chance is 50%. On CIFAR-10 they were correct 78.7% of the time, and 71.4% on the top 1% ranked by Inception score. The authors themselves did better than 95%.

## Limits

- The authors call Inception score a rough guide, and directly optimising it yields adversarial examples. Techniques are heuristic, with no convergence guarantee.
- Rater outcomes hinge on motivation and feedback. ImageNet samples at 128x128 show wrong anatomy and come with no quantitative result. The paper omits the optimizer, learning rates, batch size and step counts.

## See Also
- [[Diffusion and GAN Image Generation]] — related
- [[Frechet Inception Distance and the Two Time-Scale Update Rule]] — extends (a later metric built on Inception features)
- [[Spectral Normalization for GANs]] — extends
- [[BigGAN Large-Scale GAN Training]] — extends
