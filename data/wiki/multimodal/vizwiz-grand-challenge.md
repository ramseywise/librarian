---
title: VizWiz Grand Challenge
tags: [multimodal, concept]
summary: "VizWiz is a VQA dataset of 31,173 questions that blind users asked about their own phone photos; about 28.63% are unanswerable, and VQA v2-trained models score about 0.14 accuracy on it off the shelf (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-gurari-2018-vizwiz-grand-challenge.md
---

# VizWiz Grand Challenge

Gurari et al. (arXiv 1802.08218 v4, 2018) built a goal-oriented VQA dataset in a natural setting, from photos and spoken questions that blind users submitted via the VizWiz app. Questions were transcribed and filtered for privacy, and each received 10 crowd-worker answers. Three published VQA models and eight answerability predictors are benchmarked in the paper.

## Dataset facts (self-reported)

- 31,173 visual questions remain from 48,169 shareable candidates, split 20,000 / 3,173 / 8,000. About 31% (14,796) of the candidates were filtered out, split into 7,477 with a missing question, 4,626 in a crowd round and 2,693 in an expert round.
- Around 28.63% of questions are unanswerable, meaning at least half of the 10 answers call them unanswerable or the image unsuitable. Separately, 28% of images were judged unsuitable by two or more of 10 workers.
- Questions are brief, with a median of five words, and 27.88% open with an uncommon first word, versus 13.4% in VQA 2.0. Exact-match agreement among humans on an answer holds for 97.7% of questions.

## Model results (self-reported)

- Models trained on VQA v2.0 and used unchanged reach about 0.14 accuracy on the test set, and only 824 of the 3,000 most common VizWiz answers are among the 3,000 most common VQA 2.0 answers. Fine-tuning the best model gets 0.475, scratch training 0.465 to 0.469, and humans 0.75.
- Transfer in the other direction is weak too, since VizWiz-trained models score only 0.218 to 0.318 on VQA 2.0 test.
- For unanswerable questions, unchanged off-the-shelf models get 0.06-0.07, fine-tuned ones 0.77-0.78 and scratch-trained ones 0.80.
- For predicting unanswerability, the question-plus-image predictor reaches average precision 71.7 against 30.6 for a prior relevance method; the image alone gives 64.

## Limits

- Table 4 gives 34.6% unanswerable answer types while the text gives 28.63%, unexplained; model citation labels are swapped between the text and Table 3.
- Filtering took out complex scenes and blurry images, which may make the released set easier than the raw stream.
- Crowd workers, not blind users, judge answerability. The paper gives no seeds, variance or hyperparameters for scratch training, and its models are 2018 systems lacking pretrained vision-language models.

## See Also
- [[Visual Question Answering Benchmarks]] — related
- [[VQA v2 Balanced Dataset]] — prerequisite-for (the VQA 2.0 data and baseline it evaluates)
- [[TextVQA and LoRRA]] — related (reports that up to 21% of VizWiz questions involve reading text)
