---
title: DETR Set Prediction Object Detection
tags: [multimodal, vision-backbones, concept]
summary: "DETR decodes 100 learned object queries in parallel with a transformer encoder-decoder and trains with Hungarian bipartite matching, removing anchors and non-maximum suppression; it matches Faster R-CNN at 42.0 AP on COCO but needs 300 to 500 epochs."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-carion-2020-end-end-object-detection-transformers.md
---

# DETR Set Prediction Object Detection

Carion et al. ask whether detection can be treated as set prediction directly, using a transformer encoder-decoder trained with a bipartite matching loss, dropping anchors and non-maximum suppression while still matching Faster R-CNN on COCO. They hypothesise that self-attention across every pair of predictions can remove duplicates by itself, which makes hand-designed post-processing unnecessary.

## Method

A ResNet backbone feeds a transformer of 6 encoder and 6 decoder layers (d=256, 8 heads). N=100 object queries, which are learned positional encodings given to the decoder and added again at every attention layer, are decoded in parallel rather than autoregressively; a shared feed-forward network turns each into a class and a box. The Hungarian loss first finds the lowest-cost one-to-one assignment of predictions to ground-truth objects (the argmin over permutations of the summed matching cost); the loss on matched pairs adds class negative log-likelihood, L1 and generalised IoU box terms, with auxiliary losses after every decoder layer. A mask head extends the model to panoptic segmentation.

## Results (self-reported; COCO 2017 val unless noted)

- DETR with ResNet-50 (six encoder and six decoder layers, width 256, 8 heads, 100 queries; trained 500 epochs on 118k images, validated on 5k) reaches 42.0 AP, level with Faster R-CNN-FPN+ at the same parameter count. The DC5 ResNet-101 variant scores 44.9 AP against 44.0 for Faster R-CNN-R101-FPN+.
- Large-object AP is 61.1 against 53.4 for Faster R-CNN-FPN+, but small-object AP is 20.5 against 26.6.
- Panoptic: DETR-R101 reaches 45.1 PQ against 44.1 for PanopticFPN++ R101 (mask head trained 25 epochs on a frozen DETR); 46 PQ on the COCO test set.
- Ablations on the 300-epoch schedule: dropping every encoder layer costs 3.9 AP (6.0 on large objects), while a 12-layer encoder gives 41.6 AP at 95 GFLOPS. AP rises after each decoder layer, 8.2 AP in total between the first and last. Omitting spatial positional encodings loses 7.8 AP, and dropping the feed-forward networks shrinks the model from 41.3M to 28.7M parameters at a cost of 2.3 AP. Box loss with L1 alone scores 35.8 AP, generalised IoU alone 39.9 and the two together 40.6.
- Predicting the second-best class for empty slots instead of filtering them out gains 2 AP. NMS only helps the first decoder layer and slightly hurts the last ones.
- Training for 500 epochs instead of 300 gives 1.5 more AP; random crop adds about 1 AP. The 300-epoch baseline needs 3 days on 16 V100 GPUs (4 images per GPU, batch size 64).
- On synthetic images DETR detects every instance up to 50 visible ones but only around 30 when 100 are present, and it finds all 24 giraffes in an image although training never showed more than 13.

## Limits

- Very long training (300 to 500 epochs) compared with Faster R-CNN; the authors note new challenges in training and optimisation.
- Lower small-object AP than Faster R-CNN; the authors expect FPN-like fixes. The model cannot predict more objects than its 100 query slots.
- Loss ablations use a single weighting. Panoptic mask AP trails baselines by up to 8 on things classes. The published inference code omits batching and simplifies the positional encodings, and no seeds or variance appear.
- The extraction notes that the paper's relevance to language models is the contrast between its parallel decoding and autoregressive decoding.

## See Also
- [[Faster R-CNN]] — alternative-to
- [[Object Detection Anchors, Non-Max Suppression and Focal Loss]] — prerequisite-for
- [[Feature Pyramid Networks]] — related (the authors expect FPN-like fixes for small objects)
- [[Transformer Architecture]] — prerequisite-for
- [[Microsoft COCO]] — related
