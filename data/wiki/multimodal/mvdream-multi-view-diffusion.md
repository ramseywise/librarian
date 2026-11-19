---
title: "MVDream Multi-View Diffusion"
tags: [multimodal, diffusion-and-image-generation, concept]
summary: "MVDream fine-tunes Stable Diffusion 2.1 to denoise four orthogonal views jointly with 3D (cross-view) self-attention and camera embeddings, giving a 3D prior for score-distillation text-to-3D that avoids multi-face Janus problems."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-shi-2023-mvdream.md
---

# MVDream Multi-View Diffusion

Shi and colleagues ask whether a text-to-multi-view diffusion model, made by fine-tuning a 2D text-to-image model with a mix of 3D renders and 2D data, can act as a 3D prior and fix the multi-face Janus problem and content drift seen when 2D models are lifted to 3D. Their hypothesis: a camera-conditioned single-view model, even a flawless one, falls short, and generating consistent views together with cross-view attention yields both consistency and generalisability. Results are self-reported.

## Mechanism

- Starting from Stable Diffusion 2.1 base, fine-tuning teaches it to denoise 4 orthogonal views at once. 2D self-attention is inflated to 3D, so all views attend to each other, and a 2-layer MLP camera embedding is added to the time embedding.
- Training batches are 70% Objaverse renders and 30% LAION 2D data.
- In threestudio, the model takes the place of Stable Diffusion in SDS, which optimises a hash-grid NeRF. The SDS loss amounts to an x0-reconstruction loss weighted by w(t) = 2 sigma_t / alpha_t.
- **Multi-view DreamBooth** fine-tunes the model on a few identity images for personalised 3D generation.

## Findings

- In a user study, 78% of votes went to MVDream over four threestudio baselines (40 prompts, 914 feedbacks from 38 users).
- Training on 3D and LAION together gives a lower FID than 3D data alone, and matches the validation-set CLIP score (validation set 30.12 +- 3.15); IS is 12.90 against 12.33 for 3D only (4-view images of 1,000 held-out subjects, DDIM).
- Fine-tuning takes roughly 3 days on 32 A100 GPUs, 50,000 steps at 256x256 with batch size 1,024. The SDS stage needs about 2 hours on a single V100, whereas ProlificDreamer needs over 10 hours.
- A 1-view model still has a severe Janus problem; the 4-view model barely suffers consistency issues. Qualitatively, inflated 3D self-attention did better than temporal attention and than a separately added 3D attention module. A random-view variant, trained with 4 views and run to produce 64 views at inference, gave worse quality than the orthogonal model.

## Limits

- Output is 256x256 where the base model gives 512x512, and the base model caps generalisability.
- The rendered dataset influences lighting and texture style.
- There is no quantitative 3D metric; text-to-3D is assessed qualitatively and through a user study (38 users, 40 prompts).
- The baselines are re-implementations in threestudio, not the originals, and differ from them (DeepFloyd stands in for Imagen or eDiff-I).
- Table 1 reports no seeds or baselines, FID comes without a standard deviation, and few-shot 3D reconstruction is left unexplored.

## See Also

- [[Latent Diffusion Models]] — prerequisite-for
- [[Textual Inversion and DreamBooth Personalization]] — prerequisite-for
- [[Diffusion and GAN Image Generation]] — prerequisite-for
