---
title: "Entity-Disjoint Splits and Group Scores for Pair Matchers"
tags: [foundations, pattern]
summary: "Because match labels are transitive, a random pair split leaks the answer: close the labels into groups, hold out whole groups, block inside each side, and tune on group F1 when merging, since closure chains pair errors."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--05-time-series-and-recommenders--notes--04-entity-matching-and-learning-to-rank.md
  - data/raw/repos/learn-ai-engineering/data-science--05-time-series-and-recommenders--notes--05-learning-a-similarity-function.md
---

# Entity-Disjoint Splits and Group Scores for Pair Matchers

The thing held out is a pair, but each record sits in many pairs. Put matches A-B and B-C in training and A-C in test, and the answer is implied before the model reads a word. (The ledger problem in [[Blocking and Fellegi-Sunter Match Weights]] splits by time instead, since production meets tomorrow's lines.)

## Does the split tell the truth?

Generated parts catalogue (about 1,700 records, 13,000 candidate pairs, about 8% positive, five seeds). Train on one catalogue, score a new one. F1 estimated on the split against F1 on the truth (a new catalogue):

| Model and split | Estimate | Truth |
|---|---:|---:|
| Similarity features, random pairs | 0.793 | 0.779 |
| Token identity (sees which words), random pairs | 0.489 | 0.239 |
| Similarity features, parts disjoint | 0.859 | 0.728 |
| Token identity, parts disjoint | 0.548 | 0.466 |
| Similarity features, specs disjoint | 0.783 | 0.771 |
| Token identity, specs disjoint | 0.461 | 0.456 |

A matcher that reads nothing, joining training labels into groups and predicting same group, scored F1 0.478 (precision 1.0, recall 0.315) on the random split: any score near that line mostly says the labels connect. The similarity model lost only 0.014, so leakage depends on the features as well as the split. Holding out whole parts narrowed the token model's gap from 0.250 to 0.082 but flattered the similarity model (0.859 against 0.728): holding out parts scatters a part's look-alikes across the sides, leaving 0.86 look-alike pairs per match against 1.73 in a new catalogue; holding out specs keeps them together (1.38) and closes gaps to 0.012 and 0.005. Hold out everything a model could confuse, not just what matches. On real benchmarks the same pattern: one text matcher fell from F1 93.06 with seen entities to 67.82 with unseen; across three common benchmarks 96% to 100% of test records already appeared in training; another benchmark saw 79.16 to 70.24 for a cross-encoder, 58.07 to 29.70 for word co-occurrence, while a similarity-feature model stayed level (35.83, 36.61).

## Procedure

1. **Close the labels first**: link records by every match label on all the data; each connected component is one group (a found group, as in `GroupKFold`).
2. **Assign groups to sides, then block inside each side.** Blocking first discards cross-side pairs and changes the base rate.
3. **Check near-duplicates across sides** (no study measured this for matching; borrowed reasoning).

Which split is honest depends on production: if the matcher only sees known entities, a seen-entity score may be right, stated with its limit; report both when new entities will come.

## Closing predictions is a different test

Merging takes the closure of decisions (A-B and B-C make one group, errors included). Tuning the threshold on validation pair F1 gave group F1 0.332 (sd 0.211) and a largest group of about 69 records when the largest true group is about 7; threshold 0.206 against 0.500 even when peeking at the new catalogue (pair F1 0.795 but group F1 0.599, against 0.671 tuning on group F1). Tuning on group F1 without peeking gave 0.620. A graph-based benchmark on real company records shows the same fall: pairwise F1 96.53, group F1 56.92 before graph cleanup, 91.64 after; one dataset showed no such fall. In the capstone, with no review band 8.4 wrong pairs became 17.2 after closure ([[Similar vs Interchangeable in Matching]]).

## See Also
- [[Match Errors Are Not Classification Errors]] — prerequisite-for
- [[Tabular ML Leakage Taxonomy]] — related (group leakage)
- [[Similar vs Interchangeable in Matching]] — extends
- [[Tuning an Embedding Model from Match Labels]] — related (building batches from closed groups)
