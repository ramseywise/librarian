---
title: Faster R-CNN
tags: [multimodal, concept]
summary: "Faster R-CNN adds a fully convolutional Region Proposal Network that shares convolutional features with the detector, cutting proposal cost to 10 ms per image and reaching 5 fps with VGG-16 (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-ren-2016-faster-r-cnn.md
---

# Faster R-CNN

Ren et al. (arXiv v3, January 2016, extending the NIPS 2015 paper to journal length) tackle the proposal bottleneck of region-based detectors. Their Region Proposal Network (RPN) is fully convolutional: given an image of arbitrary size, it returns rectangular proposals, each with an objectness score. Since it reads the very convolutional features the Fast R-CNN detector uses, proposals cost almost nothing extra.

## Mechanism

- The RPN slides a 3x3 convolution over the shared feature map, followed by two sibling 1x1 layers (class and box regression) over k anchors per position. An anchor is a reference box centred on the sliding window with a scale and aspect ratio; k is 9 by default, and the design is translation invariant with single-scale images.
- Box regression uses offsets relative to the anchor (centre shifts normalised by anchor size, log ratios for width and height). The loss sums a classification term and a regression term weighted by lambda.
- Sharing is obtained with a 4-step alternating training schedule between the RPN and Fast R-CNN. Anchors crossing the image boundary are ignored in training (about 6000 of about 20000 remain per 1000x600 image); the authors report training does not converge if they are kept.

## Results (self-reported)

- Speed (K40 GPU, VGG-16, 300 proposals, Selective Search on CPU): 198 ms total against 1830 ms for Selective Search plus Fast R-CNN, about 5 fps; proposals cost 10 ms against 1510 ms. With the ZF backbone, 17 fps (59 ms).
- PASCAL VOC 2007 test (VGG-16, shared, 300 proposals): 73.2 mAP trained on VOC07+12 and 78.8 with COCO pretraining. VOC 2012 test: 70.4 with 07++12 training, 75.9 with COCO added.
- On COCO test-dev with VGG-16, 300 proposals and one scale, the paper reports 42.1 at mAP@0.5 and, separately, 21.5 at mAP@[.5,.95]. The baseline of Fast R-CNN with Selective Search gets 39.3 and, on the stricter average, 19.3. Swapping in ResNet-101 lifts COCO val to 48.4 and 27.2.
- Ablations use ZF on VOC07. Sharing features yields 59.9 versus 58.7 without sharing. Dropping box regression at test time takes mAP down to 52.1. Random proposals score 44.6 at 100 and 55.8 at 1000. The two-stage RPN plus detector (58.7) outperforms one-stage dense detection (53.9).
- Anchors (VGG-16, VOC07): one anchor per position costs 3 to 4 points; 3 scales with one ratio (69.8) matches 3 scales and 3 ratios (69.9); lambda between 1 and 100 changes mAP by about 1%.

## Limits

- Input is single-scale and the stride is 16 throughout; anchor settings are described by the authors as not carefully chosen, and ablations use VOC07 with one backbone.
- The speed comparison puts Selective Search on a CPU against a GPU network, which the authors call inequitable.
- No seeds, variances or significance tests. Backbones (ZF, VGG-16) and the code base are dated. Approximate joint training is claimed close with no table.

## See Also
- [[Visual Question Answering Benchmarks]] — related
- [[TextVQA and LoRRA]] — related
- [[LXMERT]] — extends (consumes 36 detected objects per image)
- [[Microsoft COCO]] — related (a detection benchmark here)
- [[ILSVRC ImageNet Challenge]] — related
