---
title: "Two-Tower Retrieval with logQ Correction"
tags: [foundations, pattern]
summary: "A two-tower model embeds users and items separately so item vectors precompute into an ANN index and new items embed from features; in-batch softmax over-penalises popular items unless log sampling probability is subtracted in training only."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--05-time-series-and-recommenders--notes--03-two-tower-and-evaluation.md
---

# Two-Tower Retrieval with logQ Correction

## Why retrieve first

Heavy models cannot run over millions of items per page view. A large recommender is a funnel: candidate generation narrows the catalogue cheaply to hundreds (judged on **recall**, since anything dropped is unrecoverable), a ranker with rich and cross features orders them (judged on precision near the top), and re-ranking applies diversity, freshness and business rules.

## The two towers

One network turns user features into a vector, another turns item features into a vector, the score is the dot product. Because the towers never see each other's inputs, all item vectors are computed once in batch and put in an approximate nearest neighbour index; serving is one user forward pass plus one lookup. The price is no user-item cross-features (those belong in the ranker). Matrix factorisation is the special case where each tower is an id embedding lookup; a tower can take anything (genres and release year for a film; age, gender and occupation for a user). Embeddings are L2-normalised and the logits divided by a temperature.

## In-batch softmax and its bias

A softmax over millions of items is out of the question, so the other items in a batch serve as negatives: a 512-batch gives a 512 by 512 score matrix with positives on the diagonal, and cross-entropy over each row. But items enter a batch in proportion to how often they appear, so popular items are the most frequent negatives and get pushed down for being common, not for being a poor match.

**logQ correction** (importance sampling): subtract the log of each candidate's sampling probability from its logit during training, `s_c(x, y_j) = s(x, y_j) - log p_j`. Apply it only in training, not at serving. Also mask duplicates of the positive in the batch so they are not treated as negatives. On a 5.3-million-page corpus the original report had Recall@10 rise from 0.0643 to 0.1065 with the correction at temperature 0.07; the exact derivation is still being argued.

## Measured on the film split

| Model | Recall | NDCG | Coverage |
|---|---:|---:|---:|
| Popularity | 0.0900 | 0.0752 | 0.0446 |
| EASE | 0.1550 | 0.1259 | 0.2235 |
| Two-tower, plain in-batch | 0.0532 | 0.0382 | 0.8591 |
| Two-tower, logQ corrected | 0.1413 | 0.1095 | 0.3062 |

One line moved the tower from below popularity to near EASE. The uncorrected model's 0.8591 coverage shows the bias: it spreads recommendations over most of the catalogue because it learned that being popular is bad. Temperature mattered (validation NDCG 0.1122 at 0.10, 0.1258 at 0.20, 0.1134 at 0.50). A batch of 2048 scored worse than 128 or 512 (0.1001 against 0.1304 and 0.1258) at a fixed epoch count, plausibly from fewer gradient steps, which that run did not separate. EASE still wins on a small catalogue ([[EASE and Item-Based Neighbourhood Recommenders]]); brute-force scoring of 943 users against 1,682 items took 0.001 s, so no index was needed there, while at millions of items an ANN index loses some recall that should be reported separately from the model's (brute force first, then the index).

## Cold start

Hide 10% of films from training, drop item ids at random (probability 0.3) so the network learns to use features, always drop them for hidden items, then rank only hidden films. Among 340 users with a hidden-item positive: tower on features only recall 0.220 / NDCG 0.116; random 0.082 / 0.039; EASE 0.079 / 0.039 (its score for an unseen item is zero, leaving only the random tiebreak). This is the reason to accept the tower's complexity. Richer content such as a text embedding would fill the same slot.

## Pitfalls

- Forgetting logQ, or applying it at serving.
- Duplicates of the positive left in the batch as negatives.
- Cross-features in a tower.
- Features computed today rather than as at event time leak the future.

## See Also
- [[RMSE vs Top-N Ranking in Recommenders]] — prerequisite-for
- [[Implicit Feedback: iALS and BPR]] — prerequisite-for
- [[Sampled Ranking Metrics and MRR]] — related
- [[Hard-Negative Mining and Measuring What It Fixes]] — extends (negatives beyond the batch)
