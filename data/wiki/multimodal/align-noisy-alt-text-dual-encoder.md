---
title: ALIGN Noisy Alt-Text Dual Encoder
tags: [multimodal, concept]
summary: "ALIGN trains an image encoder and a text encoder with a contrastive loss on 1.8B alt-text pairs filtered only lightly, testing whether corpus scale can make up for noise; it reports retrieval and zero-shot results on par with or above CLIP."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-jia-2021-scaling-up-visual-vision-language.md
  - data/raw/papers/2026-11-07-akkus-2023-multimodal-deep-learning.md
---

# ALIGN Noisy Alt-Text Dual Encoder

ALIGN pairs an EfficientNet-L2 image encoder with a BERT-Large text encoder, each topped by a linear layer, and trains both from scratch with a symmetric in-batch normalised-softmax contrastive loss and a learned temperature. The corpus is 1.8B English alt-text pairs that pass only simple frequency and size filters. The bet is that sheer scale compensates for noise, so heavy curation is unnecessary.

## Results

Numbers are self-reported by the paper.

- Zero-shot ImageNet is on par with CLIP; class names go through the text encoder using prompt ensembling in the CLIP style.
- Against CLIP, ALIGN's zero-shot Flickr30K retrieval from text to image is 7 points better at R@1, and from image to text it is 88.6 versus 88.0 (self-reported). On the MSCOCO 5K split with no fine-tuning, the image-to-text figure is 58.6 versus 58.4 and the text-to-image figure is 45.6 versus 37.8 (self-reported).
- Fine-tuned MSCOCO retrieval reaches 77.0 image-to-text and 59.9 text-to-image R@1.
- Frozen-feature ImageNet top-1 is 85.5 and fine-tuned 88.64; VTAB mean over 19 tasks is 79.99 against 78.72 for BiT-L (1000 training images per task).
- Noise versus cleaning, with a B7 image encoder and a BERT-base text encoder trained from scratch, scored by image-to-text recall at rank 1 on MSCOCO with no fine-tuning: 3M noisy ALIGN pairs give 8.1, cleaned CC-3M gives 18.9, 12M noisy pairs reach 23.8, and the full ALIGN data reaches 55.4 (self-reported).
- Using fewer in-batch negatives lowers quality (25% of negatives: 48.7 against 51.7), and a fixed temperature of 1/32 is much worse than the learned value, which settled near 1/64 (B5 with BERT-base).
- Adding an image embedding and a text embedding gives image-plus-text queries for search (qualitative, 160M-image index).

## Limits

- The dataset is not released, and the paper gives no compute, wall-clock time or parameter counts; most results come from single runs.
- The authors note weaker same-modality retrieval (text-to-text, image-to-image) and suspect the cross-modal-only objective; this is not tested.
- Ablations use smaller B5 or B7 encoders with BERT-base for fewer steps, and the noisy-versus-clean comparison covers COCO zero-shot alone.
- Fine-tuned ImageNet accuracy trails Meta Pseudo Labels (90.2).
- The authors give no fairness analysis of harmful alt-text and call for more before production use.

## See Also
- [[Contrastive and Masked Vision-Language Pretraining]] — related (the family comparison)
- [[CLIP Contrastive Language-Image Pretraining]] — alternative-to (curated 400M pairs instead of noisy 1.8B)
- [[Florence UniCL Vision Foundation Model]] — extends (cites ALIGN's data filtering as a baseline)
- [[SimVLM PrefixLM Pretraining]] — related (trained on the ALIGN pairs)
