---
title: Masked Autoencoders Pixel Reconstruction
tags: [multimodal, concept]
summary: "MAE masks 75% of image patches, encodes only the visible ones and reconstructs masked pixels with a small decoder, which makes pretraining of large ViTs cheap and strong for fine-tuning."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-he-2022-masked-autoencoders-scalable-vision-learners.md
---

# Masked Autoencoders Pixel Reconstruction

MAE starts from the observation that images are spatially redundant, so a very high masking ratio is needed to make the task non-trivial. The image is cut into 16x16 patches (14x14 for ViT-H) and 75% of them are removed at random. The encoder, a plain ViT, sees only the visible patches. A lightweight decoder gets the encoded patches plus shared learned mask tokens and reconstructs the masked pixels under an MSE loss. Pretraining uses ImageNet-1K, and evaluation covers fine-tuning and linear probing as well as partial fine-tuning and transfer.

## Reported results (self-reported)

- ViT-H/14 pretrained 1600 epochs on normalized pixels and fine-tuned at 448 gets 87.8% on ImageNet-1K, the top result among methods using only ImageNet-1K (previous best 87.1) (self-reported).
- Masking ratio (ViT-L/16, 800 epochs): 75% is best for fine-tuning and for linear probing, which rises from 54.6 at 10% masking to 73.5 at 75%.
- Leaving mask tokens out of the encoder speeds up wall-clock training of ViT-L by 2.8x, with 3.3x fewer FLOPs, on 128 TPU-v3 cores, whereas keeping them costs 14% linear-probe accuracy (self-reported).
- MAE-pretrained ViT-L fine-tunes to 84.9, against 82.5 for supervised training from scratch with the authors' recipe and 76.5 for the original recipe.
- Linear probing remains behind contrastive training: 75.8 for ViT-L at 1600 epochs against 77.6 for MoCo v3. Fine-tuning a single block lifts ViT-L from 73.5 to 81.0.
- Predicting dVAE tokens is no better than predicting normalized pixels, in statistical terms. MAE beats supervised pretraining on COCO box AP (Mask R-CNN, ViT-L) (self-reported).
- ImageNet-A: 68.2 for MAE ViT-H against 33.1 for supervised ViT-H. Training ViT-L for 1600 epochs takes 31 hours against 36 hours for MoCo v3 at 300 epochs.

## Limits

- Pixels are not semantic entities; the authors hypothesise that semantics emerge.
- No seeds, error bars or significance tests; COCO configurations are not given in the text.
- Vanilla ViT only. No saturation was seen at 1600 epochs, so the numbers may understate.
- Authors note it reflects dataset biases and may generate content that does not exist.

## See Also
- [[Contrastive and Masked Vision-Language Pretraining]] — related (the family comparison)
- [[BEiT Masked Image Modeling with Visual Tokens]] — alternative-to (token targets instead of pixels)
- [[EVA Masked CLIP-Feature Regression]] — extends (same masking idea with CLIP-feature targets)
- [[Contrastive Self-Supervised Pretraining]] — related
- [[MaskGIT Masked Generative Image Transformer]] — related (masked prediction over image tokens)
- [[SAM 2 Promptable Video Segmentation]] — related (uses an MAE-pretrained Hiera encoder)
