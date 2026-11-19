---
title: "Progressive Growing of GANs"
tags: [multimodal, gans, concept]
summary: "Progressive GAN starts the generator and discriminator at 4x4 and fades in layers as resolution doubles, adding minibatch standard deviation, equalized learning rate and pixelwise normalization, to reach 1024x1024 faces."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-karras-2017-progressive-growing-gans-improved-quality.md
---

# Progressive Growing of GANs

Karras and colleagues ask how to train a GAN stably at resolutions as high as 1024x1024 while keeping image quality and variety. The hypothesis is that growing both networks from low to high resolution is an easier curriculum. All numbers are the authors' own (self-reported).

## Components

- **Progressive growing.** G and D start at 4x4 and layers are added in mirrored fashion, each new layer faded in with a residual weight alpha that rises linearly from 0 to 1. One GAN is trained throughout; the loss is WGAN-GP with Adam and no batch or layer normalization.
- **Minibatch standard deviation.** For every feature and spatial position the standard deviation across the minibatch is computed, averaged into a single number, and appended to D as one extra constant feature map. It has no learnable parameters.
- **Equalized learning rate.** Weights are initialised from N(0,1) and divided at run time by each layer's He constant (w_hat = w/c), which gives every weight the same dynamic range under Adam or RMSProp.
- **Pixelwise feature vector normalization** in G, applied after each 3x3 convolution: each feature vector a is divided by the root of its mean squared entry plus eps (eps = 1e-8).
- **Sliced Wasserstein distance** computed on patch sets from Laplacian pyramids of generated and training images, and used to score quality and variation. The paper also introduces CELEBA-HQ, 30,000 images at 1024x1024 selected from 202,599 processed CELEBA images.

## Results

| Claim | Setup |
|---|---|
| About 5.4x speed-up to reach 6.4M real images (96 h against an extrapolated 520 h) | 1024x1024, single Tesla P100, fixed-layer against progressive |
| Training time roughly halved and a better optimum | CELEBA 128x128, Gulrajani WGAN-GP configuration, single P100 |
| Average SWD 9.28 (baseline) to 4.28 (progressive growing) to 2.96 (converged full model) | CELEBA 128x128, Table 1 |
| Minibatch standard deviation improves average SWD 9.84 to 7.04; minibatch discrimination improved no metric | CELEBA 128x128, Table 1 |
| Unsupervised CIFAR10 inception score 8.80 best run, 8.56 mean over 10 random initialisations; prior best unsupervised 7.90 | Network capped at 32x32, WGAN-GP with gamma = 750, no augmentation |
| The final sample set gets an FID of 7.30 and an average SWD of 5.44 | CELEBA-HQ 1024x1024; 8 V100 GPUs for 4 days |

Dropping the minibatch from 64 to 16 with no other change hurts badly (average SWD 46.23); adjusted training parameters bring it back to 8.07. On the MNIST-1K test with a crippled discriminator (about 500 parameters), WGAN-GP covers 640.1 modes, versus 856.7 with equalized learning rate plus pixelwise normalization and to 881.3 with minibatch standard deviation. The final 1024x1024 G and D each have 23.1M trainable parameters.

## What came after

[[StyleGAN Style-Based Generator]] redesigns this generator, and its StyleGAN2 revision revisits and removes progressive growing in favour of a skip generator and residual discriminator. The paper builds on the WGAN-GP loss and on ideas from [[Improved Techniques for Training GANs]] (minibatch discrimination, inception score) and uses the metric of [[Frechet Inception Distance and the Two Time-Scale Update Rule]].

## Limits

- The authors say there is a long way to go to true photorealism, citing weak semantic sensibility and dataset-dependent constraints, and image micro-structure that needs work.
- Other variation-increasing methods (unrolling, repelling regulariser, multiple generators) were not compared.
- The gamma = 750 WGAN-GP setting was tried only on CIFAR10.
- In their tests LSGAN was less stable than WGAN-GP and tended to lose variation late in long runs.
- The CIFAR10 record of 8.80 is a lucky run; the 10-run mean is 8.56.
- The 1024x1024 speed-up relies on extrapolating the non-progressive curve to 520 h.
- The Table 1 ablation is cumulative, not converged (10M images, reduced-capacity network), single run, no variance.
- The main runs give no step counts, precision or seeds; there is no human evaluation, and CELEBA-HQ has no held-out split.
- The method is GAN-based; later work in this wiki replaced the architecture (StyleGAN) and moved image synthesis to diffusion.

## See Also

- [[Generative Adversarial Nets Minimax Game]] — prerequisite-for
- [[Improved Techniques for Training GANs]] — prerequisite-for
- [[StyleGAN Style-Based Generator]] — extends
- [[Frechet Inception Distance and the Two Time-Scale Update Rule]] — related
- [[Diffusion and GAN Image Generation]] — prerequisite-for
