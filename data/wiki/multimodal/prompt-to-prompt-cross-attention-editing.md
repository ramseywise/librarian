---
title: "Prompt-to-Prompt Cross-Attention Editing"
tags: [multimodal, concept]
summary: "Prompt-to-Prompt edits a generated image by changing only the text prompt while copying or rescaling the diffusion model's cross-attention maps, so layout is preserved without masks or training."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-hertz-2022-prompt-prompt-image-editing-cross.md
---

# Prompt-to-Prompt Cross-Attention Editing

The paper asks whether an image from a text-conditioned diffusion model can be edited purely by altering the prompt, while keeping the layout and avoiding a user-drawn mask. The hypothesis is that cross-attention maps fix the spatial layout, so feeding the original run's maps into a run with the edited prompt keeps the structure.

## Mechanism

Two diffusion runs, one for the source prompt and one for the edited prompt, use the same random seed. The edited run's cross-attention maps are overridden by the source maps (all steps, a prefix of steps, or only for tokens the prompts share), or one token's map is rescaled. Three edit types follow: swap a word, add a phrase, re-weight a word's attention. It was built on the 64x64 text-to-image diffusion model of Imagen, with super-resolution used unchanged. Real images are handled by DDIM inversion plus attention-derived masks.

## Findings

All evidence is qualitative figures on that backbone.

- With only the seed fixed, changing the prompt ("lemon cake" to other cakes) yields an entirely different image; injecting the source cross-attention maps keeps the layout.
- Injecting maps at every diffusion step can over-constrain geometry (a "cat riding a bicycle" where the bicycle becomes a car, airplane, motorcycle or train); restricting injection to the early steps balances fidelity against following the new prompt.
- Attention maps for a furry bear watching a bird show that image structure is fixed early in sampling.
- The authors claim that nothing is trained, fine-tuned, added as data or optimized, and that cost rises by only one diffusion step because both runs share a batch (both claims).
- Inverting real images with DDIM often works but fails on others; a lower classifier-free guidance scale reconstructs better yet restricts edits.

## Limits

- No benchmark, metric, user study or baseline comparison is reported.
- Real-image inversion visibly distorts some images and needs a suitable user-supplied prompt.
- Cross-attention maps are low resolution, bounding precise local edits; the method cannot spatially move existing objects.
- Neither tau, the guidance scale, the number of examples nor the seeds are stated.

## See Also

- [[Diffusion and GAN Image Generation]] — related
- [[Imagen Frozen Language Model Text Conditioning]] — prerequisite-for
- [[Classifier-Free Diffusion Guidance]] — prerequisite-for
- [[InstructPix2Pix Instruction-Based Image Editing]] — extends
