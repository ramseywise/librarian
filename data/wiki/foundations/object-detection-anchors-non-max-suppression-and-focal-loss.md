---
title: "Object Detection Anchors, Non-Max Suppression and Focal Loss"
tags: [foundations, concept]
summary: "Detectors predict a grid of anchor boxes, then filter by score and non-max suppression; one-stage detectors drown in easy background anchors, which focal loss (1-p_t)^gamma discounts, provided the classifier bias starts every anchor at 1% object probability."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--notes--04-convolutional-networks.md
---

# Object Detection Anchors, Non-Max Suppression and Focal Loss

## Anchors and filtering

A one-stage detector (YOLOv2) predicts, per cell of a 19x19 grid, 5 anchor boxes with class scores: about 1,800 boxes per image, mostly useless. Two steps filter: threshold on score, then **non-max suppression** (NMS), which keeps the best box and drops others whose IoU (intersection over union) with it exceeds a threshold. Example: two cars and five boxes; the first two boxes had IoU 0.822; NMS kept boxes [0, 2]. The threshold is a setting: 0.1 kept [0, 2], while 0.95 kept all 5 (the maximum overlap was 0.907).

Anchors come from the region proposal network (RPN) of two-stage detectors, which scores 9 anchors (3 sizes x 3 aspect ratios) at each feature-map position; YOLOv2 picks its 5 shapes by k-means on training boxes. The RPN reuses the detector's own features: 10 ms per image against about 2 s for a hand-built proposal method, and 300 proposals beat 2,000 (69.9 vs 66.9 mAP on VOC 2007). Using raw anchors without box adjustment cut mAP from 56.8 to 52.1 in a smaller ablation, and a one-stage dense-window variant scored 4.8 points lower (53.9 vs 58.7).

## The imbalance problem

A one-stage detector scores about 100,000 anchor locations per image, nearly all easy negatives, whose small losses add up and swamp the few objects. Two-stage detectors cut to 1,000-2,000 boxes and sample a 1:3 positive-to-negative ratio. **Focal loss** instead multiplies cross-entropy by (1 - p_t)^gamma; with gamma = 2 an example already right at p_t = 0.9 costs 100x less. On COCO with a ResNet-50 RetinaNet, AP rose from 31.1 (best alpha-balanced cross-entropy) to 34.0 at gamma 2, and gamma 5 fell back to 32.2. Plain cross-entropy diverged until the final classifier's bias was set so every anchor starts at 1% object probability: an initialisation change, not a loss change (see [[Weight Initialisation and Activation Scale]]). The full RetinaNet reached 39.1 AP.

## See Also
- [[Convolution, Shift Sensitivity and Parameter Sharing]] — prerequisite-for
- [[Weight Initialisation and Activation Scale]] — related
