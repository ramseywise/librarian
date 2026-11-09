---
title: "Classifier Guidance and the ADM Architecture"
tags: [multimodal, concept]
summary: "Dhariwal and Nichol re-engineer the diffusion U-Net (ADM) and steer sampling with gradients from a classifier trained on noisy images, trading diversity for fidelity and reaching lower FID than BigGAN-deep on ImageNet."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-dhariwal-2021-diffusion-models-beat-gans-image.md
---

# Classifier Guidance and the ADM Architecture

The paper asks whether diffusion models can match GANs on sample quality once the architecture is improved and a way to trade diversity for fidelity is added. The authors attribute the earlier gap to heavily refined GAN architectures and to the GAN ability to trade diversity for fidelity.

## Mechanism

- **ADM** (ablated diffusion model): the [[Denoising Diffusion Probabilistic Models]] U-Net with more attention heads, attention at multiple resolutions, BigGAN-style resampling blocks and adaptive group normalization. Training uses the hybrid objective and learned variances from Improved DDPM.
- **Classifier guidance** (ADM-G): a separate classifier is trained on noisy images. At each sampling step the reverse-step mean is shifted by the classifier's log-probability gradient for the target class, scaled by a factor s. Larger s raises precision and lowers recall.
- **ADM-U**: a two-stage upsampler; guidance is applied only to the low-resolution model.

## Results (all self-reported, single runs)

- ImageNet 128x128, 250 steps, scale 0.5: FID 2.97, against BigGAN-deep 6.02.
- ImageNet 256x256, 250 steps, scale 1.0: FID 4.59 against BigGAN-deep 6.95. ImageNet 512x512, 250 steps, scale 4.0: FID 7.72 against 8.43.
- With the ADM-U upsampler, 250 base and 250 upsample steps: FID 3.94 at 256x256 and 3.85 at 512x512.
- Unconditional ImageNet 256x256 after 2M iterations: guidance at scale 10.0 gives FID 12.00, against 26.21 unguided.
- Using 25 DDIM steps at scale 2.5 on 256x256, ADM-G still outperforms BigGAN-deep. The classifier-scale-1.0 training curve (so a guided run) crosses BigGAN-deep's FID after 750K iterations, about one third of training, where FID is 6.49.
- Compute: ADM-G at 256x256 for 1980K iterations costs 962 V100-days (916 generator, 46 classifier). The paper says the best FID from guided models takes far more compute than BigGAN-deep.
- LSUN Bedrooms 256x256, 1000 steps: FID 1.90 against StyleGAN 2.35.
- Compared with the BigGAN truncation trick (ImageNet 128x128), guidance gives a better FID/IS trade-off but does not reach the top precision. Lowering the sampling temperature gave little gain and blurry images.

## Limits

- Diffusion sampling is slower than GAN sampling because it needs many forward passes.
- Guidance depends on class labels; the paper offers nothing for unlabeled data.
- On LSUN, 1000 sampling steps were used; a swept 250-step schedule mostly closed the gap, though the sweep was not exhaustive.
- FID is an imperfect proxy for sample quality; single runs without seeds or intervals; several baseline values are copied from earlier papers.

## See Also

- [[Diffusion and GAN Image Generation]] — related
- [[Denoising Diffusion Probabilistic Models]] — prerequisite-for
- [[Classifier-Free Diffusion Guidance]] — extends
- [[GLIDE Text-Guided Diffusion]] — extends
- [[Cascaded Diffusion Models]] — alternative-to
- [[BigGAN Large-Scale GAN Training]] — alternative-to
