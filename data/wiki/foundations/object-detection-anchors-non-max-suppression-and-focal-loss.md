---
title: "Object Detection Anchors, Non-Max Suppression and Focal Loss"
tags: [foundations, concept]
summary: "Detectors predict a grid of anchor boxes, then filter by score and non-max suppression; one-stage detectors drown in easy background anchors, which focal loss (1-p_t)^gamma discounts, provided the classifier bias starts every anchor at 1% object probability."
updated: 2026-11-09
sources:
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--notes--04-convolutional-networks.md
  - data/raw/papers/2026-11-07-lin-2017-focal-loss-dense-object-detection.md
---

# Object Detection Anchors, Non-Max Suppression and Focal Loss

## Anchors and filtering

A one-stage detector (YOLOv2) predicts, per cell of a 19x19 grid, 5 anchor boxes with class scores: about 1,800 boxes per image, mostly useless. Two steps filter: threshold on score, then **non-max suppression** (NMS), which keeps the best box and drops others whose IoU (intersection over union) with it exceeds a threshold. Example: two cars and five boxes; the first two boxes had IoU 0.822; NMS kept boxes [0, 2]. The threshold is a setting: 0.1 kept [0, 2], while 0.95 kept all 5 (the maximum overlap was 0.907).

Anchors come from the region proposal network (RPN) of two-stage detectors, which scores 9 anchors (3 sizes x 3 aspect ratios) at each feature-map position; YOLOv2 picks its 5 shapes by k-means on training boxes. The RPN reuses the detector's own features: 10 ms per image against about 2 s for a hand-built proposal method, and 300 proposals beat 2,000 (69.9 vs 66.9 mAP on VOC 2007). Using raw anchors without box adjustment cut mAP from 56.8 to 52.1 in a smaller ablation, and a one-stage dense-window variant scored 4.8 points lower (53.9 vs 58.7).

## The imbalance problem

A one-stage detector scores about 100,000 anchor locations per image, nearly all easy negatives, whose small losses add up and swamp the few objects. Two-stage detectors cut to 1,000-2,000 boxes and sample a 1:3 positive-to-negative ratio. **Focal loss** instead multiplies cross-entropy by (1 - p_t)^gamma; with gamma = 2 an example already right at p_t = 0.9 costs 100x less. On COCO with a ResNet-50 RetinaNet, AP rose from 31.1 (best alpha-balanced cross-entropy) to 34.0 at gamma 2, and gamma 5 fell back to 32.2. Plain cross-entropy diverged until the final classifier's bias was set so every anchor starts at 1% object probability: an initialisation change, not a loss change (see [[Weight Initialisation and Activation Scale]]). The full RetinaNet reached 39.1 AP.

The focal loss paper (Lin et al., ICCV 2017, arXiv 1708.02002) reports the following for its RetinaNet (self-reported). With ResNet-50-FPN at 600px, gamma 2 adds 2.9 AP over alpha-balanced cross-entropy and the best alpha for gamma 0 is .75; one square anchor gives 30.3 AP and 3 scales by 3 ratios gives 34.0, with more anchors adding nothing. With ResNet-101-FPN focal loss beats the best online hard example mining variant by 3.2 AP (36.0 vs 32.8). On test-dev, RetinaNet-101-800 with scale jitter and a 1.5x longer schedule reaches 39.1 AP and a ResNeXt-101 backbone 40.8; RetinaNet-101-600 matches a ResNet-101-FPN Faster R-CNN at 122 ms against 172 ms on an M40. An alternate form with gamma 2 and beta 1 gets 33.8 AP, close to 34.0.

## Limits

The extraction notes that the paper's runs are single, so gains of 0.2-0.4 AP are within unreported noise. Only the binary focal loss is tested; a hinge-loss attempt was unstable with no numbers. The authors concede faster, more accurate results came later from a Faster R-CNN variant, and training GPU type and compute are not stated.

## See Also
- [[Convolution, Shift Sensitivity and Parameter Sharing]] — prerequisite-for
- [[Weight Initialisation and Activation Scale]] — related
- [[Microsoft COCO]] — related (the benchmark its detectors are scored on)
