---
title: "VQGAN Taming Transformers"
tags: [multimodal, concept]
summary: "VQGAN compresses an image into a grid of discrete codebook indices using perceptual and patch-adversarial losses, then an autoregressive transformer models the index sequence, with a sliding window for megapixel images."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-esser-2021-taming-transformers-high-resolution-image.md
---

# VQGAN Taming Transformers

The paper asks whether transformers can generate high-resolution images when a CNN first supplies a compact discrete codebook of image parts that carries context. The hypothesis is that convolutions suit local structure while global composition needs a transformer, so the combination is both efficient and expressive.

## Mechanism

- **VQGAN:** a convolutional encoder and decoder around a learned codebook (a VQVAE variant), trained with a perceptual loss and a patch-level adversarial discriminator in place of L2. A 256x256 image turns into a 16x16 grid of indices. A weight balances reconstruction and adversarial gradients at the decoder's last layer.
- **Transformer:** a GPT-2-style model over the index sequence in raster order. Bigger images are sampled by sliding an attention window.
- One approach covers conditional synthesis from class, segmentation, depth, edges, pose and low resolution.

## Results (self-reported)

Several rows in the extraction lack their values; those are omitted here.

- In NLL on D-RIN at equal steps the transformer beats PixelSNAIL. On CIFAR-10, a transformer over a factor-2 VQGAN latent gets better FID than a pixel-level one at fixed compute.
- Sampling is much faster in latent space: a pixel-level sample took 7258 s on one GTX Titan X in the faces comparison.
- Raster order gave the best NLL among six orderings tried on ImageNet.
- The final class-conditional ImageNet model needed 45.8 days on one A100 (2.4M steps) and has roughly a tenth of VQVAE-2's parameters, whose count is an estimate.
- Face checkpoints chosen by best validation NLL had FID 10.2 and 9.6; those chosen by best training NLL had 3.86 and 2.68, so FID fails to reveal overfitting.

## Limits

- Task-specialised GANs report better FID (StyleGAN2 3.8 on FFHQ).
- The sliding window assumes roughly spatially invariant statistics, or spatial conditioning; reconstruction quality bounds sample quality, and compression beyond 16 degrades faces.
- Comparison numbers are copied from papers, not re-evaluated, except BigGAN. Optimizer and schedule are not stated.

## See Also

- [[Diffusion and GAN Image Generation]] — related
- [[MaskGIT Masked Generative Image Transformer]] — extends
- [[Make-A-Scene Scene-Based Text-to-Image Generation]] — extends
- [[StyleGAN Style-Based Generator]] — alternative-to (GAN route to high-resolution synthesis)
- [[DALL-E and Parti Autoregressive Text-to-Image]] — related
