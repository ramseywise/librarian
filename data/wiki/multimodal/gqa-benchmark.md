---
title: GQA Benchmark
tags: [multimodal, concept]
summary: "GQA builds 1.7M balanced compositional questions from Visual Genome scene graphs and adds consistency, validity, plausibility, distribution and grounding metrics; the best 2019 model, MAC, scores 54.06% against 89.3% for humans (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-hudson-2019-gqa.md
---

# GQA Benchmark

Hudson and Manning (CVPR 2019) argue that answer priors dominate existing VQA benchmarks. Their dataset generates questions from Visual Genome scene graphs that were cleaned first, applying functional programs and 524 patterns, and smooths the answer distribution inside each question group to balance it. Baselines plus the BottomUp and MAC models are judged on accuracy and five newly proposed metrics.

## Dataset (self-reported)

Generation produced 22,669,678 questions on 113,018 images, which were downsampled to 1.7M balanced ones. The split is 70/10/10/10 across train, validation, test and challenge, grouped by image. Balancing lifts the entropy of the answer distribution by 72%. Relative to VQA, GQA covers 88.8% of the questions and 70.6% of the answers, and 52% of GQA questions are compositional compared with 3% for VQA 2.0.

## New metrics

Consistency means accuracy on those questions whose answers follow from another question that was answered correctly. Validity checks that an answer falls within the question's scope, and plausibility checks that it is reasonable. Grounding is the attention probability placed on the annotated region, so it applies to attention models only.

## Results (self-reported; GQA test, models trained on the balanced training set)

- MAC, the best model, reaches 54.06% accuracy; humans reach 89.3%. A blind question-only LSTM gets 41.07%.
- Humans reach 98.4% consistency, MAC 81.59% and BottomUp 78.71%. On grounding, MAC is at 82.24% and BottomUp at 78.47%; the figure falls to 43% when spatial features take the place of object features.
- MAC gets 53.8% accuracy from text questions and 59.7% when given functional programs as input.
- Transfer runs both ways. MAC trained on GQA scores 52.1% on VQA, rising to 60.5% after fine-tuning, whereas training on VQA itself gives 68.3%. MAC trained on VQA scores 39.8% on GQA, then 46.5% after fine-tuning.

## Limits

- Questions are templated, not natural, and cover only factual, answerable-from-image questions: no why or intention questions, no OCR, no external knowledge.
- Plausibility may be imprecise for rare objects, grounding exists only for attention models, and the paper reports no seeds, learning rate or batch size.
- The baselines date from 2017-2018. The extraction notes a mismatch between the abstract figures (42.1, 54.1) and Table 1 (41.07, 54.06). The authors concede that more training data might still help.

## See Also
- [[Visual Question Answering Benchmarks]] — related
- [[Visual Genome]] — prerequisite-for (supplies the scene graphs)
- [[VQA v2 Balanced Dataset]] — related (the prior-biased benchmark GQA argues against)
- [[LXMERT]] — related (reports GQA results with no scene graphs or programs)
