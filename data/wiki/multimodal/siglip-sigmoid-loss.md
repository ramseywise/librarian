---
title: SigLIP Sigmoid Loss for Language-Image Pretraining
tags: [multimodal, concept]
summary: "SigLIP replaces the batch-softmax contrastive loss with an independent sigmoid loss on every image-text pair, which removes global normalisation, helps at small batch sizes and shows batch-size gains saturating near 32k."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-zhai-2023-sigmoid-loss-language-image-pre.md
  - data/raw/papers/2026-11-08-awais-2023-foundational-models-defining-new-era.md
---

# SigLIP Sigmoid Loss for Language-Image Pretraining

The method swaps the softmax cross-entropy used by CLIP-style training for a binary sigmoid loss applied independently to every image-text pair in a batch: the matching pair on the diagonal is a positive and every other pair is a negative. The temperature is learnable, a learnable bias starts at -10, and the loss is computed in device-local chunks so no all-gather of the full pairwise matrix is needed. SigLiT applies it with a locked image tower; SigLIP and mSigLIP train the image tower too, on WebLI.

## Results

All numbers are self-reported and carry the setup stated.

- SigLiT with a frozen ViT-g/14 reaches 84.5% zero-shot ImageNet on four TPUv4 chips in two days (batch 20k, 107k steps). With a public B/8 image checkpoint locked it reaches 79.7% in under a day on four chips.
- The sigmoid loss is clearly ahead of softmax below roughly 16k batch, and at larger batches the gap closes (SigLiT, 18B examples seen: 83.6 versus 83.1 at batch 8k). A SigLiT at 1M batch scores 84.7, against 84.6 at 32k (self-reported).
- A SigLIP B/16 trained from scratch gets 73.4% zero-shot ImageNet after 5 days on 32 TPUv4 chips, and 72.1% after 2 days (self-reported).
- SigLIP SoViT-400M with 729 patches scores 83.2% zero-shot ImageNet, versus 82.0 for EVA-CLIP E (5B) at 256 patches (self-reported); the comparison is with publicly released models trained on different data and recipes.
- mSigLIP Base reaches an average 34.9% XM3600 text-to-image recall@1 at batch 32k over 36 languages. Beyond 32k batch, multilingual retrieval declines (34.9 down to 32.7 at 240k), whereas ImageNet barely moves (73.2 and 73.1) (self-reported).
- Bias initialised at -10 with temperature parameter log 10 gives 63.0% against 62.0% with no bias; a bias of 0 with log 1 gives 53.7% (Base, batch 8k, 900M examples).
- Lowering Adam beta2, from 0.999 to 0.95, steadies training at large batch. Keeping just the hardest negatives nearly retains quality, whereas random or easy masking hurts.
- At 32k batch and 3B examples over five runs, sigmoid scores 70.1 +/- 0.2 against 69.9 +/- 0.1 for softmax.

The survey by Awais et al. reports, from other work, that masking 50-75% of image input in CLIP training (FLIP) cut the time to reach CLIP accuracy by more than 3x, and that CLIPA-v2 reaches 69.3% zero-shot ImageNet in 4 days on 8 A100 GPUs.

## Limits

- WebLI is private, so others cannot reproduce the headline numbers.
- The authors call efficient hard-negative mining promising but do not provide it. Very large batches help only with long schedules.
- The noise-robustness result is qualitative, read from a figure.
- Comparisons with public models mix data and recipes; per the extraction, EVA-CLIP and CLIPA-v2 are concurrent work.

## See Also
- [[Contrastive and Masked Vision-Language Pretraining]] — related (the family comparison)
- [[CLIP Contrastive Language-Image Pretraining]] — prerequisite-for (the softmax baseline this replaces)
- [[EVA Masked CLIP-Feature Regression]] — related (compared as a concurrent baseline)
- [[DINOv3 Gram Anchoring Self-Supervised Backbone]] — related
- [[InternVL Scaled Vision Encoder with QLLaMA]] — related
