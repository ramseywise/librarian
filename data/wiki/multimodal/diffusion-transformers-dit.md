---
title: "Diffusion Transformers (DiT)"
tags: [multimodal, concept]
summary: "DiT replaces the convolutional U-Net of a latent diffusion model with a ViT-style transformer over latent patches, conditioned through adaLN-Zero blocks, and finds FID falls as transformer Gflops rise."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-peebles-2023-scalable-diffusion-models-transformers.md
---

# Diffusion Transformers (DiT)

The paper asks whether a standard transformer can replace the U-Net inside a latent diffusion model, and how sample quality scales with the transformer's forward-pass Gflops. The authors hypothesise that the U-Net's built-in bias is not essential and that ViT-style models bring favourable scaling.

## Mechanism

The images are encoded by a frozen off-the-shelf Stable Diffusion autoencoder. A first layer ("patchify") linearly embeds patches of the latent into tokens (patch sizes 2, 4 or 8); the denoiser is a stack of transformer blocks. Four ways of injecting timestep and class were compared: in-context tokens, cross-attention, adaptive layer norm (adaLN) and **adaLN-Zero**, which also regresses a per-dimension scale applied before each residual connection and initialises so each block starts as the identity. Twelve configurations (S/B/L/XL by patch size 8/4/2) were trained on class-conditional ImageNet; DiT-XL/2 was trained to 7M steps at 256x256 and 3M at 512x512.

## Results (self-reported)

- Across the 12 models at 400K steps without guidance, transformer Gflops correlate strongly and negatively with FID-50K.
- DiT-XL/2 with classifier-free guidance (scale 1.50, 250 DDPM steps) reports a new best FID-50K on ImageNet 256x256, beating the earlier diffusion best (LDM, 3.60), and it also improves on the earlier diffusion best at 512x512. FID 2.55 arrives after just 2.35M steps.
- No guidance, 256x256, 7M steps: FID 9.62. LDM-4 scores 10.56 and ADM 10.94.
- adaLN-Zero is the best block design; at 400K iterations its FID is close to half that of the in-context variant. Cross-attention adds roughly 15% Gflops, in-context a negligible amount.
- DiT-XL/2 needs far fewer Gflops than ADM for one forward pass: 118.6 against 1120 at 256x256, and 524.6 against 1983 at 512x512.
- Giving smaller models extra sampling compute does not close the gap: XL/2 at 128 steps (15.2 Tflops) outperforms L/2 at 1000 steps (80.7 Tflops).
- Guiding three channels at scale 1.5 equals guiding four at 1.375 (FID 2.20); a fine-tuned EMA decoder scores 2.27, against 2.46 for the original LDM decoder.
- No loss spikes were observed, without warmup or regularisation (lr 1e-4, batch 256).

## Limits

- Class-conditional ImageNet only; text-to-image use is proposed as future work. Scaling is shown only to 675M parameters and 118.6 Gflops at 256 px.
- Single runs with no seeds or variance. The Gflops-to-FID correlation is measured only at 400K steps. StyleGAN-XL keeps a lower FID at 512x512 (2.41 against 3.04).
- Hyperparameters came from ADM untuned, so the U-Net comparison could favour either side; guidance covered only 3 of 4 channels.
- Parameter and Gflop counts exclude the 84M-parameter autoencoder; the pipeline depends on that frozen pretrained model.

## See Also

- [[Diffusion and GAN Image Generation]] — related
- [[Denoising Diffusion Probabilistic Models]] — prerequisite-for
- [[Classifier Guidance and the ADM Architecture]] — prerequisite-for
- [[Classifier-Free Diffusion Guidance]] — prerequisite-for
- [[Swin Transformer Shifted Windows]] — related
