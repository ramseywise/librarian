---
title: "Latent Diffusion Models"
tags: [multimodal, diffusion-and-image-generation, concept]
summary: "Latent diffusion trains a diffusion model in the latent space of a pretrained perceptual autoencoder with mild downsampling (f = 4-8), cutting training and sampling compute while adding cross-attention conditioning for text, class and layout."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-rombach-2021-high-resolution-image-synthesis-latent.md
---

# Latent Diffusion Models

Rombach and colleagues ask whether running diffusion inside the latent space of a pretrained autoencoder can cut training and sampling compute a great deal without losing quality. Their hypothesis is that splitting perceptual compression (the autoencoder) from semantic generation (the diffusion model), with only mild downsampling, hits a near-optimal trade-off. Numbers are self-reported.

## Mechanism

- **Stage 1:** an autoencoder trained once with adversarial and perceptual losses (KL- or VQ-regularised, downsampling factor f).
- **Stage 2:** a UNet conditioned on time is trained in latent space to predict the noise epsilon (squared error between eps and eps_theta(z_t, t, tau(y))).
- **Conditioning:** domain encoders tau feed cross-attention, Attention(Q,K,V) with Q from the UNet features and K, V from tau(y); spatial conditions are concatenated along channels.
- **LDM-f** denotes a latent diffusion model at downsampling factor f, so LDM-1 is simply pixel-space diffusion. First-stage compression removes high-frequency detail; the second stage learns semantic composition.
- No delicate weighting of reconstruction against generative loss is needed, unlike LSGM, which the paper says LDM outperforms.

## Findings

- Class-conditional ImageNet 256x256, LDM-4 with classifier-free guidance: FID 3.60 at 400M parameters against ADM-G 4.59 at 608M (250 DDIM steps, scale 1.5).
- On class-conditional ImageNet at equal compute, LDM-8 is ahead of pixel-based LDM-1 by 38 FID points after 2M steps. LDM-4 and LDM-8 strike the best balance; LDM-1 and LDM-2 are slow to train, and LDM-32 stalls because compression is too strong (single A100, f from 1 to 32).
- Unconditional CelebA-HQ 256x256, LDM-4: FID 5.11 with 500 DDIM steps, which the authors report as a new best over likelihood-based models and GANs.
- Places inpainting: sampling is at least 2.7x faster and FID at least 1.6x better than for pixel-space diffusion with the same parameters; the large inpainting LDM-4 with 512 fine-tuning gets FID 1.50 against LaMa 2.23 (recomputed).
- Text-to-image, 1.45B model on LAION-400M: zero-shot MS-COCO FID of 12.63 with guidance scale 1.5, versus 23.31 without guidance (30,000 samples, 250 DDIM steps).
- Reconstructing ImageNet-val, the f = 4 autoencoder gets 0.58 R-FID with PSNR at 27.43, against DALL-E f = 8 at 32.01 and VQGAN f = 16 at 4.98.
- 4x super-resolution (ImageNet-Val 64 to 256): FID 2.8 (val features) or 4.8 (train features) against 5.2 for SR3, but with lower PSNR (24.4 against 26.4) and IS (166.3 against 180.1).
- Compute: 271 V100-days for LDM-4-G on ImageNet against 962 for ADM-G, and 60 against 232 on LSUN-Bedrooms. Humans prefer LDM-4 over a pixel-based model (70.6%) for super-resolution, and LaMa loses to LDM-4 (68.1%) for inpainting.

## Used by

[[Video Latent Diffusion (Align Your Latents)]], [[AnimateDiff Motion Module]], [[GLIGEN Grounded Text-to-Image]] and [[MVDream Multi-View Diffusion]] all start from a latent diffusion or Stable Diffusion checkpoint. The VQGAN autoencoder it extends is on [[VQGAN Taming Transformers]], and the guidance it uses on [[Classifier-Free Diffusion Guidance]].

## Limits

- The authors note that sequential sampling remains slower than a GAN.
- The autoencoder's reconstruction may limit tasks that need pixel-level accuracy; super-resolution is presumed affected.
- Optimiser, warmup, schedule, precision and seeds go unreported, and runs are single.
- In the f comparison each model's learning rate was tuned separately, a confound the authors acknowledge.
- Compute figures assume a x2.2 conversion from A100 to V100 and reuse numbers from Dhariwal and Nichol; the number of user-study raters is not given.
- Super-resolution trained on bicubic degradation does not generalise to other degradations; LDM-BSR was needed.
- Societal risks named by the authors: deepfakes, training-data leakage, bias amplification.

## See Also

- [[Denoising Diffusion Probabilistic Models]] — prerequisite-for
- [[Classifier-Free Diffusion Guidance]] — prerequisite-for
- [[VQGAN Taming Transformers]] — prerequisite-for
- [[Video Latent Diffusion (Align Your Latents)]] — extends
- [[AnimateDiff Motion Module]] — extends
- [[GLIGEN Grounded Text-to-Image]] — extends
- [[MVDream Multi-View Diffusion]] — extends
- [[Diffusion and GAN Image Generation]] — prerequisite-for
