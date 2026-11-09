---
title: VQA v2 Balanced Dataset
tags: [multimodal, concept]
summary: "VQA v2 pairs every question with two similar COCO images that have different answers, so a model cannot succeed on language priors alone; models trained on the original unbalanced set lose accuracy on it (all figures self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-goyal-2017-making-v-vqa-matter.md
---

# VQA v2 Balanced Dataset

Goyal et al. (arXiv 1612.00837, v3 May 2017) ask whether visual question answering models lean on language priors instead of the image. Their remedy is to collect, for each question in the original VQA set, a second image for which the answer differs, so the dataset roughly doubles in size and each question comes with a complementary image pair.

## How the pairs are built

AMT workers see the question plus the 24 nearest COCO neighbours of the original image (by fc7 features) and pick one image for which the question still makes sense but the answer changes. Ten new answers are then collected for the chosen image. The authors report that workers marked 22% of questions (about 135K) as having no such image, and that about 9% of pairs still end with the same majority answer (both self-reported).

## What the benchmark showed

Setups use train/test letters: U is the unbalanced original, B the balanced set, Bhalf a balanced train set matched in size to the original.

- MCB, trained on U and tested on balanced validation (UB), scores 54.22 overall against 60.36 when tested on U (self-reported). Yes/No accuracy falls from 81.20 to 70.40 for MCB and from 79.99 to 67.62 for HieCoAtt (self-reported).
- A language-only baseline falls from 48.21 to 41.40 on the same change of test set (self-reported). An always-yes prior scores 24.04 on balanced validation (self-reported).
- Training MCB on Bhalf lifts the UB figure from 54.22 to 56.08, and training on full B reaches 59.14 on balanced validation (self-reported). The authors read the 2-3 point gap between Bhalf and B as models being data starved.
- HieCoAtt answers both images of a complementary pair correctly for 17.7% of pairs when trained balanced and 13.5% when trained unbalanced (self-reported).
- Balancing raises the entropy of the answer distribution by 56%. The paper also observes that, in the original set, replying yes to "Do you see a ..." questions was correct 87% of the time (self-reported).

A counter-example explanation model that retrieves the image it believes has a different answer scores Recall@5 of 43.39 against 42.84 for a plain image-distance baseline, 21.65 for a VQA model and 20.79 for random (K=24 candidates, human-picked image as target; self-reported).

## Limits

- The dataset is not perfectly balanced, by the authors' own account, and the 22% of questions with no complementary image get no pair.
- A human-picked counter-example is neither unique nor necessarily the best, which makes Recall@5 approximate, and the distance baseline comes close to the proposed explanation model.
- No hyperparameters, optimisers, seeds or variance are reported for any model.

## See Also
- [[Visual Question Answering Benchmarks]] — related
- [[Microsoft COCO]] — prerequisite-for (the image source)
- [[VLM Benchmark Shortcuts]] — related
- [[GQA Benchmark]] — related (also argues VQA sets are prior-biased)
- [[VizWiz Grand Challenge]] — related (evaluates VQA v2 models off the shelf)
