---
title: "Frechet Inception Distance and the Two Time-Scale Update Rule"
tags: [multimodal, concept]
summary: "TTUR gives a GAN's discriminator and generator separate learning rates, with a convergence argument to a local Nash equilibrium, and the paper introduces FID, a Gaussian distance between Inception features of real and generated images."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-heusel-2017-gans-trained-two-time-scale.md
---

# Frechet Inception Distance and the Two Time-Scale Update Rule

The paper asks whether GANs with separate discriminator and generator learning rates can be shown to converge to a local Nash equilibrium, and how image GANs ought to be evaluated. It contributes the **two time-scale update rule (TTUR)**, a distinct learning rate per network, and the **Frechet Inception Distance (FID)**.

## FID

Fit one Gaussian (mean and covariance) to Inception-v3 pool-layer activations of real images and another to those of 50,000 generated images, then take the Frechet distance. On CelebA, six disturbances (noise, blur, rectangles, swirl, salt-and-pepper, contamination with ImageNet images) made FID climb steadily, while Inception Score fluctuated, stayed flat or fell.

## TTUR

Use Adam with separate rates b for the discriminator and a for the generator. The convergence argument treats Adam as a heavy ball with friction and needs assumptions including Lipschitz gradients (which excludes ReLU) and stationary second moments.

## Results (self-reported)

Best FID over training, 8 runs per setting unless noted; learning rates differ per experiment.

- DCGAN, CelebA: 12.5 against 21.4 with one time-scale.
- WGAN-GP, LSUN Bedrooms: 9.5 against 20.5. WGAN-GP, CIFAR-10: 24.8 against 29.3.
- DCGAN, LSUN Bedrooms: 57.5 against 70.4. DCGAN, CIFAR-10: 36.9 against 37.7, a gain of only 0.8.
- Character-level WGAN-GP on One Billion Word: normalised JSD 0.35 against 0.38 (4-gram) and 0.74 against 0.77 (6-gram), 10 runs.
- BEGAN: no gain, because its equilibrium term couples the two gradients.

## Limits

- The proof excludes ReLU networks and needs stationary gradient moments for Adam.
- Learning rates are searched per experiment, best-over-training FID is reported, and there is no significance test.
- Theory suggests a faster discriminator, yet DCGAN here uses a larger generator rate; the authors argue this is not contradictory.
- FID assumes Gaussian Inception features and relies on an ImageNet-trained network. Dataset sizes, batch sizes and architectures are not stated.

## See Also

- [[Diffusion and GAN Image Generation]] — related
- [[BigGAN Large-Scale GAN Training]] — related (reports FID alongside Inception Score)
- [[Spectral Normalization for GANs]] — related (another stabiliser for GAN training)
- [[Improved Techniques for Training GANs]] — prerequisite-for (introduces the Inception score)
- [[LPIPS Perceptual Similarity]] — alternative-to
