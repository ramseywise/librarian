---
title: "unCLIP Hierarchical Text-Conditional Generation"
tags: [multimodal, concept]
summary: "unCLIP first generates a CLIP image embedding from a caption with a prior, then decodes it to pixels with a diffusion decoder and upsamplers, gaining image diversity at a small cost in caption match."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-ramesh-2022-hierarchical-text-conditional-image-generation.md
---

# unCLIP Hierarchical Text-Conditional Generation

The paper asks whether producing a CLIP image embedding from the caption first, and the image from that embedding second, gives more diversity while keeping photorealism and caption match. unCLIP is the whole stack: a **prior** (autoregressive or diffusion) turns the caption into a CLIP image embedding; a GLIDE-style diffusion **decoder** inverts the CLIP image encoder at 64x64; two diffusion upsamplers then reach 256 and finally 1024 pixels. CLIP is frozen; the prior, decoder and upsamplers are trained. The decoder keeps a residual latent from DDIM inversion, so each image becomes a **bipartite latent** (embedding plus residual), which allows variations, interpolations and "text diffs": rotating an image embedding along the normalised difference of two CLIP text embeddings.

## Results

- Best zero-shot MS-COCO FID among the compared zero-shot models with the diffusion prior (256x256, decoder guidance 1.25) (self-reported).
- Pairwise human evaluation against GLIDE (n=1000, hyperparameters swept using a proxy): GLIDE is slightly preferred on photorealism and wins on caption similarity, but the diffusion-prior unCLIP is strongly preferred on diversity (two 4x4 grids per caption over 1,000 MS-COCO captions) (self-reported). GLIDE at guidance scale 2.0 nearly matches unCLIP on photorealism and caption similarity but is less diverse.
- Win rates against GLIDE are lower for the autoregressive prior than for the diffusion prior. The paper claims the diffusion prior beats the autoregressive one at similar size, with less training compute.
- Small models: feeding the decoder a prior-generated image embedding beats a text embedding or caption alone on FID (small stack FID 7.99) (self-reported).
- PCA retains 319 of the 1,024 CLIP dimensions at under 1% mean-squared reconstruction error, so the autoregressive prior sees three times fewer tokens (CLIP trained with SAM) (self-reported).
- Aesthetic probe (512 GPT-3-written prompts, 4 images each, linear probe on AVA) (self-reported): guiding the decoder improves the aesthetic score at no cost to recall, while guiding the prior hurts.

## Limits

- Binding attributes to objects is weaker than GLIDE, and rendered text is incoherent (qualitative); the authors suspect the CLIP embedding and BPE encoding.
- Weak detail in complex scenes, blamed on the 64x64 base resolution.
- Hardware, compute, seeds and learning-rate schedule are not stated; datasets are not released; the production model differs and its hyperparameters are not given.
- Carries a higher risk profile than GLIDE, and the architecture's bias behaviour needs more study. Human-evaluation sweeps rely on a proxy trained on earlier human comparisons.

## See Also

- [[Diffusion and GAN Image Generation]] — related
- [[GLIDE Text-Guided Diffusion]] — prerequisite-for
- [[Classifier-Free Diffusion Guidance]] — prerequisite-for
- [[Imagen Frozen Language Model Text Conditioning]] — alternative-to
