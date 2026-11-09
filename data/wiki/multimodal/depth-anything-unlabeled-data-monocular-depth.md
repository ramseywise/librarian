---
title: Depth Anything Monocular Depth from Unlabeled Data
tags: [multimodal, method]
summary: "Depth Anything scales monocular depth estimation by pseudo-labeling 62M unlabeled images with a teacher, training a student under strong perturbation and aligning its features to a frozen DINOv2 encoder."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-yang-2024-depth-anything-2401-10891.md
---

# Depth Anything Monocular Depth from Unlabeled Data

The question is whether a monocular depth foundation model can come from scaling up with big unlabeled image sets and pseudo labels, even though labeled data is already plentiful. The hypothesis is that unlabeled images improve zero-shot generalisation when the student faces a tougher target and takes semantic priors from DINOv2.

## Mechanism

A teacher trained on 1.5M labeled images produces labels for 62M unlabeled images. A student, re-initialised, trains on both sets; the unlabeled images get CutMix and colour perturbation, and a feature-alignment loss L_feat = 1 - mean cosine similarity to a frozen DINOv2 encoder is applied, with a tolerance margin. Later the encoder is fine-tuned for metric depth (within the ZoeDepth framework) and for segmentation.

## Results

- ViT-L has lower AbsRel than MiDaS v3.1 ViT-L on all six unseen sets, for instance NYUv2 0.043 against 0.048 and Sintel 0.458 against 0.587 (self-reported). Setup: zero-shot relative depth, with scale and shift fitted to the ground truth.
- ViT-S (24.8M) trails MiDaS on NYUv2 (0.053 against 0.048) and DIODE (0.076 against 0.075), yet is ahead on KITTI, Sintel, DDAD and ETH3D (self-reported).
- Pseudo-labelled data without perturbation brings no gain (KITTI AbsRel 0.085), while strong perturbation plus L_feat gives 0.076 on KITTI and 0.043 on NYUv2 (self-reported). Setup: ViT-L ablation.
- Applying L_feat to labeled data gives no benefit (self-reported).
- Fine-tuned for Cityscapes semantic segmentation the encoder gets 86.2 mIoU, and on ADE20K 59.4 against 58.3 before (self-reported). Setup: Mask2Former, ViT-L.
- Downstream, it beats the MiDaS encoder (ADE20K 59.4 vs 52.4) and the original DINOv2 encoder (NYUv2 AbsRel 0.056 vs 0.066) (self-reported).

## Limits

- The biggest model is ViT-L, and the training resolution of 518 is judged too small for real applications.
- MiDaS trained on NYUv2 and KITTI images, so in those two comparisons the baseline saw in-domain training data.
- The paper states no compute, batch size, seeds or latency, and the ControlNet benefit is only shown qualitatively.
- Zero-shot relative evaluation fits scale and shift to the ground truth, so it says nothing on metric distance.

## See Also
- [[Vision-Language Model Training Families]] — related (a vision encoder trained with frozen-encoder alignment)
- [[Contrastive Self-Supervised Pretraining]] — related
