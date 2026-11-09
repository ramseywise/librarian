---
title: "Cascaded Diffusion Models"
tags: [multimodal, concept]
summary: "A pipeline of separately trained diffusion models at rising resolution reaches strong class-conditional ImageNet FID with no classifier guidance, provided each super-resolution stage is trained on augmented low-resolution inputs."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-ho-2021-cascaded-diffusion-models-high-fidelity.md
---

# Cascaded Diffusion Models

The paper (CDM) asks whether a pipeline of diffusion models at rising resolution can match the best class-conditional ImageNet quality without classifier guidance. The hypothesis is that corrupting the low-resolution input given to each super-resolution stage cuts the compounding error caused by the gap between training inputs and generated ones.

## Mechanism

A 32x32 base model feeds a 32->64 super-resolution model, then a 64->128 or 64->256 model; each is a separately trained U-Net. **Conditioning augmentation** is data augmentation of the low-resolution input: Gaussian noise for the lower upsampling stages and Gaussian blur for the higher ones. Two noise variants exist: truncated (stop the low-resolution reverse process at timestep s and condition on that state) and non-truncated (sample fully, then corrupt with the forward process). Training amortizes over augmentation strength, so the strength can be searched after training.

## Results (self-reported unless noted)

- ImageNet class-conditional, 50k samples: FID 1.48 at 64x64, 3.52 at 128x128 and 4.88 at 256x256 (32->64->256 cascade), against BigGAN-deep 6.9 and ADM with upsampling 7.49 (no classifier guidance) at 256x256.
- Classification accuracy of a classifier trained on generated samples: 63.02% top-1 at 256x256 against 54.83% for VQ-VAE-2, and 59.84% top-1 at 128x128 against 40.64% for BigGAN-deep.
- Small ablation (16x16 base to 64x64 on ImageNet): without augmentation FID is 6.02, worse than the non-cascaded 64x64 baseline at 2.35; with non-truncated augmentation (s=1001) it is 2.13.
- 32->64 stage: FID 1.71 without augmentation and 1.48 with the best amortized setting. Truncated and non-truncated variants are about equally effective.
- When the conditioning is ground truth, FID gets worse as augmentation strength grows (0.76 at s=0, 1.11 at s=1501), the reverse of the generated-conditioning case.
- 64->256 stage: blur on 50% of training examples lowers FID from 7.26 to 6.18; class conditioning, larger batch and flips bring it to 4.88. Cutting inference to 4 steps only marginally degrades 256x256 FID.
- LSUN Bedroom 64->128: FID 2.30 at s=0 and 2.06 at s=251.

## Limits

- The authors concede that ADM with classifier guidance beats CDM on FID and IS; LOGAN's 3.36 beats CDM's 3.52 at 128x128; GANs win on Inception score once truncation is tuned for it.
- Avoiding guidance needs thousands of timesteps in the low-resolution models (4000, against hundreds for ADM).
- Gaussian noise augmentation gave negative results for the 128 and 256 upsamplers, so blur is used for those.
- Single runs, no seeds; the training-set FID was used for selection.

## See Also

- [[Diffusion and GAN Image Generation]] — related
- [[Denoising Diffusion Probabilistic Models]] — prerequisite-for
- [[SR3 and Palette Image-to-Image Diffusion]] — prerequisite-for
- [[Imagen Frozen Language Model Text Conditioning]] — extends
- [[Classifier Guidance and the ADM Architecture]] — alternative-to
