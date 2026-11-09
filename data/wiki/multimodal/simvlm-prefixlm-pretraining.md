---
title: SimVLM PrefixLM Pretraining
tags: [multimodal, concept]
summary: "SimVLM trains one encoder-decoder end to end with a single prefix language-modeling loss on image patches and noisy web pairs, replacing detector features and multi-loss pretraining."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-wang-2021-simvlm.md
---

# SimVLM PrefixLM Pretraining

SimVLM drops object detectors and auxiliary objectives. Image patches pass through a small three-block ResNet convolution stage and become a bidirectional prefix for an encoder-decoder transformer. The only loss is prefix language modeling: the prefix has bidirectional attention and the remaining text tokens are predicted autoregressively. Pretraining starts from scratch on ALIGN image-text pairs mixed in with C4 text, and the model is then fine-tuned per task or used zero-shot.

## Reported results (self-reported)

- SimVLM huge reaches 80.34 on VQA v2 test-std as a fine-tuned single model, above VinVL at 76.60; the base size already beats VinVL large on test-dev.
- Zero-shot cross-modality transfer: fine-tuned on text-only SNLI-VE data and tested with images, the huge model is compared with fully supervised UNITER at 78.59 and 78.28. A hypothesis-only check with the image masked is near chance.
- Generative VQA improves out-of-domain accuracy by 17.5 points over a discriminative head on the Karpathy-test out-of-domain split (huge; out-of-domain means the best answer is outside 3,129 candidates).
- Ablations use a small 8-layer, 512-dim model on VQA only, single runs: PrefixLM beats a plain LM and span corruption; encoder-decoder beats decoder-only; ALIGN beats CC-3M; the full ALIGN set beats 10% of it; removing the conv stage hurts; dropping the image-text data returns to the no-pretraining level (49.70); dropping text-only data costs about 2 points.
- ImageNet linear probe is below CLIP and ALIGN. Zero-shot open-ended VQA fell short until 50k extra steps of pretraining on WIT, with qualitative evidence.
- The COCO captioning score uses plain cross-entropy fine-tuning, while the VinVL comparison (140.9) uses CIDEr optimisation.

## Limits

- The paper gives no parameter counts, seeds, variance, wall-clock time or FLOPs.
- Ablations are small-model and VQA only; exact-match scoring undercounts valid synonymous answers.
- The extraction notes that the zero-shot COCO numbers in v1 were wrong and were corrected in v3.
- It is not stated whether the ALIGN pretraining data is released.

## See Also
- [[Contrastive and Masked Vision-Language Pretraining]] — related (the family comparison)
- [[ALIGN Noisy Alt-Text Dual Encoder]] — prerequisite-for (supplies the pretraining pairs)
- [[BLIP Bootstrapped Captioning and Filtering]] — alternative-to
- [[ViLT Patch Projection Vision-Language Transformer]] — alternative-to (also removes the detector)
- [[GIT Generative Image-to-Text Transformer]] — related
- [[Region-Based Single-Stream VLP (UNITER, VL-BERT, Unified VLP)]] — related
