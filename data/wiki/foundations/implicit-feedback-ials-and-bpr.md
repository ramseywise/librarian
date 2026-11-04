---
title: "Implicit Feedback: iALS and BPR"
tags: [foundations, concept]
summary: "With clicks and plays there is no negative signal and counts measure confidence, not strength; iALS weights every cell in closed form and BPR optimises pairwise order, and a published alpha of 40 was the worst setting on other data."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--05-time-series-and-recommenders--notes--02-collaborative-filtering-and-matrix-factorisation.md
---

# Implicit Feedback: iALS and BPR

Most real data has no stars, only clicks, plays and purchases. Two things differ from ratings. There is **no negative signal**: not watching could mean disinterest or never having seen it. And the observation count measures **confidence** in a preference, not its strength. Rated items are also not a random sample: people choose what to watch and then what to rate, so empty cells carry taste information.

## iALS (implicit alternating least squares)

Binarise the target and weight each cell by confidence `c_ui = 1 + alpha * r_ui`. Every cell is now in the loss, including the empty ones, which sounds intractable but is not: alternating least squares has a closed form for each user given the items, and the empty cells collapse into one shared item Gram matrix (`Y^T Y`), computed once per sweep.

## BPR (Bayesian personalised ranking)

Rather than predict cell values, optimise order directly: for a user, a seen item should score above an unseen one. Sample (user, seen item, unseen item) triples and take a gradient step on each; the criterion relates to optimising AUC.

## Results and a warning

Same film split as [[RMSE vs Top-N Ranking in Recommenders]], positives only: iALS recall 0.1380 / NDCG 0.1117 / coverage 0.2515; BPR 0.1257 / 0.0992 / 0.3080; against EASE 0.1259 NDCG and item kNN 0.1140. Both factor models give more coverage than the linear ones, and the two simplest learned models led NDCG.

iALS validation NDCG over (alpha, reg): (1, 5) 0.1348; (10, 10) 0.1302; (40, 20) 0.1113; (40, 100) 0.1305. An alpha of 40 worked well in the original work, where r_ui counted how much of a programme was watched; here the input is binary and the same setting scored worst. A published hyperparameter is a fact about someone else's data, so grid-search it on your own.

## Choosing

- Explicit stars: biases and MF on observed cells, then still check top-N.
- Implicit events, catalogue up to tens of thousands: start with [[EASE and Item-Based Neighbourhood Recommenders]].
- Larger catalogue: iALS or BPR factors.
- Side features or cold start needed: [[Two-Tower Retrieval with logQ Correction]].

## See Also
- [[RMSE vs Top-N Ranking in Recommenders]] — prerequisite-for
- [[EASE and Item-Based Neighbourhood Recommenders]] — alternative-to
- [[Two-Tower Retrieval with logQ Correction]] — prerequisite-for
