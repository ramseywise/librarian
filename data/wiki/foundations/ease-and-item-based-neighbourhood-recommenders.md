---
title: "EASE and Item-Based Neighbourhood Recommenders"
tags: [foundations, concept]
summary: "EASE is a linear item-item model with a zero diagonal and a closed-form solution from one matrix inverse; with item kNN it led a small-catalogue ranking table, though the cubic inverse limits it to catalogues of tens of thousands."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--05-time-series-and-recommenders--notes--02-collaborative-filtering-and-matrix-factorisation.md
---

# EASE and Item-Based Neighbourhood Recommenders

## Item kNN

"People who liked this also liked that." Compare items rather than users: item relationships change slowly enough to precompute, which scales, and on early film-rating experiments quality also beat user-based methods. Compute a similarity per item pair from co-occurrence, keep each item's strongest neighbours (50 here), and score an unseen item by summing similarities to what the user liked. A shrink term (10 here) stops two rare items with one shared fan from looking identical.

## EASE

If co-occurrence similarity works, learn the item-item matrix B by regression instead: predict each column of the user-item matrix from the others, with L2 regularisation. The crucial constraint, inherited from an earlier sparse linear method (SLIM): the diagonal of B must be zero, or each item simply predicts itself. The constrained problem has a closed form:

```
P = (R^T R + lambda I)^-1
B_ij = -P_ij / P_jj   (i != j),    B_jj = 0
```

Training is one matrix inversion (0.04 s on a 1,682-item catalogue). Lambda was chosen on validation users' future: NDCG 0.1378 at 30, 0.1406 at 100, 0.1374 at 300, 0.1337 at 1000.

## Result and limit

On the film split, positives only: item kNN recall 0.1369 / NDCG 0.1140; EASE 0.1550 / 0.1259; popularity 0.0752 NDCG; rating-fitted MF 0.0340 (full table in [[RMSE vs Top-N Ranking in Recommenders]]). Two lines of linear algebra beat everything tried so far. The inverse costs cubic time in the number of items, so EASE fits catalogues in the tens of thousands, not millions; that limit more than accuracy pushes large systems to factor models ([[Implicit Feedback: iALS and BPR]]) and towers ([[Two-Tower Retrieval with logQ Correction]]). A small dataset with a small catalogue is its home ground.

EASE also cannot score an item it never saw: its score is zero everywhere, so on hidden new films it matched random (recall 0.079 against 0.082 random).

## See Also
- [[RMSE vs Top-N Ranking in Recommenders]] — prerequisite-for
- [[Implicit Feedback: iALS and BPR]] — alternative-to
- [[Two-Tower Retrieval with logQ Correction]] — alternative-to
- [[Regularisation as a Prior]] — related (the L2 term)
