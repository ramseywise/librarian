---
title: HotpotQA
tags: [eval, benchmark]
summary: "A crowdsourced multi-hop QA set where each question needs two Wikipedia paragraphs and carries sentence-level supporting facts; the 2018 baseline scores 58.28 answer F1 in the distractor setting but 34.36 in the full wiki setting, against 91.40 for humans (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-yang-2018-hotpotqa.md
---

# HotpotQA

Yang and colleagues (EMNLP 2018) ask how to build a question set that needs reasoning over several documents, is not tied to a knowledge-base schema, and supervises the evidence as well as the answer. Crowd workers on Mechanical Turk wrote the questions over pairs of Wikipedia first paragraphs and marked the supporting sentences.

## Construction and settings

- **Bridge questions**: paragraph pairs come from the hyperlink graph, and the **bridge entity** linking them must be inferred. **Comparison questions**: pairs come from curated lists.
- **Distractor setting**: the two gold paragraphs are mixed in a shuffled set with eight distractors chosen by bigram tf-idf. **Full wiki setting**: the system must answer from the opening paragraphs of the whole of Wikipedia, with no gold paragraphs supplied.
- Scoring uses answer EM/F1, supporting-fact EM/F1, and **joint** metrics that multiply answer and supporting-fact precision and recall before taking F1; joint EM is 1 only when the answer and the supporting facts are both exactly right.
- The baseline is a reimplemented multi-paragraph reader with a supporting-fact classifier. Train-medium (56,814 questions) holds multi-hop examples the baseline answered correctly with high confidence under three-fold cross-validation.

## Results (self-reported)

Setup: dev set, baseline trained with supporting-fact supervision unless noted.

- Distractor: 44.44 answer EM, 58.28 answer F1, supporting-fact F1 66.66 (EM only 21.95), joint F1 40.86.
- Full wiki (distractor-trained model on the top 10 tf-idf paragraphs): 34.36 answer F1, joint F1 17.73. Retrieval of the gold paragraphs is weak, with Hits@10 of 56.06 on dev. F1 on bridge questions goes from 59.09 to 30.42, but on comparison questions only from 55.05 to 50.70.
- Human answer F1 is 91.40 against 68.99 for the baseline on 1,000 random samples in the distractor setting; the human ceiling for joint F1 is 96.37.
- Without supporting-fact supervision answer F1 is 56.19, about 2 below 58.28. Giving the model just the supporting facts as context yields 66.98 answer F1. Dropping train-easy and train-medium gives 43.61.
- Of 100 manually classified dev and test questions, 42% need chain reasoning through a bridge entity.

## Limits

- One baseline architecture; hyperparameters and seeds are not stated. The authors say their way of using supporting-fact supervision is probably not the best.
- Full wiki MAP and mean rank are optimistic bounds, since gold paragraphs the retriever missed are assigned a fixed rank. Full wiki uses first paragraphs only.
- Dev and test were selected for being hard for the 2018 baseline, and train-medium carries the same selection bias. In a sample, about 6% of questions are single-hop and 2% cannot be answered.
- Workers agree less on supporting facts than on answers, so that part of the task is partly subjective. The baseline is long surpassed.

## See Also
- [[2WikiMultiHopQA]] — extends (builds multi-hop questions from Wikidata triples and compares itself with this set)
- [[Math Word Problem Benchmarks]] — related
- [[RAG Evaluation]] — prerequisite-for
- [[FRAMES Benchmark]] — related (multi-document retrieval and reasoning questions)
