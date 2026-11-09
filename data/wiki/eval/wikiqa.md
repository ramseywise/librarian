---
title: WikiQA
tags: [eval, benchmark]
summary: "A 3,047-question answer-sentence-selection set from Bing query logs where about two-thirds of questions have no correct sentence, introducing the answer triggering task; the best system's question-level F1 stays only slightly above 30% (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-yang-2015-wikiqa.md
---

# WikiQA

Yang, Yih and Meek (EMNLP 2015) argue that the earlier QASENT (TREC-QA) benchmark selects candidates by lexical overlap with the question, which inflates word-matching methods in a more natural setting. WikiQA instead samples questions from Bing query logs, links each by clicks to a Wikipedia page, takes every sentence of the page summary as a candidate, and has crowd workers label them.

## Answer triggering

Because candidates are not pre-filtered, many questions have no correct sentence. **Answer triggering** asks a system to detect whether any candidate is correct and, if so, return one; it is scored by question-level precision, recall and F1, with the threshold tuned on dev. The study compared seven baselines (word counts, LCLR, Paragraph Vector, a CNN and two combinations) by MAP and MRR on QASENT and WikiQA, then ran the best, a CNN with word-count features, on answer triggering.

## Results (self-reported)

- The dataset has 3,047 questions and 29,258 candidate sentences. About two-thirds of questions have no correct sentence, and 20.3% of answer sentences share no content words with the question. Description questions are 36% of WikiQA against 7% of QASENT.
- Word counting is weak on WikiQA compared with QASENT. On QASENT a plain CNN scores below word counting, yet on WikiQA it scores above it; word-matching features add about 3 to 4 MAP/MRR points to the CNN, which was best by MAP.
- The best answer-triggering F1 barely exceeds 30%. Adding question length raised F1 most; a question-class feature slightly lowered it.

## Limits

- Candidates are drawn only from the page's summary paragraph, so whether the pool contains the answer is never tested.
- The triggering study covers one system with few features. No seeds, variance or significance tests, and model details are not given; the CNN reimplementation performs slightly worse than the cited original.
- The neural baselines are from 2014 and later models far surpass them.

## See Also
- [[HotpotQA]] — related (a later Wikipedia-based question set)
- [[RAG Evaluation]] — prerequisite-for
- [[Eval Metric Interpretation Pitfalls]] — related (question-level scoring when no answer exists)
