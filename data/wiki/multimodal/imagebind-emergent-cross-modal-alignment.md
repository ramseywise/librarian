---
title: ImageBind Emergent Cross-Modal Alignment
tags: [multimodal, concept]
summary: "ImageBind aligns audio, depth, thermal and IMU encoders to frozen OpenCLIP image embeddings using only image-paired data, and text-to-modality alignment emerges without any modality-text pairs."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-girdhar-2023-imagebind-one-embedding-space-bind.md
---

# ImageBind Emergent Cross-Modal Alignment

ImageBind builds one embedding space over six modalities (image or video, text, audio, depth, thermal, IMU). Audio, depth, thermal and IMU each get a transformer encoder trained with a symmetric InfoNCE loss against the image and text embeddings of a frozen OpenCLIP ViT-H, one (image, modality) pair type at a time. Because every modality is tied to images, modalities that were never paired (for example audio and text) end up aligned, which the paper calls emergent zero-shot classification.

## Reported results (self-reported; emergent zero-shot unless stated)

- ESC-50 audio classification (self-reported): top-1 of 66.9 without any audio-text training, against 68.6 for AudioCLIP, which uses text supervision (5-fold average, CLIP templates).
- Text-to-audio retrieval (self-reported): Clotho R@1 6.0 against 3.0 for AVFIC; on AudioCaps, R@1 is 9.3 and R@10 is 42.3, against 8.7 and 37.7.
- MSR-VTT 1k-A text-to-video R@1 is 36.1 with the frozen OpenCLIP encoders; audio alone gives 6.8 and audio plus video 36.8.
- Depth scene classification: NYU-D 54.0 and SUN-D 35.1, against 41.9 and 25.4 for OpenCLIP ViT-H on grayscale depth. IMU Ego4D scenarios 25.0 against 0.9 random; LLVIP thermal person classification 63.4 against 50.0.
- Ablations (ViT-B encoders, ESC fold 1, self-reported): moving the image encoder from ViT-B to ViT-H gains roughly 7% for depth and 4% for audio; a linear head beats an MLP head (56.7 against 51.0); heavy image augmentation takes ESC down from 56.7 to 22.6; the best batch size differs by modality (2k for ESC, 512 for NYU-D); batches are far below the 32K used in earlier work.
- Despite lower ImageNet accuracy, a frozen DINO image encoder yields better emergent audio alignment than DeiT (ESC 44.7 against 25.0) (self-reported).
- Few-shot audio: about 40% higher top-1 than self-supervised AudioMAE at four shots or fewer.

## Limits

- The authors call it a research prototype; embeddings lag specialist models and cover only concepts in the training data (thermal is outdoor street scenes, depth is indoor).
- Detection, audio-to-image generation and embedding arithmetic are qualitative only. There is no fair baseline for emergent zero-shot, since AudioCLIP is not strictly zero-shot.
- No seeds, variance or compute reported.
- Internal inconsistency: the text says 32 epochs while Table 9 lists 64 (8 for Ego4D).

## See Also
- [[Contrastive and Masked Vision-Language Pretraining]] — related (the family comparison)
- [[CLIP Contrastive Language-Image Pretraining]] — prerequisite-for (zero-shot protocol and frozen encoders)
