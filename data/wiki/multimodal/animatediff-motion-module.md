---
title: "AnimateDiff Motion Module"
tags: [multimodal, video, concept]
summary: "AnimateDiff trains a temporal-Transformer motion module once on video, with a LoRA domain adapter absorbing the video-quality gap, so any personalised Stable Diffusion v1.5 checkpoint can be animated without per-model tuning; MotionLoRA adds new camera motions."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-guo-2023-animatediff.md
---

# AnimateDiff Motion Module

Guo and colleagues ask how to animate existing personalised text-to-image diffusion models with no tuning for each model. Their hypothesis: one motion module, trained a single time on video while a domain adapter takes up the video-quality gap, carries over to any personalised checkpoint built on the same base text-to-image model. Results are self-reported.

## Mechanism

- A **motion module** made of temporal Transformer layers goes into Stable Diffusion v1.5 after it is inflated, with training on WebVid-10M while the image layers are frozen.
- Before that, a LoRA **domain adapter** is fitted on still video frames so that it takes up the visual-quality gap. At inference it is removed or scaled by alpha, so the query is the usual projection of z plus alpha times the low-rank term A B^T z.
- **MotionLoRA** puts LoRA layers on the motion module's self-attention so that it can learn new motion patterns (zoom, pan, roll), from 20 to 50 reference videos augmented by rules.

## Findings

- In the user study AnimateDiff ranked best on motion smoothness and domain similarity; on text alignment it scored 2.210, marginally above Tune-a-Video. On CLIP metrics it has the highest smoothness and domain scores but the lowest text score.
- MotionLoRA needs 20-50 reference videos, 2,000 training iterations and roughly 30M of storage; with N = 5 videos it degrades significantly, while N = 50 learns the pattern. Ranks 2 (about 1M) and 128 (about 36M) give comparable motion.
- A motion module built from 1D temporal convolution, at the same parameter count, produces identical frames, so no motion, where the Transformer version does move (shown only in the supplementary material).
- Reducing the domain-adapter scaler from 1 to 0 raises visual quality and gets rid of the WebVid watermark (qualitative, first frame).

## Limits

- The quantitative evidence is a user study plus CLIP scores, measured against two adapted baselines; Gen-2 and Pika Labs (commercial) are compared only qualitatively.
- The PDF does not contain the study size, prompts or CLIP details; they are supplementary.
- AnimateDiff gets the lowest CLIP text score, and on domain similarity in the user study Text2Video-Zero comes out ahead.
- The motion module is tied to the base text-to-image model (SD v1.5) of the personalised checkpoints.
- The authors flag misuse risk: the method can generate human-related content, and community models may hold inappropriate content.

## See Also

- [[Latent Diffusion Models]] — prerequisite-for
- [[Video Latent Diffusion (Align Your Latents)]] — related
- [[Textual Inversion and DreamBooth Personalization]] — prerequisite-for
- [[ControlNet Spatial Conditioning]] — related (AnimateDiff reuses its zero initialisation and works with controllable generation)
- [[Diffusion and GAN Image Generation]] — prerequisite-for
