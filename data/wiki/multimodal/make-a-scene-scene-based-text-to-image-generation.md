---
title: "Make-A-Scene Scene-Based Text-to-Image Generation"
tags: [multimodal, concept]
summary: "Make-A-Scene conditions a 4B-parameter autoregressive transformer on text plus optional segmentation (scene) tokens, uses region-aware tokenizer losses, and applies classifier-free guidance to logits."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-gafni-2022-make-scene.md
---

# Make-A-Scene (scene-conditioned text-to-image)

The paper asks whether text-to-image generation can be made more controllable, rated higher by people, and reach 512x512 by adding segmentation-derived scene tokens, tokenizer losses aimed at faces and objects, and guidance without a classifier, all on an autoregressive transformer.

## Mechanism

A GPT-3-style autoregressive transformer with 4B parameters reads a sequence of text, scene and image tokens. Scene tokens are produced by VQ-SEG, a VQ-VAE trained on panoptic, human and face segmentation with an added edge channel. Image tokens are produced by VQ-IMG, a [[VQGAN Taming Transformers]] variant with feature-matching losses that stress faces and objects. The scene input is optional ("implicit conditioning": the network may ignore it). Guidance works on logits, adding a scale times the conditional-minus-unconditional gap to the unconditional logits, so samples need no reranking after generation.

## Results (self-reported)

Setup: MS-COCO validation prompts, 30k images, no reranking.

- 256x256 model: FID 7.55, lowest among compared models trained with COCO; filtered FID (no COCO train data) 11.84 against 12.24 for GLIDE. The train-versus-val lower bound is 2.47.
- With scene input the best model reaches FID 4.69.
- Ablation (cumulative rows): guidance lowers FID from 14.45 to 7.55; scene tokens alone move FID from 18.01 to 19.16 yet people prefer the result. The 512 model has FID 8.70 and 62.0% preference for quality.
- Pairwise AMT (500 pairs, 5 raters each): chosen over CogView on quality 92.2% of the time and over the authors' re-implemented DALL-E on text alignment 65.9%; in the ablation, guidance is preferred 76.8% on quality.

## Limits

- No code, weights or data release is stated; compute and hardware are not given. No seeds, intervals or significance tests.
- Baselines differ in training data, and the DALL-E comparison uses the authors' own re-implementation.
- The lowest FID comes from the 256 model while people favour 512. Scene categories are fixed, so absent classes need substitutes. Ablation rows are cumulative, so effects depend on order.

## See Also

- [[Diffusion and GAN Image Generation]] — related
- [[VQGAN Taming Transformers]] — prerequisite-for
- [[Classifier-Free Diffusion Guidance]] — prerequisite-for
- [[GLIDE Text-Guided Diffusion]] — alternative-to (diffusion baseline it is compared with)
