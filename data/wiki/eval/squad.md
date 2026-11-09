---
title: SQuAD
tags: [eval, reference]
summary: A span-extraction reading-comprehension benchmark of 107,785 crowdsourced questions on 536 Wikipedia articles, scored by exact match and token F1 against humans; the CNN/Daily Mail cloze corpus is its large semi-synthetic predecessor.
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-rajpurkar-2016-squad.md
  - data/raw/papers/2026-11-07-hermann-2015-teaching-machines-read-comprehend.md
---

# SQuAD

Rajpurkar and colleagues (EMNLP 2016) built SQuAD v1.0 to see whether a big, careful, span-answer reading set on Wikipedia could be made, and how a feature-based baseline compares with people.

## Construction and metrics

Passages come from the top 10,000 Wikipedia articles by PageRank; 536 were sampled uniformly and paragraphs under 500 characters dropped, leaving 23,215 paragraphs split 80/10/10 into train, dev and test. Mechanical Turk workers wrote questions whose answers are spans; dev and test carry at least 2 extra answers. Exact match counts a hit against any one reference. F1 is a bag-of-tokens score taken as the maximum over references and then averaged; punctuation and articles are ignored in both.

## Results (self-reported)

- Humans, test set, second answer scored against the rest: EM 77.0, F1 86.8; on dev, EM 80.3, F1 90.5.
- A feature-rich logistic regression (candidates restricted to constituents, 180M features): 51.0 F1 on dev and test, EM 40.4 on test. Dropping the lexicalised and dependency-path features together took dev F1 down to 35.8 from 51.0.
- By answer type on dev, the logistic regression ranged from 72.1 F1 (Date) to 31.2 (Verb Phrase) while humans ranged from 82.4 to 95.4.
- On dev, 77.3% of correct answers are constituents, so methods that choose among constituents are capped there.
- A hand label of 192 dev questions found syntactic variation in 64.1% and multiple-sentence reasoning in 13.6%; the paper reports syntactic divergence through dependency-path edit distance.
- A neural model by Wang and Jiang (2016) reported 70.3 F1 on v1.1 soon after release.

## Predecessor: CNN/Daily Mail cloze

Hermann and colleagues (NIPS 2015) built a supervised reading dataset from news articles and their summary bullets: one entity in a bullet becomes a placeholder, and entities are replaced by coreference-based markers permuted each time an item is loaded. The two corpora total roughly a million items. They compared symbolic baselines with Deep LSTM, Attentive and Impatient Readers; the Attentive Reader was the best neural model on the CNN test set (the extraction gives no figures), and on CNN, across all documents, the most frequent entity was correct just 30.5% of the time (self-reported).

## Limits

- Answers are spans, narrower than interpretative questions; every question has an answer in its passage (2.6% were marked unanswerable by a second worker, none excluded as such).
- The human score is agreement between annotators, and dev (90.5) differs from test (86.8).
- All results use v1.0; later models and v1.1 are not covered.
- CNN/Daily Mail: the frame-semantic baseline simplifies the parser and covers little; many queries are ambiguous, and coreference mistakes can turn one person into two markers; no human ceiling, seeds or variance are reported; the authors concede many queries needing long-range inference go unanswered.

## See Also
- [[TyDi QA]] — related (a native-language alternative to SQuAD-style data)
- [[Output Length Confounds Reference Metrics]] — related (uses SQuAD as a test set)
- [[Wizard of Wikipedia]] — related (used as multi-task training data)
- [[LAMA Knowledge Probe]] — related
