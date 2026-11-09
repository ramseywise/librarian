---
title: ViLT Patch Projection Vision-Language Transformer
tags: [multimodal, concept]
summary: "ViLT embeds images with a linear patch projection straight into a single-stream transformer, with no CNN or region detector, cutting visual-embedding cost sharply at some accuracy cost on VQA."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-kim-2021-vilt.md
---

# ViLT Patch Projection Vision-Language Transformer

ViLT asks whether the transformer that fuses modalities can also process visual input directly. The model is a single-stream transformer started from ViT-B/32 weights: the image is cut into 32x32 patches that are linearly projected, then joined with BERT-tokenised text embeddings and modal-type embeddings. Pretraining uses ITM (plus a word-patch alignment term) together with whole-word MLM, over four caption datasets, then fine-tuning on VQAv2, NLVR2 and retrieval.

## Reported results (self-reported)

- Speed: visual embedding plus transformer takes about 15 ms against about 900 ms for region-feature models such as UNITER-Base (Xeon E5-2650 plus P40, 10K-run average; 384x640 against 800x1333 input). The linear patch embedding costs about 0.4 ms and 2.4M parameters, against 25M for a ResNet-50.
- ViLT-B/32 has 87.4M parameters and 55.9 GFLOPs against 154.7M and 949.9 for UNITER-Base.
- Accuracy: 70.33 on VQAv2 test-dev after 100K pretraining steps (mean of 3 seeds), below UNITER-Base at 72.70 and VinVL-Base at 75.95; 71.26 with RandAugment and 200K steps. NLVR2 test-P is 74.57 against 75.80, and 76.13 with RandAugment plus 200K steps.
- Retrieval: Flickr30k text retrieval R@1 of 81.4 against 75.7 for Pixel-BERT-R50; COCO 5K image retrieval R@1 of 41.3 against 50.3 for UNITER-Base. Zero-shot Flickr30k text retrieval reaches 73.2 at 200K steps.
- Ablations at 100K steps (self-reported): whole word masking takes NLVR2 test-P up from 74.15 to 74.57; RandAugment at fine-tuning lifts it to 75.57; a masked patch prediction objective lowers it to 73.54.
- Pooled CLIP-style dot-product embeddings with a fine-tuned head fail near chance on NLVR2 dev.

## Limits

- The authors call ViLT-B/32 a proof of concept and suspect detector objects ease VQA.
- Only ViT-B/32 weights (ImageNet-21K) were used; larger models and data are left for later.
- Without region supervision there is no good visual masking objective. Starting from BERT plus the ViT patch projection did not work, and no numbers are given.
- Pretraining stopped at 200K steps because text retrieval declined afterward; speeds are for 2021 hardware.

## See Also
- [[Contrastive and Masked Vision-Language Pretraining]] — related (the family comparison)
- [[ViLBERT Co-Attention Two-Stream Pretraining]] — alternative-to (region features, two streams)
- [[ALBEF Align Before Fuse]] — alternative-to
- [[SimVLM PrefixLM Pretraining]] — alternative-to
