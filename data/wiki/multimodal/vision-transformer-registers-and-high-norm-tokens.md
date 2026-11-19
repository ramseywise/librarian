---
title: Vision Transformer Registers and High-Norm Tokens
tags: [multimodal, vision-backbones, concept]
summary: "Large ViTs trained long enough produce a small share of high-norm patch tokens that carry global information; appending learnable register tokens to the input, discarded at the output, removes them in DeiT-III, OpenCLIP and DINOv2."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-darcet-2023-vision-transformers-need-registers.md
---

# Vision Transformer Registers and High-Norm Tokens

Darcet et al. look for the cause of high-norm artifact tokens that appear in the feature and attention maps of big vision transformers, and ask if added input tokens can absorb them. Their hypothesis is that sufficiently trained large models spot patch tokens carrying redundant content and repurpose them as scratch space for global information; supplying dedicated register tokens should then eliminate the artifacts at no cost in quality.

## Diagnosis

An outlier (high-norm) token is an output token whose norm passes a hand-chosen threshold, 150 for DINOv2. In DINOv2 ViT-g/14 run over a small set of images, about 2% of patches qualify (self-reported). They emerge near layer 15 of 40 once about one third of training is done, and are absent from all but the three biggest models studied. Linear probes show that outlier patch tokens hold less local information than ordinary ones (position prediction) while holding global information: a probe on one random outlier token gives an ImageNet-1k linear score, to be compared with 86.0 for [CLS].

## Registers

A register is an extra learnable token placed after the patch embedding, as [CLS] is, that does not depend on the input image and is dropped from the output. The authors retrain three models with and without registers: a supervised DeiT-III ViT-B, a text-supervised OpenCLIP ViT-B/16 and a self-supervised DINOv2 ViT-L/14.

- Registers eliminate the outliers in all three models, and with registers the high-norm values sit wholly inside the register tokens.
- DeiT-III ViT-B (ImageNet-22k) is about unchanged on ImageNet, ADE20k and NYUd. OpenCLIP ViT-B/16 (Shutterstock corpus) improves on NYUd rmse with zero-shot ImageNet unchanged. DINOv2 ViT-L is evaluated by frozen-feature linear probing on ADE20k, ImageNet and NYUd with 4 registers.
- LOST object discovery on VOC2007 uses DINOv2 with registers (keys) and DeiT-III with registers (values); OpenCLIP gets slightly worse.
- Four registers cost under 2% extra FLOPs, sixteen up to 6%. Sweeping 0, 1, 2, 4, 8 and 16 registers on DINOv2 ViT-L/14, a single register already removes the artifacts, additional ones improve ImageNet, dense tasks peak at an intermediate count, and 4 were adopted.
- A linear probe on a register (DINOv2, one register) gives [CLS] 85.2 against 84.6 for an outlier patch with no registers (Aircraft).

## Limits

- Which parts of training produce the artifacts remains undetermined, in the authors' words. The mechanism study focuses on DINOv2, and the cutoff of 150 may differ for other models.
- With registers, OpenCLIP's LOST score is slightly lower; the suggested reason (outliers lying in the null space of the value projection) is deferred. Regularising registers and quantising their norms are likewise future work.
- Hyperparameters, seeds and compute are not reported; runs are single and training-set sizes are not given. OpenCLIP's absolute scores are lower because its corpus is licensed data.
- MAE shows no artifacts, but as a source of frozen features it is weak (ViT-L linear probe 75%).

## See Also
- [[Vision Transformer ViT Patch Tokens and Scaling]] — prerequisite-for
- [[DINOv2 Curated-Data Self-Supervised Features]] — prerequisite-for (the main model studied)
- [[DINO and iBOT Self-Distillation for Vision Transformers]] — related (DINO's attention maps are artifact-free)
- [[Masked Autoencoders Pixel Reconstruction]] — related
- [[CLIP Contrastive Language-Image Pretraining]] — related
