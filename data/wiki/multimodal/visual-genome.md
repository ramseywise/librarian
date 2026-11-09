---
title: Visual Genome
tags: [multimodal, reference]
summary: "Visual Genome densely annotates 108,077 images with region descriptions, objects, attributes, relationships, scene graphs and about 17 QA pairs per image, canonicalised to WordNet synsets; it is the base for GQA (all figures self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-krishna-2017-visual-genome.md
---

# Visual Genome

Krishna et al. (IJCV 123, 2017) hold that models must grasp how objects relate to each other, so training data ought to carry dense annotations of them rather than a single caption or a few labels per image. Mechanical Turk workers wrote region descriptions and drew boxes, then pulled out objects, attributes and relationships and authored question-answer pairs. Verification and WordNet canonicalisation followed. Every image is Creative Commons and lies in the overlap of MS-COCO and YFCC100M.

## Contents (self-reported)

- The set has 108,077 images. Each carries roughly 50 region descriptions, 35 objects, 26 attributes, 21 relationships and 17 QA pairs, across six question types with binary questions excluded; VQA has 614,163.
- There are 33,877 object categories, averaging 113.45 objects each, and 42,374 distinct relationships.
- An image's scene graph merges its region graphs, where each region graph is a directed graph of the objects, attributes and relationships behind one region description.
- Canonicalisation to WordNet is 85.7 precision and 95.9 recall for attributes, 92.9 and 88.5 for relationships.
- Region descriptions are more semantically diverse than COCO captions: with five sampled descriptions, about 4 clusters against 2 (t = -240, p < 0.01).

## Baselines (self-reported)

The baselines are a fine-tuned VGG-16 with SVMs for attribute and relationship prediction, NeuralTalk for region captioning, and an answer-frequency baseline for QA. Relationship prediction is difficult (top 100 relationships, 80/10/10 split by image), and also predicting the object class raises attribute accuracy. For the frequency baseline, why questions are the hardest.

## Limits

- Annotation is not exhaustive, so a correct prediction may still be marked wrong. Images lean toward people and sports, men receive twice the annotations women do, and 93.02% of workers were based in the US.
- The baselines date from 2015, are untuned and were run without seeds. Exact match is a poor QA metric for long answers.

## See Also
- [[Visual Question Answering Benchmarks]] — related
- [[GQA Benchmark]] — extends (builds questions from its scene graphs)
- [[Microsoft COCO]] — prerequisite-for (all images are also COCO images)
- [[Deep Visual-Semantic Alignments]] — related (NeuralTalk is its region-captioning baseline)
