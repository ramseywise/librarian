---
title: "GLIDE Text-Guided Diffusion"
tags: [multimodal, concept]
summary: "GLIDE is a 3.5B text-conditional diffusion model plus upsampler that compares CLIP guidance with classifier-free guidance, finds humans prefer the latter, and is fine-tuned for text-guided inpainting."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-nichol-2021-glide.md
---

# GLIDE Text-Guided Diffusion

GLIDE asks whether guided diffusion can make photorealistic images from text, and which kind of guidance does it better. The hypothesis is that classifier-free guidance beats CLIP guidance in human judgments of realism and caption match, since CLIP guidance may exploit the CLIP model used for evaluation.

## Mechanism

- A 3.5B-parameter ADM-style diffusion model at 64x64 (2.3B visual parameters plus a 1.2B transformer text encoder), and a 1.5B upsampler from 64 to 256, trained on the data used for DALL-E.
- **Classifier-free guidance** fine-tuned in by replacing 20% of captions with an empty sequence; at sampling the prediction is extrapolated from the unconditional toward the conditional one by scale s.
- **Noised CLIP** guidance: CLIP models trained on noised images so their gradients are valid during sampling.
- Text-guided inpainting by fine-tuning with four extra input channels.

## Results (self-reported)

- Human raters prefer classifier-free GLIDE over DALL-E for photorealism (MS-COCO captions, 256x256). Without reranking and at temperature 1.0, GLIDE wins photorealism 91%; against reranked DALL-E (temperature 0.85), GLIDE wins caption similarity 69%. Passing GLIDE samples through DALL-E's decoder still wins, by smaller margins.
- Classifier-free guidance (scale 3.0) gets the top human photorealism Elo, above CLIP guidance (scale 2.0) and no guidance. CLIP guidance raises the CLIP score further, but people disagree; the authors speculate it produces adversarial examples against the CLIP model used for scoring.
- Guidance gives a larger Elo gain than scaling the model about 10x: 3.5B at scale 3.0 scores 133.0 against -23.9 unguided; the 300M model at scale 4.0 scores 28.2 against -131.8 unguided.
- Zero-shot MS-COCO 256x256 FID with scale 1.5: 30k sampled captions, 250 steps, whole validation set as reference. Removing the 21% of validation images most similar to training images raised FID only slightly.
- Sampling takes about 15 seconds per image on one A100 (unoptimised).
- A 300M filtered model and a noised ViT-B CLIP are released.

## Limits

- Very unusual objects or scenarios fail, and sampling is far slower than a GAN.
- Optimizer, learning rate, hardware, dataset size and compute are not stated; human-evaluation details and confidence intervals are missing.
- The filtered model can keep dataset biases and guidance amplifies them; the filter targets just two US hate symbols. The released model can inpaint, which invites misuse.
- The adversarial-example account of CLIP guidance is only a hypothesis.

## See Also

- [[Diffusion and GAN Image Generation]] — related
- [[Classifier Guidance and the ADM Architecture]] — prerequisite-for
- [[Classifier-Free Diffusion Guidance]] — prerequisite-for
- [[unCLIP Hierarchical Text-Conditional Generation]] — extends
- [[Imagen Frozen Language Model Text Conditioning]] — alternative-to
- [[Make-A-Scene Scene-Based Text-to-Image Generation]] — alternative-to
- [[DALL-E and Parti Autoregressive Text-to-Image]] — alternative-to
