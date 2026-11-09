---
title: Microsoft COCO
tags: [multimodal, reference]
summary: "Microsoft COCO is a 2014 object dataset of non-iconic Flickr images with per-instance segmentations (91 categories, 2.5M instances, 328k images); a DPM detector lost about half its AP moving from PASCAL VOC to COCO (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-lin-2014-microsoft-coco.md
---

# Microsoft COCO

Lin et al. (ECCV 2014) set out to build a dataset that moves object recognition toward scene understanding, covering off-centre non-iconic views, reasoning from context and exact 2D placement of objects. An **iconic** image shows one large object from a canonical viewpoint; COCO images deliberately avoid that. **Thing** categories have countable instances; **stuff** categories (materials, no clear boundaries) are not included.

## Construction

To get non-iconic images, the authors queried Flickr using two object categories at a time, or a scene paired with an object. Amazon Mechanical Turk annotation ran in three stages. First came hierarchical category labelling by 5 workers, then instance spotting by 5 workers, then segmentation by one trained worker per image; roughly a third of workers passed the training.

## Reported figures (self-reported)

- 91 categories, 2.5M labelled instances, 328k images; most categories are well populated (82 of the 91 exceed 5,000 instances). Segmentation was unfinished at publication.
- Images average 3.5 categories each; only 10% have a single category, against over 60% for ImageNet detection validation and PASCAL.
- Labour: 17,751 worker hours for category labelling, 8,417 for spotting, around 60,000 in all; each 1,000 segmentations cost upward of 22 worker hours.
- Baseline (DPMv5, 20 PASCAL categories; the COCO-trained model uses a 55k-image subset): trained on PASCAL, average AP is 29.6 on PASCAL VOC 2012 and 16.9 on COCO. COCO-trained, it scores 19.1 on COCO and 26.8 on PASCAL. The cross-dataset drop is 12.7 AP for the PASCAL-trained model and 7.7 for the COCO-trained one.
- The authors caution that harder training images need not help a model of limited capacity like DPM, and the effect differs by category.

## Limits

- Only DPMv5 baselines; no deep models, though the authors expect CNNs to improve results. The generalisation advantage claimed for COCO-trained models is tested on a single model family in one run.
- Segmentation by a single worker with only periodic checks; no stuff, occlusion, keypoint or caption labels (captions are named as future work).
- The 91-category list and annotation interfaces are in an extended version, not this paper.

## See Also
- [[POPE Object Hallucination Probing]] — related (builds probes from COCO objects)
- [[Visual Instruction Tuning and Tool-Using VLMs]] — related
- [[Object Detection Anchors, Non-Max Suppression and Focal Loss]] — related (detectors are evaluated on COCO)
- [[Food-101 and car-197 Fine-Grained Datasets]] — related (another dataset paper of the same era)
- [[Visual Question Answering Benchmarks]] — related (VQA sets built on COCO images)
- [[Deep Visual-Semantic Alignments]] — related
- [[Faster R-CNN]] — related
- [[ILSVRC ImageNet Challenge]] — related
