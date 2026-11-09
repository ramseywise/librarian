---
title: Visual Commonsense Reasoning and Adversarial Matching
tags: [multimodal, concept]
summary: "VCR is a four-way multiple-choice dataset of movie-scene questions, answers and rationales built with Adversarial Matching; the R2C model reaches 44.0% on the staged answer-plus-rationale task against 85.0% for humans (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-zellers-2019-recognition-cognition.md
---

# Visual Commonsense Reasoning and Adversarial Matching

Zellers et al. (CVPR 2019) ask whether vision systems can answer commonsense questions about an image and justify the answer. They contribute the VCR task and dataset, a dataset-construction algorithm called Adversarial Matching, and a baseline model, R2C.

## Adversarial Matching

VCR combines movie-scene images with questions, answers and rationales written by crowd workers. Wrong choices need to look plausible while being clearly wrong, so each correct answer is recycled as a negative for other questions, exactly three times over. The assignment is a max-weight bipartite matching, whose weight combines a log relevance term, log P_rel(q_i, r_j), with lambda times a second term that penalises similarity: the log of one minus P_sim(r_i, r_j). A relevance model (BERT) rates how well a candidate suits the query, and a similarity model (ESIM with ELMo) helps steer away from candidates close to duplicating the true answer. The authors set this against Adversarial Filtering, whose wrong answers were machine-generated.

## R2C

R2C grounds text in image regions with a BiLSTM, contextualises through attention, and reasons with a second BiLSTM, taking frozen BERT features together with ResNet50 features for objects.

## Results (self-reported)

- On the test set R2C reaches 44.0% on the staged Q->AR task (both answer and rationale correct; chance 6.25%), against 85.0% for humans (5-worker majority on 200 questions). The best VQA model, MLB, gets 17.2%.
- On Q->AR, BERT with text alone outscores every VQA model, and R2C adds roughly 9 points to BERT.
- Validation ablations for Q->AR: dropping query contextualisation loses about 21.6 points; GloVe in place of BERT leaves 18.3%; taking out visual features at the grounding step leaves 33.8%; deleting the reasoning LSTM loses about 1.9 points.
- BERT given only the response sits close to chance on Q->A, at 27.7% against 25% chance, which the authors take to mean answer-only artifacts are small. On datasets with human-written distractors, answer-only BERT-Base reaches 33.8% (MovieQA) up to 45.8% (TGIFQA), compared with 27.6% on VCR Q->A.

## Limits

- Test accuracy is far from the human 85%, so the authors treat the task as unsolved; BERT is frozen in R2C and end-to-end fine-tuning would likely raise results.
- Language priors persist in QA->R, where BERT without the image scores 64.1% on validation. Distractors built from remapped detection tags can come out ungrammatical.
- Because it draws on movie data, the dataset is biased against women and minorities, and the authors recommend not deploying models trained on VCR.
- One run per entry; human score from 200 test questions. Later models are far above R2C.

## See Also
- [[Visual Question Answering Benchmarks]] — related
- [[VQA v2 Balanced Dataset]] — related (VQA baselines are evaluated on VCR)
- [[VLM Benchmark Shortcuts]] — related
