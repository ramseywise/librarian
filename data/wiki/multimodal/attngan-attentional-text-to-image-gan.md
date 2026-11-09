---
title: "AttnGAN Attentional Text-to-Image GAN"
tags: [multimodal, concept]
summary: "AttnGAN generates images in three stages that attend to individual words per image sub-region, and adds a word-level image-text matching loss (DAMSM) to the GAN loss."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-xu-2018-attngan.md
---

# AttnGAN Attentional Text-to-Image GAN

The paper asks whether a multi-stage text-to-image GAN does better when it attends to individual words and is trained with a finer image-text matching loss, rather than conditioning on one sentence vector. The hypothesis is that a single sentence vector loses word-level detail, so letting each image sub-region look at the words that matter should help, particularly on complex scenes.

## Mechanism

The generator has three stages (64, 128, 256 pixels). From the second stage on, an attention layer lets each image sub-region query the word vectors, and the attended context joins the next stage's input. A pretrained **DAMSM** (Deep Attentional Multimodal Similarity Model: a bidirectional LSTM text encoder plus an Inception-v3 image encoder) embeds sub-regions and words together and supplies a word-level matching loss, which is added to the GAN loss with a weight lambda.

## Results (self-reported)

- COCO test set, 256x256, lambda 50: inception score 25.89 against the previous best reported 9.58 (PPGN). R-precision 85.47% over 100 candidate texts.
- CUB test set, lambda 5: inception score 4.36 against 3.82 for StackGAN-v2.
- Ablation on CUB: without DAMSM, R-precision is 10.37% and inception score 3.98, whereas the full model reaches R-precision 67.82. Raising lambda from 0.1 to 5 lifts a one-attention model from 16.55% to 58.65%.
- Adding the second attention stage (128 to 256) gives R-precision 63.87 to 67.82 on CUB and a slightly higher inception score.

## Limits

- Images can be sharp and detailed yet unrealistic (birds with several heads, eyes or tails), because overall coherent structure is not captured. COCO output is less photorealistic than CUB.
- A third attention stage was not tried for GPU memory reasons.
- Training details such as optimizer, step size, batch and epoch counts, plus the hardware used, are missing.
- R-precision relies on the authors' own DAMSM encoders, which also shaped training. There is no human evaluation, and the evidence for attention is qualitative. The authors concede that inception score does not show whether an image matches its text.

## See Also

- [[Diffusion and GAN Image Generation]] — related
- [[Make-A-Scene Scene-Based Text-to-Image Generation]] — related (a later text-to-image system with extra control)
- [[Imagen Frozen Language Model Text Conditioning]] — alternative-to (text-to-image with a frozen language model instead of GAN stages)
