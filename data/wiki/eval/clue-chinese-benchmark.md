---
title: CLUE Chinese Benchmark
tags: [eval, benchmark]
summary: "A GLUE-style benchmark of nine Chinese language understanding tasks plus a 514-pair diagnostic set; the best 2020 baseline averages 74.90 against 85.09 for humans, a gap of about 10 points (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-xu-2020-clue.md
---

# CLUE Chinese Benchmark

Xu and colleagues (COLING 2020) argue that Chinese language understanding needs its own benchmark because Chinese differs from English and because Chinese models still leave a gap to humans of the kind that English benchmarks no longer show. CLUE follows GLUE's multi-task and diagnostic design.

## Contents

- Nine tasks, two newly created: three single-sentence, three sentence-pair and three machine reading comprehension, each with one metric.
- A raw pre-training corpus of 214 GB (about 76 billion words), against about 1.1 GB for Chinese Wikipedia.
- A 514-pair hand-written natural language inference diagnostic set by linguists covering nine phenomena, including some unique to Chinese; models are tested on it after fine-tuning on OCNLI.
- A toolkit and an online leaderboard, with a certified mark for open-source submissions whose results the organisers can reproduce.

## Results (self-reported)

Setup: nine fine-tuned Chinese transformers, test score from the best dev run of three; human figures are the majority vote of annotators on 100 test items for five tasks and published figures for four.

- RoBERTa-wwm-ext-large, the strongest baseline, scores 74.90 on average to the humans' 85.09.
- On the Winograd-style CLUEWSC2020, humans score 98.0 against 81.38 for the best model. TNEWS is hardest for both (human majority 71.0, best model 58.61). On CSL the top model (82.13) outscores the average annotator (80.0).
- A small ALBERT variant with about one twentieth of BERT-base parameters loses up to about 12 points on single and pair tasks but up to 40 on ChID, and scores 31.86 on C3, near chance.
- Diagnostic: RoBERTa-wwm-ext-large 61.5 overall, BERT-base 53.5, XLNet-mid 54.7, majority baseline 35.1. Monotonicity is hardest (43.3 for RoBERTa).

## Limits

- Human scores for five tasks rest on 100 items and three annotators, whose scores differ a lot (TNEWS ranges from 57.0 to 73.0).
- There is no variance across fine-tuning runs, and the models differ together in size, pre-training data and masking, so the cause of any gap is not isolated.
- The diagnostic set is small (24 to 100 pairs per category) and uses only OCNLI fine-tuning.
- No contamination check between pre-training corpora and task sets; BERT-class encoders only, no generative LLMs.

## See Also
- [[BIG-bench]] — related
- [[AGIEval]] — related
- [[Eval Contamination Defenses]] — related
