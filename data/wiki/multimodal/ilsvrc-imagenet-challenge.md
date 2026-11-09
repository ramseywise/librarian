---
title: ILSVRC ImageNet Challenge
tags: [multimodal, concept]
summary: "The ILSVRC paper documents how the ImageNet challenge was built, how classification, localization and detection entries improved from 2010 to 2014, and a two-annotator human comparison with GoogLeNet (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-russakovsky-2015-imagenet-large-scale-visual-recognition.md
---

# ILSVRC ImageNet Challenge

Russakovsky et al. (arXiv v3, January 2015) describe the ImageNet Large Scale Visual Recognition Challenge: dataset construction, metrics, a survey of 2010 to 2014 entries, significance tests, a per-class analysis and a human comparison.

## Construction and metrics

- Categories come from WordNet, candidate images from search engines, labels are verified on a crowd platform. Detection boxes use a three-step pipeline and hierarchical multi-label queries. A naive presence annotation of 200 classes over 60,000 images would cost 80 times the classification labelling (self-reported), which the hierarchy avoids.
- Classification, 2012 to 2014: 1000 classes, 1,281,167 training, 50,000 validation and 100,000 test images, scored by top-5 error (no returned label matches). Detection 2014: 200 classes, 456,567 training images; the overlap threshold is loosened for small boxes (self-reported counts).
- Quality checks: about 99.7% image-level label precision (5 errors in 1500 checked test images); the box pipeline fully covers 97.9% of images with 99.2% tight boxes (10 categories, 200 images each) (self-reported).

## Findings (self-reported)

- The winning top-5 error shrank by a factor of 4.2 between 2010 and 2014, or 2.4 counting only from 2012 (SuperVision to GoogLeNet), when the dataset stopped changing. Error on single-object localization shrank 1.7 times. Detection mAP grew 1.9 times between 2013 and 2014, though the 2014 winner relied on external data and a larger detection training set. Extra data gave that framework 3.7 points; its 2014 method gained 5.8 on unchanged data, going from 26.3% to 32.0%.
- The "optimistic" model takes the best entry for each class, whatever its data. It averages 94.6% classification accuracy over a class range of 41.0 points, with 81.5% localization and 44.7% detection AP. Objects lacking texture are harder than those with little texture, and object scale has only a weak effect on classification.
- Human study on 1500 test images: the trained annotator (A1) beat GoogLeNet's 5.8% error (one-sided z-test p=0.022); the second annotator (A2, 100 training images, 258 labelled) was much worse. Of GoogLeNet's errors, 21% came from small or thin objects and 13% from image filters. Bootstrap 99.9% intervals separate winner from runner-up in every 2012-2014 track.

## Limits

- One label per image makes classification ambiguous (hence top-5); remaining label errors sit in fine-grained classes labelled by non-experts.
- 2013 and 2014 detection figures are not directly comparable. The human study has two annotators and heavy training. Classes changed in 2010 to 2012, rules on outside data were revised in 2014, and entrants' compute and hyperparameters are not reported.

## See Also
- [[Visual Question Answering Benchmarks]] — related
- [[Faster R-CNN]] — related
- [[Microsoft COCO]] — related (the newer benchmark with segmentation)
- [[Food-101 and Car-197 Fine-Grained Datasets]] — related
