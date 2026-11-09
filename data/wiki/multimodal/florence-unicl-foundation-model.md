---
title: Florence UniCL Vision Foundation Model
tags: [multimodal, concept]
summary: "Florence pretrains a two-tower CoSwin-H and text transformer on 900M curated image-text pairs with the UniCL contrastive loss, then adds small adapters for detection, vision-language tasks and video."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-yuan-2021-florence.md
  - data/raw/papers/2026-11-07-akkus-2023-multimodal-deep-learning.md
---

# Florence UniCL Vision Foundation Model

Florence is presented as a foundation model for computer vision: a single image-text pretrained model plus light adapters that reach across modality as well as time (image to video) and space (scene to object). The pretraining set, FLD-900M, holds 900M image-text pairs curated from about 3B web images. A 12-layer text transformer and a CoSwin-H image encoder (893M parameters) are trained in two stages with UniCL, a bidirectional supervised contrastive loss on image-label-description data. The adapters are Dynamic Head for object detection, METER for visual question answering and Video CoSwin for video.

## Results

All numbers are self-reported by the paper.

- Zero-shot, it beats the prior best on 9 of 12 classification datasets (ImageNet plus 11 others), using CLIP-style templates and ensembling at 384 px with near-duplicates removed. The table it cites gives CLIP ViT-L/14 at 336 px 76.2 and FILIP 78.3 for zero-shot ImageNet-1K top-1.
- Fine-tuned ImageNet-1K uses CoSwin-H at 512 px on the 900M images for 10 epochs; the paper says it sits slightly below CoAtNet-7, which is larger in model and data.
- The VQAv2 score of 80.16 comes from the METER-based vision-language adapter with extra pretraining on 14M images, not the two-tower model alone; the SimVLM comparison (80.03) is within 0.13.
- Zero-shot detection does better than 5-shot fine-tuning of DyHead-Swin-L on 7 of 11 Roboflow tasks (self-reported).
- The survey by Akkus et al. reports, from the paper, a 7.3 point zero-shot ImageNet margin over CLIP and ALIGN.

## Limits

- By the authors' own statement the model is smaller than several other billion-scale models. FLD-900M, the weights and the code are not released with the paper.
- On novel domains such as blood-cell and chess-piece images, zero-shot detection still trails supervised learning; the linear probe is weaker on CIFAR at 32x32 inputs.
- Internal inconsistencies the extraction notes: the ImageNet-1K fine-tune comparison table lists CoAtNet-7 at 90.88, while a later sentence gives it as 90.05; and the VQA result of 80.16 comes from an adapter with extra pretraining on 14M images, so its margin over SimVLM (80.03) is only 0.13 and not a measure of the pretrained model alone.
- Many hyperparameters (learning rate, schedule, warmup, weight decay, seeds) are unstated, there are no ablations and runs are single.

## See Also
- [[Contrastive and Masked Vision-Language Pretraining]] — related (the family comparison)
- [[CLIP Contrastive Language-Image Pretraining]] — prerequisite-for (the two-tower recipe it builds on)
- [[ALIGN Noisy Alt-Text Dual Encoder]] — prerequisite-for
- [[Swin Transformer Shifted Windows]] — prerequisite-for (basis of the CoSwin encoder)
