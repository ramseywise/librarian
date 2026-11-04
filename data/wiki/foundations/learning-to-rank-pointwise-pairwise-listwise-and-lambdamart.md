---
title: "Learning to Rank: Pointwise, Pairwise, Listwise and LambdaMART"
tags: [foundations, concept]
summary: "Learning to rank trains on one item, one pair or one whole list; NDCG is flat or discontinuous so LambdaMART defines gradients (RankNet's times |delta NDCG|) instead of a loss, yet on a matching task moving to pairs bought most of the gain and the NDCG factor little."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--05-time-series-and-recommenders--notes--04-entity-matching-and-learning-to-rank.md
---

# Learning to Rank: Pointwise, Pairwise, Listwise and LambdaMART

Treat each bank line as a **query** and each candidate invoice as a **document** with a grade (2 true link, 1 another invoice from the right supplier, 0 otherwise). NDCG handles grades and rewards the top of the list (scored at 5 here). The three setups differ in what one training example is.

- **Pointwise**: one example is one pair with its label; fit a classifier, sort by probability. Never looks at the rest of the list.
- **Pairwise**: one example is two candidates of one query and which goes first. RankNet models P(i beats j) = 1 / (1 + exp(-sigma(s_i - s_j))) and minimises cross-entropy. Collecting the gradient per document (a lambda) cuts training time per query from close to quadratic to close to linear.
- **Listwise**: one example is a whole list. XE-NDCG is a cross-entropy between the model's distribution over the list and one derived from the grades, shown to bound NDCG.

## Why not optimise NDCG directly, and LambdaMART

Sorting makes NDCG everywhere either discontinuous or flat in the scores. Pairwise cross-entropy has a gradient but counts every swap equally: a list can go from 13 pairwise errors to 11 by moving a top document down, better for RankNet and worse for NDCG. LambdaRank writes no loss, only the wanted gradient: RankNet's, multiplied by |delta NDCG|, the change in NDCG if the two documents swapped. Pairs near the top pull hard, far-down pairs barely. **LambdaMART** feeds these gradients to boosted trees (specifying gradients and the Newton step), which gives no objective to analyse but works; an ensemble won a track of a 2010 learning-to-rank challenge. In LightGBM it is `objective="lambdarank"` with group sizes per query.

## Results (five generated ledgers, train on earliest 60%, test last 20%)

| Model | NDCG@5 | Top-1 |
|---|---:|---:|
| Closest amount | 0.5397 | 0.4714 |
| Fellegi-Sunter weights | 0.8703 | 0.8332 |
| Pointwise linear | 0.9101 | 0.8012 |
| Pairwise linear (RankNet) | 0.9374 | 0.8440 |
| Pointwise trees | 0.9129 | 0.8513 |
| Pairwise trees, no NDCG factor | 0.9416 | 0.8541 |
| Pairwise trees + NDCG factor | 0.9451 | 0.8600 |
| LambdaMART (LightGBM) | 0.9469 | 0.8628 |
| Listwise trees (XE-NDCG) | 0.9413 | 0.8495 |

LambdaMART won all five paired comparisons, but read where the gain comes from:

- The biggest step is having features at all (0.54 to 0.87).
- The second is changing the training example: pointwise to pairwise adds about 0.03 for trees and linear alike, and a pairwise linear model (0.9374) beats pointwise trees (0.9129), so here the objective mattered more than the model family.
- The famous |delta NDCG| factor moved the same trees by 0.0035, about an eighth of what pairs bought.
- Listwise lost all five ledgers by 0.0056, though in web-search benchmarks it had a small edge (48.23 against 48.08 NDCG@5); the gap is data-dependent.
- Top-1 is a harsher, noisier judge (standard deviation over 0.02); if only the top pick is linked, pointwise trees are a simpler start.

Dropping one evidence group from LambdaMART: all features NDCG 0.9469 / top-1 0.8628; no reference 0.9195 / 0.7675; no name 0.7720 / 0.7917; no amount 0.8855 / 0.6991; no date 0.9193 / 0.7926. Name matters most to NDCG (it lifts grade-1 candidates), amount most to top-1 (it picks one invoice among a supplier's several): the grade definition is a real design decision. The generator's difficulties were chosen; rerun on your own data before trusting close orderings.

## See Also
- [[Blocking and Fellegi-Sunter Match Weights]] — prerequisite-for
- [[Match Errors Are Not Classification Errors]] — extends
- [[RMSE vs Top-N Ranking in Recommenders]] — prerequisite-for (NDCG)
- [[Two-Tower Retrieval with logQ Correction]] — related (the retrieve-then-rank funnel)
