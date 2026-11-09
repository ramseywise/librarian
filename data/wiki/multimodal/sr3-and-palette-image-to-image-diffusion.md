---
title: "SR3 and Palette Image-to-Image Diffusion"
tags: [multimodal, concept]
summary: "SR3 conditions a DDPM-style U-Net on a low-resolution image to do super-resolution; Palette reuses the idea, with the source image concatenated to the noisy target, for colorization, inpainting, uncropping and JPEG restoration."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-saharia-2022-image-super-resolution-iterative-refinement.md
  - data/raw/papers/2026-11-08-saharia-2022-palette.md
---

# SR3 and Palette Image-to-Image Diffusion

Both papers turn a diffusion model into a conditional image-to-image translator trained with a plain denoising loss, with no adversarial or auxiliary loss. SR3 targets super-resolution and doubles as the upsampling stage in cascaded generation; Palette asks whether one model with no task-specific tuning can handle several translation tasks.

## SR3

The bicubic-upsampled low-resolution image is concatenated with the noisy high-resolution target along the channel axis, and the noise level is supplied too; the net predicts the noise. T=2000 in training, but at most 100 refinement steps at sampling; since the noise level is an input, the inference schedule can be retuned after training.

- CelebA-HQ 16x16 to 128x128 (trained on FFHQ): about 50% of raters were fooled at 8x face super-resolution, whereas GAN methods reach no more than 34%; each pair appeared for 3 seconds beside ground truth (self-reported).
- ImageNet 64->256: SR3 has Inception score 180.1 against 121.1 for regression, but PSNR 26.4 against 27.9 and SSIM 0.762 against 0.801 (self-reported). The extraction reads this as PSNR and SSIM favouring blurry regression outputs. Fool rate is about 39% against 13-17% for regression (self-reported).
- A two-stage cascade (64x64 class-conditional DDPM, then 4x SR3) reaches FID 11.3 on 256x256 class-conditional ImageNet (self-reported). That is better than VQ-VAE-2 and near BigGAN at truncation 1.5, but behind BigGAN at truncation 1.0.
- Blurring the low-resolution input during training improves FID by about 2 points, and L1 edges out L2 (64 to 256 ImageNet; self-reported).

## Palette

An ADM-style U-Net at 256x256 without class conditioning receives the source image concatenated with the noisy target and trains on the noise-prediction loss. For inpainting and uncropping the hole is filled with Gaussian noise (no extra mask channel), the loss covers masked pixels only, and sampling keeps the known pixels fixed.

- Inpainting, ImageNet, 128x128 centre mask: FID 6.6 against DeepFillv2 18.0 (self-reported). Uncropping the right half: FID 5.8 against Boundless 18.7; on Places2 the human fool rate is 40% against 25% for Boundless and 15% for InfinityGAN (self-reported).
- JPEG restoration at QF=5: FID 8.3 against 29.0 for an identical-U-Net regression baseline (self-reported). Colorization: FID-5K 15.78 against ColTran 19.37, fool rate 47.80% against 36.55% (self-reported).
- L2 gives more diverse samples than L1 at comparable FID (inpainting LPIPS 0.13 for L2, 0.11 for L1) (self-reported).
- A single multi-task model gets inpainting FID 6.8 (specialist 6.6) and JPEG QF=5 FID 7.0 (specialist 8.3) (self-reported).
- Sampling takes 0.8 s per image on a TPUv4 over 1000 refinement steps (self-reported).

## Limits

- SR3: signs of mode dropping (near-identical outputs; smoothed skin that loses moles and piercings). The authors advise against real-world super-resolution use until such biases are understood. It fails on braided hair, frameless glasses and text. Its FID of 11.3 is behind BigGAN at truncation 1.0, which scores 7.4. Hardware, seeds and intervals go unreported; the human study covers 100 faces and few baselines.
- Palette: 1000 steps makes it much slower than GANs; group norm and self-attention tie it to one resolution (all work is at 256x256); no text conditioning. The multi-task model got the same number of steps as each specialist, so it may be undertrained.
- Internal inconsistency in the Palette extraction: the abstract and Section 4 name a ResNet-50 classifier while Appendix C.5 names EfficientNet-B0; the text also rounds the uncropping fool rates to 40/25/15.

## See Also

- [[Diffusion and GAN Image Generation]] — related
- [[Denoising Diffusion Probabilistic Models]] — prerequisite-for
- [[Classifier Guidance and the ADM Architecture]] — prerequisite-for
- [[Cascaded Diffusion Models]] — extends
- [[pix2pix Conditional Adversarial Image Translation]] — alternative-to
- [[SDEdit Guided Image Synthesis]] — alternative-to
- [[SPADE Spatially-Adaptive Normalization]] — alternative-to
