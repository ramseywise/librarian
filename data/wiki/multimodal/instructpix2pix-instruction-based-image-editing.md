---
title: "InstructPix2Pix Instruction-Based Image Editing"
tags: [multimodal, concept]
summary: "InstructPix2Pix trains a conditional diffusion model on synthetic before/after image pairs, built with GPT-3 and Stable Diffusion plus Prompt-to-Prompt, to edit a real image from a written instruction in one forward pass."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-brooks-2023-instructpix2pix.md
---

# InstructPix2Pix Instruction-Based Image Editing

The paper asks whether one forward pass of a diffusion model can edit a real photo following a written instruction, when trained purely on synthetic data. The hypothesis is that GPT-3 and Stable Diffusion together can generate paired edit examples, and that a conditional model trained on them transfers zero-shot to real photos and instructions written by people.

## Mechanism

1. **Paired data.** GPT-3 Davinci is fine-tuned on 700 manually written triplets (caption, instruction, edited caption) and then produces 454,445 triplets from LAION-Aesthetics captions. Stable Diffusion with Prompt-to-Prompt renders a before and an after image for each. CLIP-based filters (image-image, image-caption and directional similarity) select up to 4 examples per caption pair from 100 generated.
2. **Model.** Stable Diffusion v1.5 is fine-tuned, taking the input image as additional input channels and the instruction as the text condition.
3. **Two-condition guidance.** Classifier-free guidance is extended to the image condition and the text condition with separate scales sI and sT: the prediction starts from the unconditional output, adds sI times the effect of adding the image, then sT times the effect of adding the text. Typical good ranges are tuned per example for the paper's figures.

## Results (self-reported)

- Editing takes about 9 seconds per 512x512 image on one A100 (100 denoising steps, Euler ancestral sampler).
- Training took 10,000 steps over 25.5 hours on 8 A100 40GB GPUs (256x256, batch 1024, learning rate 1e-4).
- Versus SDEdit, the model reaches higher CLIP image consistency at equal directional similarity (curves in Fig 8, text guidance 7.5, sI between 1.0 and 2.2); neither numbers nor the size of the evaluation set are given.
- Ablations (Fig 10): smaller training sets (10% and 1%) reduce the ability to make larger edits; removing the CLIP filter lowers consistency with the input.

## Limits

- The only quantitative evaluation is a pair of CLIP-based trade-off plots against SDEdit; no numbers, human study or test-set size.
- Bounded by Stable Diffusion's image quality, GPT-3, the 700 manual examples and Prompt-to-Prompt.
- Weak at counting and spatial reasoning (moving left, swapping positions); cannot change viewpoint; may over-edit or fail to isolate one object. Carries over biases from data and models.
- Guidance weights were tuned per example for the figures shown. Open questions the authors raise: instructions about space, other kinds of conditioning, how to evaluate instruction-based editing, and learning from human feedback.

## See Also

- [[Diffusion and GAN Image Generation]] — related
- [[Prompt-to-Prompt Cross-Attention Editing]] — prerequisite-for
- [[Classifier-Free Diffusion Guidance]] — prerequisite-for
- [[ControlNet Spatial Conditioning]] — related (both add conditioning to a pretrained Stable Diffusion model)
