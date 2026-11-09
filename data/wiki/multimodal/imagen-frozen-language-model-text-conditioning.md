---
title: "Imagen Frozen Language Model Text Conditioning"
tags: [multimodal, concept]
summary: "Imagen conditions a cascade of diffusion models on a frozen text-only T5 encoder, adds dynamic thresholding for large guidance weights, and introduces the DrawBench prompt set."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-saharia-2022-photorealistic-text-image-diffusion-models.md
---

# Imagen Frozen Language Model Text Conditioning

The paper asks whether general-purpose language models, frozen and pretrained on text alone, can serve as the text encoder for a cascade of text-to-image diffusion models, and whether scaling that encoder helps more than scaling the image model.

## Mechanism

A frozen T5-XXL encoder conditions a 64x64 text-to-image diffusion model; two text-conditional super-resolution diffusion models then raise the output to 256 and 1024. Classifier-free guidance is used throughout. Two additions:

- **Dynamic thresholding**: at each sampling step, take a percentile of the predicted clean image's absolute pixel values as s; if s exceeds 1, clip to [-s, s] then divide by s. **Static thresholding** clips every element to [-1, 1] instead.
- **Noise conditioning augmentation**: the low-resolution input is degraded with noise whose level the model also receives; the level is random during training and swept at inference.

The paper also introduces an efficient U-Net variant. **DrawBench** is a text-to-image benchmark of 200 prompts in 11 categories.

## Results (self-reported)

- Zero-shot COCO FID-30K of 7.27 (MS-COCO 2014 validation, 256x256, 30K prompts, guidance 1.35 on the 64x64 model and 8.0 on the super-resolution models). Quoted comparisons: DALL-E 2 10.39, GLIDE 12.24, and Make-A-Scene, which trained on COCO, 7.55.
- Photorealism: raters selected Imagen rather than the real COCO image in 39.5% of 200 pairs, or 43.9% when prompts mention no people. Caption alignment: 91.4 for Imagen, 91.9 for the original images.
- Ablations on 64x64 models: enlarging the frozen text encoder helps quality more than enlarging the U-Net; T5-XXL and CLIP encoders score alike on COCO, yet raters prefer T5-XXL for DrawBench alignment in all 11 categories; cross-attention over the embedding sequence beats pooling.
- Dynamic thresholding yields better CLIP scores than static thresholding and comparable or better FID, particularly at high guidance weights (guidance sweep 1-10, FID-10K).
- The efficient U-Net samples 2-3x faster and converges faster (64 to 256 super-resolution). Noise conditioning augmentation is critical; the best samples used aug_level between 0.1 and 0.3.
- DrawBench (25 raters per category): raters prefer Imagen over DALL-E 2 for alignment in 7 of 11 categories and for fidelity in all 11; against GLIDE the counts are 8 and 10 of 11.

## Limits

- Code, weights and a demo are withheld because of bias, weaker people generation and a content audit of the training data. Bias checks (lighter skin tones, Western gender stereotypes for professions) were small-scale internal assessments.
- FID only loosely follows perceptual quality, and CLIP counts poorly. The ablations use smaller 300M to 2B base models scored by FID-10K rather than the final setup.
- DrawBench is only 200 prompts with no rater filtering; no total compute, wall-clock or sampling steps stated.
- Internal inconsistency in the extraction: the text says 39.2% and 43.6% where the table gives 39.5% and 43.9%.

## See Also

- [[Diffusion and GAN Image Generation]] — related
- [[Classifier-Free Diffusion Guidance]] — prerequisite-for
- [[Cascaded Diffusion Models]] — prerequisite-for
- [[GLIDE Text-Guided Diffusion]] — alternative-to
- [[unCLIP Hierarchical Text-Conditional Generation]] — alternative-to
- [[Make-A-Scene Scene-Based Text-to-Image Generation]] — alternative-to
- [[Prompt-to-Prompt Cross-Attention Editing]] — extends
- [[Textual Inversion and DreamBooth Personalization]] — extends
