---
title: LXMERT
tags: [multimodal, concept]
summary: "LXMERT pretrains a three-encoder cross-modality Transformer on 9.18M image-sentence pairs with five tasks and, among the models the paper compares against, sets state of the art on VQA, GQA and NLVR2 (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-tan-2019-lxmert.md
---

# LXMERT

Tan and Bansal (EMNLP-IJCNLP 2019) test whether a Transformer pretrained specifically for cross-modality gives a backbone reusable across vision-and-language reasoning tasks, as opposed to bolting vision heads onto BERT.

## Architecture and pretraining

- Three parts: a language encoder of 9 layers; an object-relationship encoder of 5 layers over 36 Faster R-CNN objects, whose RoI features are fused with position; and 5 cross-modality layers combining cross-attention, self-attention and feed-forward blocks.
- Pretraining uses five tasks with equal weight. They are masked cross-modality language modelling (where the image can help predict masked words), RoI-feature regression, classification of detected labels, cross-modality matching, and image question answering.
- The data is 9.18M image-sentence pairs over 180K images, drawn from COCO captions, Visual Genome captions, VQA, GQA and VG-QA. Training took about 670K steps at batch 256, 20 epochs over 10 days on 4 Titan Xp GPUs. Fine-tuning targets VQA, GQA and NLVR2.

## Results (self-reported)

- VQA v2.0 and GQA test-standard (single model, fine-tuned; GQA with no functional programs or scene graphs): higher overall accuracy than the previous best at submission (BAN+Counter on VQA, BAN on GQA), with a 4.6% gain on GQA open questions.
- NLVR2 unreleased test: 76.2% accuracy, 22% absolute over the previous best, with NLVR2 data absent from pretraining; consistency 42.1%. Public test: 74.5% accuracy and 39.7% consistency.
- Ablations on NLVR2 dev: pretraining from scratch 74.9 against 50.9 with no pretraining; initialising from BERT is worse (70.1); the image-QA task helps (74.9 against 72.4); with no vision pretraining tasks accuracy is 50.9. On VQA dev, augmenting data at fine-tuning gives 69.1 against 69.9 for pretraining on the QA data.

## Limits

- No variance, seeds or significance tests; ablations are single runs on dev sets.
- State-of-the-art claims are as of the May 2019 submission; the paper notes a stronger model (MCAN, 72.8% on VQA). Concurrent work (ViLBERT, VisualBERT) is claimed to trail by 1.5% on VQA and 9% on NLVR2.
- The model relies on a frozen detector yielding 36 objects and noisy labels. The paper does not give the parameter count, number of heads or warmup.

## See Also
- [[Visual Question Answering Benchmarks]] — related
- [[GQA Benchmark]] — prerequisite-for
- [[VQA v2 Balanced Dataset]] — prerequisite-for
- [[ViLBERT Co-Attention Two-Stream Pretraining]] — alternative-to (concurrent)
- [[Faster R-CNN]] — prerequisite-for
- [[Visual Genome]] — prerequisite-for
