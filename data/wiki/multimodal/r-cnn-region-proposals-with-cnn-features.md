---
title: "R-CNN Region Proposals with CNN Features"
tags: [multimodal, vision-backbones, concept]
summary: "R-CNN runs a CNN on about 2000 warped selective-search proposals per image and scores the features with per-class SVMs; the paper reports 53.7% mAP on VOC 2010 against 35.1% for the best listed baseline, at 13 s per image on a GPU (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-girshick-2014-rich-feature-hierarchies-accurate-object.md
---

# R-CNN Region Proposals with CNN Features

Girshick, Donahue, Darrell and Malik (CVPR 2014; the PDF read is arXiv tech report v5) ask whether a large CNN run over bottom-up region proposals, pre-trained with supervision on ImageNet and then fine-tuned for the target domain, can push detection and segmentation accuracy far past systems built on HOG and SIFT. R-CNN stands for Regions with CNN features.

## Pipeline

1. About 2000 selective-search proposals per image are warped to 227x227. Warping with 16 px of context padding beat the alternatives by 3 to 5 mAP points in pilot experiments on VOC.
2. An AlexNet-style CNN in Caffe, first trained for ILSVRC2012 classification and then fine-tuned on warped proposals, produces 4096-d features.
3. Per-class linear SVMs score the features, followed by greedy non-maximum suppression.
4. A ridge regressor on pool5 features can then adjust each box (optional). With proposal P and learned offsets d, the centre moves by P's width and height times d_x and d_y, and the width and height are scaled by exp(d_w) and exp(d_h).

## Results (self-reported)

- VOC 2010 test, with T-Net features and selective-search proposals: box regression brings R-CNN to 53.7% mAP; the listed baselines reach 35.1% (UVA) and 33.4% (DPM v5). VOC 2011/12 test: 53.3% mAP, a gain of more than 30% relative to the previous best.
- ILSVRC2013 detection test (200 classes, with bounding-box regression, fine-tuned on val1+train1k): 31.4% mAP against OverFeat's 24.3%.
- VOC 2007 test (T-Net): fine-tuning on VOC 2007 trainval adds 8.0 points to 54.2% (fc7, no regression), against DPM v5 at 33.7%. Bounding-box regression lifts that to 58.5%. Using the 16-layer O-Net in place of T-Net lifts 58.5% to 66.0%, at about 7x the forward-pass time.
- With no fine-tuning (only the ILSVRC2012 pre-trained CNN), dropping fc7 costs nothing; fc7 features generalise less well than fc6, and pool5 accounts for about 6% of the parameters.
- Scoring with the fine-tuned network's own softmax instead of SVMs gives 50.9% VOC 2007 mAP in place of 54.2% (fine-tuned fc7). Raising the SVM negative IoU threshold from 0.3 to 0.5 lost 5 mAP points (VOC validation).
- On the ILSVRC val2 ablation (fc7, SVMs trained on val1+train1k), fine-tuning gives 29.7% mAP and bounding-box regression 31.0%.
- Segmentation on VOC 2011 test (CPMC regions, no fine-tuning): the full+fg variant on fc6 features scores 47.9% mean accuracy.
- The paper contrasts Szegedy et al.'s regression-based detection (30.5% mAP on VOC 2007, as reported) with 58.5% for R-CNN on the same set.

## Limits

- Slow: 13 s per image on a GPU and 53 s on a CPU, with OverFeat about 9x faster (2 s per image).
- Training has several stages (CNN fine-tuning, SVMs, bounding-box regressors).
- Selective search recalls just 91.6% of ILSVRC objects at 0.5 IoU.
- Hyperparameters for ILSVRC were carried over from PASCAL, which the authors call undoubtedly slightly suboptimal.
- The dominant error mode is mislocalisation.
- Without fine-tuning, segmentation only roughly ties O2P.
- The paper reports no seeds, variance, precision or pre-training hyperparameters.

## See Also
- [[Faster R-CNN]] — extends
- [[VGG Depth with Stacked 3x3 Filters]] — prerequisite-for
- [[ILSVRC ImageNet Challenge]] — related
- [[Object Detection Anchors, Non-Max Suppression and Focal Loss]] — related
