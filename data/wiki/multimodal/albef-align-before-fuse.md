---
title: ALBEF Align Before Fuse
tags: [multimodal, concept]
summary: "ALBEF aligns image and text features with a contrastive loss before a cross-attention fusion encoder, and uses momentum-distilled pseudo-targets to cope with noisy web captions, without a detector."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-li-2021-align-before-fuse.md
---

# ALBEF Align Before Fuse

ALBEF is a detector-free vision-language pretraining model. The idea is that unimodal image and text features should be aligned with a contrastive objective before they enter the cross-modal encoder, so fusion has an easier job. A second idea is momentum distillation: pseudo-targets from a momentum model soften supervision from noisy web text.

## Mechanism

- A ViT-B/16 image encoder, a 6-layer BERT text encoder and a 6-layer cross-attention multimodal encoder.
- Pretraining losses: image-text contrastive (ITC) on the unimodal features, MLM and ITM. ITM draws its hard negatives from the contrastive similarity scores.
- Momentum distillation uses a weight of alpha 0.4 and applies to the pretraining objectives; the model is then fine-tuned on five downstream tasks.
- The authors also analyse the objectives as mutual information maximisation.

## Reported results (self-reported)

The extraction gives the direction of most ablation effects without the figures.

- Table 1 setup (4M pretraining images): adding ITC to MLM plus ITM raises VQA test-dev, Flickr30K text-retrieval mean recall and NLVR2 test-P.
- The abstract claims +2.37 absolute VQA test-std and +3.84 NLVR2 test-P over VILLA with 14M pretraining images; at 4M images the model already beats VILLA on VQA test-std.
- Zero-shot Flickr30K retrieval is compared to CLIP (88.0 text-retrieval R@1) and ALIGN (88.6); the model was fine-tuned on COCO first. Fine-tuned retrieval is compared with ALIGN at 1.2B pairs.
- Reranking is insensitive to the candidate count k (Flickr text-retrieval mean recall 98.60 at k=16, 98.57 at k=128 and 256); dropping hard negatives at k=128 lowers it.
- Weakly supervised RefCOCO+ grounding works with Grad-CAM on the ITM cross-attention layer, with no box annotations.
- The extraction notes that the speed advantage over VILLA is stated in text with no timing table.

## Limits

- No seeds or variance reported.
- RefCOCO+ validation and test images appear in the pretraining data and were not removed.
- SNLI-VE test data is reported to be noisy.
- The ablation runs on 4M images only; the 14M row changes the data as well.
- The extraction leaves several numeric fields blank, so only the stated comparisons are reproduced here.

## See Also
- [[Contrastive and Masked Vision-Language Pretraining]] — related (the family comparison)
- [[BLIP Bootstrapped Captioning and Filtering]] — extends (same 14M set, adds generation and CapFilt)
- [[CLIP Contrastive Language-Image Pretraining]] — related (retrieval baseline)
- [[ViLT Patch Projection Vision-Language Transformer]] — alternative-to (detector-free competitor)
