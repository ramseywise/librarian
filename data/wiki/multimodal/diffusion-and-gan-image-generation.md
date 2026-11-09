---
title: "Diffusion and GAN Image Generation"
tags: [multimodal, concept]
summary: "Map of the image-generation methods compiled from the multimodal engineering papers: diffusion foundations, guidance, text-to-image systems, editing and personalisation, GANs and their metrics, and token-based generators."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-brock-2018-large-scale-gan-training-high.md
  - data/raw/papers/2026-11-07-brooks-2023-instructpix2pix.md
  - data/raw/papers/2026-11-07-chang-2022-maskgit.md
  - data/raw/papers/2026-11-07-dhariwal-2021-diffusion-models-beat-gans-image.md
  - data/raw/papers/2026-11-07-esser-2021-taming-transformers-high-resolution-image.md
  - data/raw/papers/2026-11-07-gafni-2022-make-scene.md
  - data/raw/papers/2026-11-07-gal-2022-image-worth-one-word.md
  - data/raw/papers/2026-11-07-hertz-2022-prompt-prompt-image-editing-cross.md
  - data/raw/papers/2026-11-07-heusel-2017-gans-trained-two-time-scale.md
  - data/raw/papers/2026-11-07-ho-2020-denoising-diffusion-probabilistic-models.md
  - data/raw/papers/2026-11-07-ho-2021-cascaded-diffusion-models-high-fidelity.md
  - data/raw/papers/2026-11-07-ho-2022-classifier-free-diffusion-guidance.md
  - data/raw/papers/2026-11-07-ho-2022-video-diffusion-models.md
  - data/raw/papers/2026-11-07-isola-2017-image-image-translation-conditional-adversarial.md
  - data/raw/papers/2026-11-07-karras-2019-style-based-generator-architecture-generative.md
  - data/raw/papers/2026-11-07-karras-2021-alias-free-generative-adversarial-networks.md
  - data/raw/papers/2026-11-07-mokady-2022-self-distilled-stylegan.md
  - data/raw/papers/2026-11-07-nichol-2021-glide.md
  - data/raw/papers/2026-11-07-nichol-2021-improved-denoising-diffusion-probabilistic-models.md
  - data/raw/papers/2026-11-07-ramesh-2022-hierarchical-text-conditional-image-generation.md
  - data/raw/papers/2026-11-07-ruiz-2022-dreambooth.md
  - data/raw/papers/2026-11-07-saharia-2022-photorealistic-text-image-diffusion-models.md
  - data/raw/papers/2026-11-07-song-2019-generative-modeling-estimating-gradients-data.md
  - data/raw/papers/2026-11-07-song-2020-denoising-diffusion-implicit-models.md
  - data/raw/papers/2026-11-07-xu-2018-attngan.md
  - data/raw/papers/2026-11-07-zhang-2023-adding-conditional-control-text-image.md
  - data/raw/papers/2026-11-08-miyato-2018-spectral-normalization-generative-adversarial-networks.md
  - data/raw/papers/2026-11-08-peebles-2023-scalable-diffusion-models-transformers.md
  - data/raw/papers/2026-11-08-saharia-2022-image-super-resolution-iterative-refinement.md
  - data/raw/papers/2026-11-08-saharia-2022-palette.md
---

# Diffusion and GAN Image Generation

This page orders the image-generation papers in this wiki by the question each answers. Each method has its own page; numbers and limits live there, not here. Per-paper results are self-reported by the authors.

## Diffusion foundations

- Noise prediction and sampling: [[Denoising Diffusion Probabilistic Models]] covers DDPM, the score-based NCSN line, Improved DDPM and DDIM.
- Steering samples: [[Classifier Guidance and the ADM Architecture]] uses a separate classifier's gradient; [[Classifier-Free Diffusion Guidance]] drops the classifier by mixing conditional and unconditional predictions.
- Scaling resolution: [[Cascaded Diffusion Models]] chain a base model and super-resolution stages; [[SR3 and Palette Image-to-Image Diffusion]] apply diffusion to super-resolution and general image-to-image tasks.
- Backbone and modality: [[Diffusion Transformers (DiT)]] swap the U-Net for a transformer; [[Video Diffusion Models]] extend the model across time.

