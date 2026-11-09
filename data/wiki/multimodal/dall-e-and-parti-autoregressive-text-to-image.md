---
title: DALL-E and Parti Autoregressive Text-to-Image
tags: [multimodal, concept]
summary: "DALL-E and Parti generate images by predicting discrete image tokens with a transformer: DALL-E uses a 12B decoder over dVAE tokens, Parti an encoder-decoder up to 20B over ViT-VQGAN tokens."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-ramesh-2021-zero-shot-text-image-generation.md
  - data/raw/papers/2026-11-07-yu-2022-scaling-autoregressive-models-content-rich.md
---

# DALL-E and Parti Autoregressive Text-to-Image

Both systems turn text-to-image generation into next-token prediction over discrete image tokens, in two stages: a tokenizer compresses an image into a grid of codes, then a transformer models text and image tokens.

## DALL-E

A dVAE compresses every 256x256 image into a 32x32 grid whose tokens come from a vocabulary of 8192, cutting transformer context by a factor of 192. A 12B sparse decoder-only transformer models up to 256 BPE text tokens followed by 1024 image tokens as a single stream. A pretrained contrastive model (CLIP) then reranks the samples. The training set has 250M text-image pairs; the paper describes mixed-precision recipes (gradient scaling per resblock) and PowerSGD compression, and training ran for 430,000 updates at batch 1024 on 1024 V100 GPUs (self-reported).

Self-reported results: human raters prefer its zero-shot samples over DF-GAN for realism and for caption match (1000 MS-COCO captions, five MTurk votes each, best-of-512 reranking inferred). Zero-shot FID on 30,000 MS-COCO captions lands within 2 points of the strongest prior approach, and is best outright with slight blur (radius 1). Reranking gains continue up to 32 samples. On CUB it trails badly.

## Parti

A ViT-VQGAN tokenizer maps a 256x256 image to 1024 tokens (8192-entry codebook); an encoder-decoder transformer from 350M to 20B parameters maps text tokens to image tokens. Inference uses classifier-free guidance and 16 samples per prompt reranked with a CoCa model. The 20B model has 64 decoder layers against 16 encoder layers. The paper also introduces PartiPrompts, over 1600 prompts.

Self-reported results (MS-COCO 2014 val, 30,000 samples): zero-shot FID 7.23 for the 20B model, against 7.27 for Imagen, and 3.22 finetuned against 7.55 for Make-A-Scene. Zero-shot FID improves with scale, from 14.10 at 350M through 10.71 (750M) and 8.10 (3B) to 7.23 (20B). On Localized Narratives, the zero-shot figure is 15.97 and the finetuned one 8.39. Human raters choose zero-shot Parti over finetuned XMC-GAN (91.7% on realism, 90.5% on text match). On PartiPrompts, 20B is preferred over 3B for realism (56.8%) and text match (62.7%). The paper says scaling mostly helps text match rather than realism.

## Limits

- DALL-E: heavy dVAE compression loses high-frequency detail; CUB is far worse than prior work; variable binding is inconsistent. Some MS-COCO validation images were in its training data (taking them out did not change results). Weights, data and compute are not released; single run; the human evaluation compares only DF-GAN; baseline FID and IS values are read from figure curves.
- Parti: models, code and data are unreleased; training compute, seeds, sampling temperature and guidance dropout are not stated; human evaluation has no significance tests; the paper says FID alone ranks poorly (by eye Parti was much better than XMC-GAN at a similar FID); the comparison with diffusion is by FID only. Failures include counting past seven, spatial relations, negation, rendering text and feature blending.
- The Parti paper notes web-data bias and NSFW content and says the model is not for generating people.

## See Also
- [[Contrastive and Masked Vision-Language Pretraining]] — related (the family comparison; DALL-E's dVAE tokens are reused by BEiT)
- [[BEiT Masked Image Modeling with Visual Tokens]] — prerequisite-for (reuses the dVAE tokenizer)
- [[CLIP Contrastive Language-Image Pretraining]] — prerequisite-for (reranker)
- [[GLIDE Text-Guided Diffusion]] — alternative-to
