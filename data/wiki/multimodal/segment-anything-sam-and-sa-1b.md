---
title: Segment Anything SAM and SA-1B
tags: [multimodal, concept]
summary: "Segment Anything defines promptable segmentation, an MAE-pretrained ViT-H model with a light mask decoder, and a three-stage data engine that produced the 1.1B-mask SA-1B dataset."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-kirillov-2023-segment-anything.md
---

# Segment Anything SAM and SA-1B

The paper proposes a promptable segmentation task (return a valid mask for any prompt), a model, and a data engine, aiming at a foundation model for segmentation that transfers zero-shot. SAM has a ViT-H image encoder pretrained with MAE, a prompt encoder for points, boxes, masks and CLIP text, and a two-layer transformer mask decoder that outputs three ambiguity-aware masks with IoU scores. SA-1B holds 1.1B masks on 11M images, 99.1% fully automatic. The three data-engine stages are assisted-manual, semi-automatic and fully automatic. Annotation time per mask in stage one fell from 34 s to 14 s as the model improved (self-reported).

## Reported results (self-reported, zero-shot)

- Point prompts, 23 datasets, one centre foreground point, most confident mask: mIoU is higher than RITM on 16 of 23 datasets, and with an oracle pick among the three masks SAM is better on all 23 (self-reported). Annotators rate single-point masks 7 to 9 on average.
- BSDS500 edges (self-reported): ODS .768, OIS .786, AP .794 and R50 .928, with HED at ODS .788; the high R50 comes at a cost in precision since SAM predicts more edges than annotated.
- LVIS v1 proposals: AR@1000 of 59.3 against 63.0 for ViTDet-H; the ambiguity-aware model beats the single-output one (59.3 against 54.9).
- Instance segmentation with ViTDet-H boxes as prompts: COCO mask AP 46.5 against 51.0; LVIS 44.7 against 46.6. Human raters nonetheless score SAM masks higher (8.1 against 7.9, LVIS).
- Ablations (self-reported): automatic masks alone trail the three-stage mix by about 0.5 mIoU; 1M images (about 10%) matches the full set; a bigger encoder helps going from ViT-B to ViT-H, with the step from ViT-L to ViT-H marginal.
- 94% of automatic masks exceed 90% IoU with professionally corrected versions (500 images, about 50k masks).
- With the image embedding precomputed, the prompt encoder and the decoder take about 50 ms on a CPU, in a browser. Training took 256 A100 GPUs for 68 hours.
- Geography: 54.0% of SA-1B images come from high-income countries, against 89.1% for COCO and 87.5% for Open Images. Clothing segmentation shows a gender gap at one point (76.3 against 81.0) that closes at three points.

## Limits

- Can miss fine structure and produce small disconnected components; its boundaries are less crisp than those of methods that zoom in.
- Not tuned for the high-IoU interactive regime; the heavy encoder is not real-time. Text-to-mask is exploratory.
- SA-1B under-represents Africa, Latin America and low-income countries.
- Single runs; no training seeds; data-engine retraining compute is not stated.

## See Also
- [[Contrastive and Masked Vision-Language Pretraining]] — related (the family comparison)
- [[Masked Autoencoders Pixel Reconstruction]] — prerequisite-for (supplies the encoder initialisation)
- [[CLIP Contrastive Language-Image Pretraining]] — prerequisite-for (text prompt encoder)
- [[SAM 2 Promptable Video Segmentation]] — extends
- [[SAM 3 Promptable Concept Segmentation]] — extends
