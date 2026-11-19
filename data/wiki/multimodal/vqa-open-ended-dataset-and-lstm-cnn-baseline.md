---
title: VQA Open-Ended Dataset and LSTM-CNN Baseline
tags: [multimodal, benchmarks-and-metrics, reference]
summary: "The original VQA dataset (about 0.25M images, 0.76M questions, 10M answers) with a VGG-plus-LSTM baseline at 58.16% open-ended accuracy against 83.30% for humans, and a language-only model at 48.76% showing how much the benchmark rewards question priors."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-antol-2015-vqa.md
---

# VQA Open-Ended Dataset and LSTM-CNN Baseline

Antol et al. define free-form, open-ended visual question answering as an automatically evaluable task and release a crowdsourced dataset. Numbers are self-reported by the paper on real COCO images unless noted.

## Dataset and metric

The collection has 204,721 real COCO images plus 50,000 synthetic abstract scenes, with 3 questions per image (written to stump a "smart robot") and 10 human answers each: roughly 0.25M images, 0.76M questions and 10M answers. An answer scores min(humans giving it / 3, 1), so three matching workers earn full credit. Splits: test-dev for debugging, test-standard for reporting, test-reserve to guard against overfitting, test-challenge for winners. Answers are one word in 89.32% of cases, so BLEU or ROUGE collapse to exact match, and "yes" makes up 58.83% of yes/no answers.

## Baseline model

Frozen VGGNet fc7 image features and an LSTM question embedding are fused by element-wise product, then an MLP with softmax over the top 1,000 answers, which cover 82.67% of train+val answers and so cap a classifier's ceiling.

- Best model (deeper LSTM Q plus normalised image): 58.16% open-ended and 63.09% multiple-choice (18 candidates) on test-standard.
- Humans with question and image: 83.30% on open-ended; human multiple-choice accuracy is 88.53% (91.54% by majority); inter-human open-ended agreement 80.62% on 3,000 questions.
- Humans shown only the question score 40.81% overall, and 21.22% on "other" questions. Given the question plus a human caption but no image, they score 57.47% on a 3K-question subset.
- Model priors on test-dev: always "yes" 29.66%, image-only 28.13%, language-only LSTM Q 48.76%, nearest neighbour 42.70%. Element-wise product beats concatenation by 0.95%; training on a confidence-filtered set (344,600 questions) lowers accuracy by 1.13%.
- Perceived requirements (MTurk workers, not controlled): the model acts like a 4.74-year-old, while the average required age is 8.98; commonsense is 17.35% against 31.23% required. Accuracy drops from 61.07% on questions rated for ages 3 to 4 to 47.83% on those rated 18+. On 47.43% of questions, at least three of ten subjects said commonsense is needed.

## Limits

- Optimiser, learning rate, batch size, epochs and hardware are not stated.
- The language-only result shows the benchmark rewards question priors; exact string matching ignores synonyms and plurals and depresses "other" agreement below 76%.
- Age and commonsense estimates reflect crowd perception. Answers are short, so the task is short-answer only. The models are 2015-era and scores are superseded.

## See Also
- [[Visual Question Answering Benchmarks]] — related
- [[VQA v2 Balanced Dataset]] — extends
- [[Microsoft COCO]] — related (source of the real images)
- [[Contrastive and Masked Vision-Language Pretraining]] — related
