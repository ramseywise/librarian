---
title: BEiT Masked Image Modeling with Visual Tokens
tags: [multimodal, concept]
summary: "BEiT pretrains a vision transformer by masking about 40% of patches blockwise and predicting each masked patch's discrete dVAE token, which the ablations show beats raw-pixel regression."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-bao-2021-beit.md
---

# BEiT Masked Image Modeling with Visual Tokens

BEiT carries BERT-style masked prediction over to images. A ViT sees an image whose 16x16 patches are about 40% masked (in blocks), and for each masked patch it predicts the discrete visual token assigned by a dVAE tokenizer, through a softmax over 8192 codes. The tokenizer is an external, already-trained one that the source calls the DALL-E tokenizer. After pretraining, the encoder is fine-tuned end to end on classification and on ADE20K segmentation. The stated hypothesis is that discrete targets keep the model from spending capacity on short-range, high-frequency detail.

## Reported results (self-reported)

- A ViT-B pretrained for 800 epochs on ImageNet-1K without labels, then fine-tuned at 224, reaches top-1 of 83.2 (self-reported). That is level with MoCo v3-B and higher than DINO-B (82.8) and DeiT-B trained from scratch (81.8). A ViT-L at 384 reaches 86.3 (self-reported).
- Ablations (300 epochs, ViT-B, single run, self-reported): replacing token prediction with pixel regression lowers ImageNet accuracy from 82.86 to 81.04, which is under DeiT-B from scratch. Dropping blockwise masking and the visual tokens at once gives ImageNet 80.50 and ADE20K 37.09. Recovering every token instead of only the masked ones lowers results.
- Training for 800 epochs rather than 300 lifts ADE20K to 45.58 and ImageNet to 83.19 (self-reported).
- Linear probe is weak for base size: 56.7 against 78.2 for DINO-B (average-pooled 9th-layer features). BEiT-L reaches 73.5 from 14th-layer features.
- ADE20K with SETR-PUP: 45.6 mIoU against 45.3 for supervised pretraining; 47.7 with intermediate fine-tuning.
- With an in-house 70M intermediate set, BEiT-L+ reaches 89.5 top-1 at 512 and 58.4 multi-scale mIoU on ADE20K (UperNet, 640).
- CIFAR-100: 90.1 against 48.5 for a ViT trained from scratch. Pretraining throughput is 4.2x that of a BEiT plus DINO multitask run.

## Limits

- 300-epoch ablations with single runs; no error bars.
- It relies on an external, already-trained DALL-E tokenizer, and only classification and segmentation were tested.
- Only classification and segmentation tested; scaling to larger models is suggested, not shown. The largest results use an unreleased in-house 70M labelled set.
- Internal inconsistency in the extraction: Table 4 reports BEiT 300-epoch ADE20K as 44.65 while Table 5's ViT row gives 44.86 under UperNet, and the Table 4 task layer is unstated.

## See Also
- [[Contrastive and Masked Vision-Language Pretraining]] — related (the family comparison)
- [[Masked Autoencoders Pixel Reconstruction]] — alternative-to (reconstructs pixels with a high masking ratio)
- [[Contrastive Self-Supervised Pretraining]] — related (contrastive baselines such as DINO)
- [[VQGAN Taming Transformers]] — related (a discrete image-token tokenizer)