## Text-to-image systems

[[GLIDE Text-Guided Diffusion]] compares CLIP guidance with classifier-free guidance; [[unCLIP Hierarchical Text-Conditional Generation]] generates an image embedding from text first and decodes it; [[Imagen Frozen Language Model Text Conditioning]] conditions on a frozen text-only language model. [[Make-A-Scene Scene-Based Text-to-Image Generation]] and [[AttnGAN Attentional Text-to-Image GAN]] reach text-to-image through a token transformer and a GAN respectively.

## Editing and personalisation

[[Prompt-to-Prompt Cross-Attention Editing]] edits by reusing attention maps; [[InstructPix2Pix Instruction-Based Image Editing]] trains a model that follows written edit instructions; [[ControlNet Spatial Conditioning]] adds edge, depth or pose control to a frozen model; [[Textual Inversion and DreamBooth Personalization]] teach a model a user's own subject.

## GANs and their metrics

- Scale and stability: [[BigGAN Large-Scale GAN Training]] and [[Spectral Normalization for GANs]].
- Evaluation and training rule: [[Frechet Inception Distance and the Two Time-Scale Update Rule]].
- Architecture: [[StyleGAN Style-Based Generator]] (with the alias-free and self-distilled follow-ups) and [[pix2pix Conditional Adversarial Image Translation]] for paired translation.

## Token-based generation

[[VQGAN Taming Transformers]] makes a discrete image vocabulary and an autoregressive transformer over it; [[MaskGIT Masked Generative Image Transformer]] decodes the same tokens in parallel.

## How the methods relate

The ADM paper reports beating BigGAN on FID, and the MaskGIT and VQGAN papers compare against GAN baselines. The extraction notes mark the StyleGAN3 source as dated for text-to-image work; StyleGAN3 does not say so itself. Treat these as each paper's own comparisons under its own protocol, so cross-paper numbers are not directly comparable.

## What argues against it

Several extractions flag weak evidence: ControlNet, InstructPix2Pix and Prompt-to-Prompt rely on small user studies or qualitative figures, and Imagen and Palette each carry an internal inconsistency recorded on their pages.

## See Also

- [[Denoising Diffusion Probabilistic Models]] — instance-of
- [[Classifier Guidance and the ADM Architecture]] — instance-of
- [[Classifier-Free Diffusion Guidance]] — instance-of
- [[Cascaded Diffusion Models]] — instance-of
- [[SR3 and Palette Image-to-Image Diffusion]] — instance-of
- [[GLIDE Text-Guided Diffusion]] — instance-of
- [[unCLIP Hierarchical Text-Conditional Generation]] — instance-of
- [[Imagen Frozen Language Model Text Conditioning]] — instance-of
- [[Diffusion Transformers (DiT)]] — instance-of
- [[Video Diffusion Models]] — instance-of
- [[Prompt-to-Prompt Cross-Attention Editing]] — instance-of
- [[InstructPix2Pix Instruction-Based Image Editing]] — instance-of
- [[ControlNet Spatial Conditioning]] — instance-of
- [[Textual Inversion and DreamBooth Personalization]] — instance-of
- [[BigGAN Large-Scale GAN Training]] — instance-of
- [[Spectral Normalization for GANs]] — instance-of
- [[Frechet Inception Distance and the Two Time-Scale Update Rule]] — instance-of
- [[StyleGAN Style-Based Generator]] — instance-of
- [[pix2pix Conditional Adversarial Image Translation]] — instance-of
- [[AttnGAN Attentional Text-to-Image GAN]] — instance-of
- [[VQGAN Taming Transformers]] — instance-of
- [[MaskGIT Masked Generative Image Transformer]] — instance-of
- [[Make-A-Scene Scene-Based Text-to-Image Generation]] — instance-of
- [[SPADE Spatially-Adaptive Normalization]] — instance-of
- [[SDEdit Guided Image Synthesis]] — instance-of
- [[Pivotal Tuning Inversion]] — instance-of
- [[StyleCLIP Text-Driven StyleGAN Editing]] — instance-of
- [[Improved Techniques for Training GANs]] — instance-of
- [[LPIPS Perceptual Similarity]] — instance-of
