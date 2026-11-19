---
title: "DCGAN Architectural Constraints for Stable GANs"
tags: [multimodal, gans, concept]
summary: "DCGAN is a family of convolutional GAN architectures (strided and fractionally-strided convolutions, batchnorm, no fully connected hidden layers) that Radford, Metz and Chintala report trains stably in most settings, with discriminator features reaching 82.8% on CIFAR-10 (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-radford-2015-unsupervised-representation-learning-deep-convolutional.md
---

# DCGAN Architectural Constraints for Stable GANs

Radford, Metz and Chintala (ICLR 2016, under-review version, arXiv v2) ask whether architectural constraints can make convolutional GANs stable to train, and whether parts of the trained generator and discriminator work as general image representations.

## Architecture

The constraints: strided and fractionally-strided convolutions (some recent papers wrongly call the latter deconvolutions, the authors note), batchnorm, no fully connected hidden layers, and ReLU or LeakyReLU activations. The models are trained on ImageNet-1k, on LSUN bedrooms and on a set of faces. Features from the ImageNet-trained discriminator are fed to a linear L2-SVM, which is evaluated on CIFAR-10 and SVHN.

## Results (self-reported)

- CIFAR-10: the L2-SVM on ImageNet-1k discriminator features (all layers, max-pooled to 4x4, 28672 dimensions) reaches 82.8%. That tops the K-means pipelines (80.6% and 82.0%) and trails Exemplar CNN (84.3%).
- SVHN, 1000 labels, same feature pipeline: 22.48% test error, where the earlier best was 23.56% (stacked what-where autoencoders). Trained purely with labels, a CNN of the same architecture reached a validation error of 28.87% (best of 64 random-search trials), which shows the architecture alone does not explain the gap.
- MNIST: nearest-neighbour test error on conditional DCGAN samples is 1.48% at 10M samples (10K validation split), where real data gives 3.1% and a baseline GAN gives 6.28% and 5.65%.
- LSUN bedrooms: hashing with a denoising autoencoder removed approximately 275,000 near duplicates. About 200 feature maps were selected as window-predictive by logistic regression on the second-highest convolutional layer; dropping them mostly erases windows from generated bedrooms (qualitative, Fig 6).
- Arithmetic on the latent Z is stable only when the Z vectors of three exemplars are averaged, whereas single samples were unstable (qualitative, Figs 7 and 8).

## Limits

- The authors admit the instability is not gone: on longer runs some filters collapse into a single oscillating mode.
- Fine-tuning the discriminator features is left for later work, and Exemplar CNN beats DCGAN on CIFAR-10.
- Evidence of sample quality is mostly qualitative; no log-likelihood or sample-quality metric is given.
- The text omits layer counts, channel widths, training steps and seeds, and no code is linked.
- The SVHN comparison sets DCGAN's test error against a supervised CNN's validation error.

## See Also
- [[Batch Normalization]] — prerequisite-for
- [[Diffusion and GAN Image Generation]] — related
- [[Improved Techniques for Training GANs]] — related
- [[Frechet Inception Distance and the Two Time-Scale Update Rule]] — related (reports FID for DCGAN)
- [[BigGAN Large-Scale GAN Training]] — related
