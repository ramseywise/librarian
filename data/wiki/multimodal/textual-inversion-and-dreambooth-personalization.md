---
title: "Textual Inversion and DreamBooth Personalization"
tags: [multimodal, concept]
summary: "Two ways to make a text-to-image model render a user's own subject from 3-5 photos: Textual Inversion learns one new word embedding in a frozen model, DreamBooth fine-tunes the model around a rare-token identifier with a prior-preservation loss."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-gal-2022-image-worth-one-word.md
  - data/raw/papers/2026-11-07-ruiz-2022-dreambooth.md
---

# Textual Inversion and DreamBooth Personalization

Both papers ask how a pretrained text-to-image model can render a user-provided subject in new scenes from 3-5 example images.

## Textual Inversion

One new token embedding (placeholder S*) is optimised with the latent-diffusion denoising loss on 3-5 images of the concept, using neutral prompt templates; the autoencoder, text encoder and denoiser are all frozen. The learned pseudo-word then goes into ordinary prompts.

- Setup: latent diffusion model (1.4B), 2xV100, batch 4, 5,000 steps at effective learning rate 0.04, about two hours per concept (self-reported). User study: two questionnaires of 600 responses each.
- About 5 training images work best on a headless-sculpture concept (1 to 25 tried); additional images drag the learned embedding further from those of real words, which hurts editability.
- A single-word embedding reconstructs about as well as multi-word baselines and edits better (CLIP metrics, numbers only in a figure). Human-written captions miss the likeness and reduce editability. Learning rate trades distortion against editability.

## DreamBooth

The model is fine-tuned on 3-5 photos captioned "a [V] [class noun]" with the usual denoising loss, plus a **prior-preservation** term evaluated on samples the frozen model itself produced for the bare class noun. With Imagen, the 64 to 256 super-resolution model is fine-tuned too (noise augmentation lowered from 1e-3 to 1e-5). The paper also contributes a 30-subject dataset and an evaluation protocol: DINO and CLIP-I for subject fidelity, CLIP-T for prompt fidelity. **Language drift** names the model gradually losing the ability to produce the subject's class.

- On Stable Diffusion, DreamBooth beats Textual Inversion on DINO subject fidelity (30 subjects, 25 prompts, 4 images each, 3,000 images); with Imagen it reaches DINO 0.696, with 0.774 for real images (self-reported).
- Users preferred DreamBooth for subject and prompt fidelity (72 users, 1800 answers; Stable Diffusion only) (self-reported).
- Ablation, 15 Imagen subjects: prior preservation reduces class collapse and increases diversity while subject fidelity dips slightly (DINO 0.684 against 0.712). With the right class noun DINO is 0.744, with none 0.303, with a wrong one 0.454 (5 subjects) (self-reported).
- Around 1000 iterations at lambda=1 suffice; learning rate is 1e-5 for Imagen and 5e-6 on Stable Diffusion; one TPUv4 (Imagen) or A100 (Stable Diffusion) takes roughly five minutes (self-reported).

## Limits

- Textual Inversion: poor at precise shapes; slow optimisation; cannot handle relations between several learned concepts; CLIP metrics are blind to shape; qualitative figures are partly curated (best of 16); only the 1.4B model was tested; no seeds or variance.
- DreamBooth: rare prompts can get the wrong context, and context and appearance entangle or overfit; one comparable baseline, on Stable Diffusion only; ablations use 2-15 subjects; optimizer, batch size, schedule and seeds are not stated.

## See Also

- [[Diffusion and GAN Image Generation]] — related
- [[Imagen Frozen Language Model Text Conditioning]] — prerequisite-for
- [[ControlNet Spatial Conditioning]] — related (another way to adapt a pretrained model)
