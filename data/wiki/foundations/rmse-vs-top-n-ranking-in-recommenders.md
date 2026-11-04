---
title: "RMSE vs Top-N Ranking in Recommenders"
tags: [foundations, concept]
summary: "A recommender is judged on the short list it shows, not on rating error; the model with the best RMSE lost to a popularity list on top-10, so score full-catalogue ranking, split by time, and put popularity and simple linear models in every table."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--05-time-series-and-recommenders--notes--02-collaborative-filtering-and-matrix-factorisation.md
  - data/raw/repos/learn-ai-engineering/data-science--05-time-series-and-recommenders--README.md
---

# RMSE vs Top-N Ranking in Recommenders

Collaborative filtering learns preferences from a nearly empty user-item table. Nobody sees the RMSE; a person sees a short list chosen from the whole catalogue. The demonstration used a 100,000-rating film dataset (943 users, 1,682 films, 6.3% dense), where the top 10% of items held 43% of ratings.

## Biases do most of the rating work

Predicting a rating as the global mean plus a user bias plus an item bias takes RMSE from 1.2290 (predict the mean) to 1.0147. Adding a latent-factor dot product, `mu + b_u + b_i + p_u . q_i`, fitted on observed cells only with L2 regularisation by SGD, reaches 0.9959. The biases account for about 0.21 of the drop and the factors only about 0.02, on a chronological split that is harder than the random holdouts behind many published numbers. The factors are still meaningful: a film's nearest neighbours in factor space are films liked by the same people, with no genre information used.

## Top-N metrics

A test item is a hit if rated 4 or 5. Rank the whole catalogue minus items the user has already seen, then report:

- **Recall@10**: share of a user's relevant test items on the list, with denominator capped at the list length.
- **NDCG@10**: the same with more credit near the top (binary hits discounted by log2(rank+1)).
- **Coverage**: share of the catalogue appearing on anyone's list. A high NDCG with 4% coverage is a bestseller list.

| Model | Recall | NDCG | Coverage |
|---|---:|---:|---:|
| Popularity | 0.0900 | 0.0752 | 0.0446 |
| Random | 0.0054 | 0.0049 | 0.9952 |
| MF fitted on ratings | 0.0428 | 0.0340 | 0.2140 |
| Item kNN | 0.1369 | 0.1140 | 0.2271 |
| EASE | 0.1550 | 0.1259 | 0.2235 |

The MF model, best on RMSE, scores under half of popularity's NDCG. It was never asked to rank unrated films; when it does it reaches for less popular ones (median 90 training positives per listed film against 262 for popularity), so its scores rest on far less data. It answers a different question, it is not broken. Algorithms tuned on RMSE do not necessarily do well at top-N, and non-personalised popularity can be surprisingly competitive.

## Splitting interaction data

Split by time. One global cut is closest to production but here most post-cut raters had no history (109 of 301 had any), so a per-user chronological split (oldest 80% train, next 10% validate, newest 10% test) was used as a named compromise. A random 90/10 split more than doubled EASE's NDCG (0.309 against about 0.126) and lifted popularity from 0.075 to 0.135, with the same model: none of it is skill. Choose hyperparameters on validation, never test.

## The reproducibility warning

Of 18 recent top-n algorithms, only 7 could be reproduced with reasonable effort; 6 of those were often beaten by simple heuristics such as nearest neighbours, and the last did not consistently beat a well-tuned linear method. A widely cited claim that a learned MLP is a better similarity than a dot product reversed under proper tuning: the plain dot product substantially beat it and was far cheaper to serve. Habit to take: popularity, kNN and EASE in every table, tuned as carefully as the favourite model.

## Pitfalls

- Optimising RMSE and shipping a list.
- Not removing seen items at evaluation.
- Treating empty cells as dislikes, or ignoring them: weight them low, sample them, or use a closed form ([[Implicit Feedback: iALS and BPR]]).
- Popularity feedback: logs come from the previous recommender, so popular things get shown, clicked and shown again ([[Counterfactual Evaluation with Inverse Propensity Scoring]]).
- Averages hide segments: light users gained more from EASE (NDCG 0.061 to 0.131) than heavy users (0.090 to 0.121).
- Training on all ratings including 1s and 2s lowered EASE's NDCG from 0.126 to 0.116 while raising coverage from 0.22 to 0.28.

## See Also
- [[EASE and Item-Based Neighbourhood Recommenders]] — extends
- [[Implicit Feedback: iALS and BPR]] — extends
- [[Sampled Ranking Metrics and MRR]] — extends
- [[Two-Tower Retrieval with logQ Correction]] — extends
- [[Forecast Baselines and Rolling-Origin Backtest]] — related (the same baseline-first habit)
