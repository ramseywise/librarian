---
title: PAWS Word-Swapping Paraphrase Adversaries
tags: [eval, language-tasks, benchmark]
summary: PAWS builds paraphrase pairs with high word overlap but different word order by LM-constrained word swapping and back translation, then has five humans label them; BERT drops to 33.5% on PAWS-QQP when trained on QQP alone and recovers to 85.0% with PAWS training (self-reported).
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-zhang-2019-paws.md
---

# PAWS Word-Swapping Paraphrase Adversaries

Zhang, Baldridge and He (NAACL 2019) ask whether a paraphrase dataset of high-lexical-overlap pairs can expose, and help repair, models' insensitivity to word order and structure. A PAWS pair is two sentences with high bag-of-words overlap but different word order.

## Construction

- **Word swapping:** candidate sentences are produced by constrained beam search under a one-billion-word language model, swapping words while keeping the sentence acceptable to the LM and the constraints (about 3% of candidates pass).
- **Back translation:** English-German-English translation yields paraphrases with a different surface form.
- **Human labels:** five annotators label each pair as paraphrase or not.

Swapping yields mostly non-paraphrases (67% on Quora, 88% on Wikipedia); back translation yields 94.9% paraphrases (26,897 pairs from Wikipedia). In QQP itself, among roughly 1,000 pairs sharing an identical bag of words, only about 20% are non-paraphrases.

The dataset has 108,463 human-labelled pairs across PAWS-QQP, PAWS-Wiki and PAWS-Wiki-Swap, plus 656k unlabelled PAWS-Wiki pairs used for silver-label pretraining. PAWS-Wiki has an 8,000-pair test set; Because PAWS-QQP lacks a test set, its results come from a dev set of 677 pairs. On swapped pairs, annotators match the majority label 92.0% of the time on Quora text and 94.7% on Wikipedia text; keeping only pairs with at least four matching votes raises these to 95.8% and 97.5%.

## Results (self-reported)

- Trained on QQP alone, all six models stay below 40% on PAWS-QQP although each exceeds 83% on QQP itself; BERT-base gets 90.5% on QQP and 33.5% on PAWS-QQP.
- With 11,988 PAWS-QQP training pairs added, BERT reaches 85.0% on PAWS-QQP (AUC from 35.1 to 83.1) and QQP accuracy does not suffer. DIIN (590k parameters) goes from 32.8% to 83.8%; the bag-of-words model barely moves (29.0 to 30.0%).
- BiLSTM trails BERT by 4.2% on QQP but by 27% on PAWS-QQP.
- With 6,000 PAWS-QQP examples, DIIN and BERT both go from about 30% to 74% AUC, and the curves have not converged.
- BERT-base on PAWS-Wiki test: 90.4% supervised only, 91.9% with silver-label pretraining. DIIN's AUC on PAWS-Wiki is 46.0% without PAWS data, 70.5% trained on QQP plus PAWS-QQP, and 92.9% when trained in-domain on PAWS-Wiki.
- DIIN answers 280 (41%) of BERT's 687 PAWS-Wiki test mistakes correctly.

## Limits

- No variance, seeds or significance tests; only BERT-base was run (BERT-large did not fit in GPU memory), with default hyperparameters.
- The paper proposes no method that solves PAWS; it evaluates existing models. English only.
- PAWS-QQP has no test set. The learning curves have not converged, so more data would likely help.
- SuperGLUE's authors exclude PAWS-Wiki because BERT beat their crowd human baseline there (91.9 against 84% accuracy).

## See Also
- [[Paired Input-Perturbation Eval]] — related (another way of testing sensitivity to small input changes)
- [[SuperGLUE and CoLA Language Understanding Benchmarks]] — related (SuperGLUE considered and excluded PAWS-Wiki)
- [[SNLI and MultiNLI Crowdsourced NLI Corpora]] — related
