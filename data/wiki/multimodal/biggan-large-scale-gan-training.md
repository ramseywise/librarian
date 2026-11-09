---
title: "BigGAN Large-Scale GAN Training"
tags: [multimodal, concept]
summary: "BigGAN scales class-conditional GANs to batch 2048 and wider networks, adds orthogonal regularisation so a truncation trick can trade sample variety for fidelity, and documents why large GANs collapse."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-brock-2018-large-scale-gan-training-high.md
---

# BigGAN Large-Scale GAN Training

The paper asks whether GANs that are class-conditional and trained at far greater scale can give diverse, high-resolution ImageNet samples, and what limits their stability. The hypothesis is that larger batches and widths, orthogonal regularisation and a truncation trick narrow the gap to real images in fidelity and variety.

## Mechanism

The base is a self-attention GAN with a class-conditional ResNet generator and discriminator (BigGAN, plus a deeper BigGAN-deep variant), trained with hinge loss, [[Spectral Normalization for GANs]], a shared class embedding, hierarchical latent input ("skip-z") and an exponential moving average of generator weights. Training ran on TPU v3 pods at 128, 256 and 512 pixels with batch 2048.

- **Truncation trick.** Sample the latent vector, resample any value whose magnitude exceeds a threshold. Lower thresholds raise fidelity and cut variety.
- **Orthogonal regularisation.** A penalty on the off-diagonal part of W^T W, with strength 1e-4, enables the truncation trick.

## Results (self-reported)

- ImageNet 128x128, BigGAN-deep, truncation set so Inception Score matches real validation data: IS 166.5, FID 7.4, versus 52.52 and 18.65 for the self-attention GAN baseline. The best untruncated FID at 128x128 is 5.7.
- 256x256 gives IS 232.5 and FID 8.1; 512x512 gives IS 241.5 and FID 11.5 (same truncation rule).
- Batch 256 to 2048 raises IS by 46% (checkpoints taken just before collapse); widening channels by 50% adds 21%; shared embedding speeds training by 37%; skip-z adds about 4% and an 18% speedup.
- Orthogonal regularisation raises the share of runs that tolerate truncation from 16% to 60%.
- On a JFT-300M subset at 256x256, FID is 13.75 and IS 30.61 versus 48.38 and 23.27 for the baseline, and those runs remain stable for several hundred thousand iterations. CIFAR-10, untruncated: IS 9.22, FID 14.73.
- Instability analysis: discriminators memorise (train accuracy above 98%, validation 50-55%). An R1 gradient penalty of 10 stabilises training but cuts IS by 45%.

## Limits

- Full stability costs a lot of performance, so models are stopped early, just before collapse.
- Headline IS and FID depend on the chosen truncation setting; both metrics have known flaws (see [[Frechet Inception Distance and the Two Time-Scale Update Rule]]).
- The negative results hold only for the authors' own setup. Training needs 24 to 48 hours on a TPU pod, so the scale is costly to reproduce.

## See Also

- [[Diffusion and GAN Image Generation]] — related
- [[Spectral Normalization for GANs]] — prerequisite-for
- [[Frechet Inception Distance and the Two Time-Scale Update Rule]] — prerequisite-for
- [[Classifier Guidance and the ADM Architecture]] — related (the diffusion paper compares its FID against this GAN)
- [[Improved Techniques for Training GANs]] — prerequisite-for
