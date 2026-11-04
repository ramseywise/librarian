---
title: "Sampled Ranking Metrics and MRR"
tags: [foundations, pattern]
summary: "Ranking each positive against 99 sampled negatives is a different metric from the full ranking, inflates scores several-fold and flipped the order of two models; rank the whole catalogue, and use MRR only when one good result ends the task."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--05-time-series-and-recommenders--notes--03-two-tower-and-evaluation.md
---

# Sampled Ranking Metrics and MRR

Ranking every item for every user is expensive, so for years evaluations ranked each test positive against 99 random negatives and reported hit rate. That is not a noisy version of the true metric but a different one: sampled metrics are inconsistent with exact ones, model A can beat B on the full ranking and lose on the sample even in expectation, and as the sample shrinks all metrics collapse towards AUC. Advice: avoid sampling at evaluation time, or apply a correction if you must.

## Measured

Hit rate at 10, film split:

| Model | Full HR@10 | Sampled HR@10 |
|---|---:|---:|
| Popularity | 0.0904 | 0.5029 |
| EASE | 0.1366 | 0.5911 |
| Two-tower, logQ | 0.1248 | 0.6173 |
| Two-tower, plain | 0.0379 | 0.3260 |

Sampled numbers are about four to nine times higher, so a reader would think the models far better than they are, and EASE beats the corrected tower on the full ranking but loses on the sample. With 999 negatives instead of 99 the inflation shrank from more than fourfold to about 1.3 times (EASE 0.1723, tower 0.1683) and the order recovered, but that took more than half of a 1,682-item catalogue, so the practical rule stays: rank the whole catalogue.

## MRR versus recall and NDCG

**Mean reciprocal rank** gives each user 1/rank of their best-placed relevant item, ignoring everything after it. Recall@10, NDCG@10 and MRR for popularity, EASE, tower-logQ and tower-plain: MRR 0.1582, 0.2270, 0.1972, 0.0788; all three metrics ordered the models the same way here, but they need not (a model placing one liked film first and nothing else in the top 10 scores well on MRR, poorly on recall). Use MRR when a single good result ends the task, recall and NDCG when the list as a whole is the product. Ties counted in the item's favour make popularity's MRR slightly generous.

NDCG came from a need for graded relevance and a discount for documents a user is less likely to reach; with only binary hits and a log2(rank+1) divisor, only the discount separates it from recall.

## See Also
- [[RMSE vs Top-N Ranking in Recommenders]] — prerequisite-for
- [[Two-Tower Retrieval with logQ Correction]] — related
- [[Counterfactual Evaluation with Inverse Propensity Scoring]] — extends (the next rung of offline evaluation)
