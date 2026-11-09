---
title: "MaskGIT Masked Generative Image Transformer"
tags: [multimodal, concept]
summary: "MaskGIT generates images by iteratively predicting all VQGAN tokens in parallel with a bidirectional transformer, keeping the most confident and re-masking the rest on a cosine schedule, in about 8 to 12 steps."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-chang-2022-maskgit.md
---

# MaskGIT Masked Generative Image Transformer

The paper asks whether a bidirectional transformer, trained to fill in masked image tokens, can generate in a few parallel decoding steps and outperform raster-scan autoregressive models. The hypothesis: scanning pixels in raster order is not the best, or most efficient, way to generate.

## Mechanism

Stage one reuses the [[VQGAN Taming Transformers]] tokenizer (16x downsampling, 1024-entry codebook). Stage two is a bidirectional transformer of 24 layers, trained to recover randomly masked tokens with the mask ratio drawn from a schedule. Generation begins with every token masked; in each of T steps the model predicts all tokens, samples them, retains the most confident, and re-masks the others following the schedule. The **mask scheduling function** sets how many tokens remain masked at each step, and a cosine schedule gave the best results. Inpainting, outpainting and class-conditional editing work with the same model and no architecture change.

## Results (self-reported)

Setup: ImageNet class-conditional, 227M parameters, no top-k, nucleus sampling or classifier guidance unless stated.

- Step counts are 8 at 256x256 and 12 at 512x512, versus 256 and 1024 for the VQGAN baseline. The claimed 30 to 64x speedup covers transformer decoding only, timed on one unspecified GPU.
- Unguided, FID at 256 is 6.18 against 6.95 for BigGAN-deep; recall is 0.51, lower than for ADM and Improved DDPM (0.63 and 0.62). At 512x512 it reports a new best FID, beating BigGAN-deep (8.43).
- Classifier-based rejection sampling at 0.05 acceptance gives IS 355.6, with FID 4.02, at 256x256.
- Cosine schedule: FID 6.06 at T=10 on 256x256; the best step count is about 8 to 12.
- Roughly 10% of tokens are enough for a holistic reconstruction, and the curve turns near a 90% mask ratio.
- Places2 inpainting (central 50%) lands close to CoModGAN in FID with no task training; outpainting right 50% gives the best FID against baselines evaluated at 256x256 while MaskGIT used 512x512.

## Limits

- Learning-rate schedule, warmup, step count, precision, seeds and the number of FID samples go unreported.
- Long outpainting drifts in semantics and colour; faces, text and symmetric objects show artifacts. The tokenizer is unchanged VQGAN.
- The speedup excludes the tokenizer and rests on one unnamed GPU.
- Internal inconsistency (per the extraction notes): the text says the effect of temperature annealing is discussed in Section 4.4, but no such experiment appears there.

## See Also

- [[Diffusion and GAN Image Generation]] — related
- [[VQGAN Taming Transformers]] — prerequisite-for
- [[Classifier Guidance and the ADM Architecture]] — related (diffusion baseline it is compared with)
- [[BEiT Masked Image Modeling with Visual Tokens]] — related
- [[Masked Autoencoders Pixel Reconstruction]] — related
