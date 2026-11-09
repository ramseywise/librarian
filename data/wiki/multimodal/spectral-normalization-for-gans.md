---
title: "Spectral Normalization for GANs"
tags: [multimodal, concept]
summary: "Spectral normalization divides each discriminator weight matrix by its largest singular value, estimated with one power-iteration step, to stabilise GAN training more cheaply than gradient penalties and without collapsing weight rank."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-miyato-2018-spectral-normalization-generative-adversarial-networks.md
---

# Spectral Normalization for GANs

The paper asks whether bounding the spectral norm of each discriminator layer stabilises GAN training at lower cost and more robustly than weight clipping, weight normalisation, orthonormal regularisation or a gradient penalty. The hypothesis: dividing every weight matrix by its largest singular value caps how fast the discriminator can change its output, yet keeps the weights from losing rank.

## Mechanism

Replace each discriminator weight matrix W by W divided by sigma(W), its largest singular value. A single power-iteration step per update estimates sigma(W), reusing the vector from the previous step. For a linear layer the Lipschitz constant equals sigma(W), so the layerwise product bounds the whole network. Weight clipping and weight normalisation, by the paper's analysis, favour low-rank layers, while spectral normalisation spreads singular values more broadly.

## Results (self-reported)

Setups: CIFAR-10, STL-10 and ImageNet, compared with seven alternatives under six Adam settings, best setting reported.

- CIFAR-10 ResNet with hinge loss: inception score 8.22 and FID 21.7, against FID 23.8 for orthonormal regularisation. With the standard CNN, 7.42 against 7.40 for orthonormal regularisation, above clipping, WGAN-GP and the other normalisers.
- WGAN-GP fails at high learning rate and momentum while spectral normalisation stays robust. Per-layer spectral norms stay near 1 with one power iteration.
- Cost is about 110 to 120% of weight normalisation time and much cheaper than WGAN-GP.
- Conditional ImageNet at 128x128: inception score 21.1 after 450K generator updates; intra-class MS-SSIM 0.101 against about 0.25 for AC-GAN (the latter taken from another paper), read as less mode collapse.
- Doubling generator width helped spectral normalisation but hurt WGAN-GP. Adding a learned scale to a spectrally normalised layer raised WGAN-GP inception score from 6.68 to 7.20 and cut FID from 40.1 to 32.0.

## Limits

- Table rows compare methods differing in optimiser and architecture, as the authors concede.
- Orthonormal regularisation beats it slightly on STL-10 with the standard CNN (8.56 against 8.28).
- The bound is an upper bound; no theory explains the quality gain. Only Inception score and FID at 32x32 to 128x128; no precision/recall, human study, seed count or batch size.
- Each method gets only six settings and no significance test. The extraction notes add that diffusion models have since replaced GANs for most image work.

## See Also

- [[Diffusion and GAN Image Generation]] — related
- [[BigGAN Large-Scale GAN Training]] — extends
- [[Frechet Inception Distance and the Two Time-Scale Update Rule]] — related (the evaluation metric used here)
- [[Improved Techniques for Training GANs]] — prerequisite-for
