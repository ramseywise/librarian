---
title: LENS Frozen LLM with Vision Modules
tags: [multimodal, concept]
summary: "LENS converts an image to text with frozen tag, attribute and captioning modules and has a frozen Flan-T5 answer from that text, with no multimodal training."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-berrios-2023-towards-language-models-that-can.md
---

# LENS Frozen LLM with Vision Modules

LENS asks whether a frozen off-the-shelf language model can handle object recognition and vision-language tasks given text from independent vision modules, with no alignment training. Three frozen modules describe the image: a CLIP-based tag module, a CLIP-based attribute module and a BLIP intensive captioner. Their text is joined with the task question and passed to a frozen Flan-T5 reasoning module, which writes a short answer. Evaluation is zero-shot (plus one and three shots for object recognition); few-shot gave no gain on vision-language tasks.

## Reported results (self-reported, zero-shot, baseline numbers copied from other papers)

- Object recognition over 9 datasets: with an H/14 encoder and Flan-T5XXL, LENS beats CLIP H/14 on average by a small margin; with L/14 it is on par (71.6 and 72.3 against 71.7). The gain is under one point, and a better vision backbone matters more than the LLM size.
- VQAv2 test-dev: 62.6 with Flan-T5XXL and zero trainable parameters (self-reported), compared with 65.0 for the BLIP-2 ViT-g FlanT5XXL model.
- OK-VQA: 43.3 (self-reported), which is under BLIP-2 ViT-g at 45.9 and Flamingo80B at 50.6.
- Rendered-SST2: 83.3 with Flan-T5XL against 67.1 for Kosmos-1. Hateful Memes test-seen ROC AUC: 62.5 against 46.4 for Flamingo80B.
- VQA 2.0 minival accuracy grows as more intensive captions are supplied and then saturates, going from 37.2 with the question only to 60.4 with 50 captions (self-reported). On Hateful Memes dev, OCR alone gives 57.2 and all modules together 59.4, with attributes helping most.
- The authors cite Flamingo pretraining as needing about 15 days, 2 billion image-text pairs and 43 million webpages.

## Limits

- Vision ability is capped by CLIP and BLIP; failures include wrong visual information, inconsistency across turns and forgetting. Evaluation still needs 8 A100 GPUs.
- The per-task module choice (for example captioning only for VQA) came from preliminary experiments, so it is tuned.
- No seeds or variance. On VQAv2 and OK-VQA, LENS does not beat BLIP-2.
- Internal inconsistencies: Table 7 and Table 3 disagree, and Sec 4.1 states that OK-VQA test and Rendered-SST2 were evaluated although Table 6 lists validation splits.

## See Also
- [[Contrastive and Masked Vision-Language Pretraining]] — related (the family comparison)
- [[BLIP Bootstrapped Captioning and Filtering]] — prerequisite-for (supplies the captioner)
- [[CLIP Contrastive Language-Image Pretraining]] — prerequisite-for (tag and attribute modules)
- [[InstructBLIP Instruction-Aware Query Transformer]] — alternative-to
