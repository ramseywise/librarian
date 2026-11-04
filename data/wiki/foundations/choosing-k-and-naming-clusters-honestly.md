---
title: "Choosing k and Naming Clusters Honestly"
tags: [foundations, pattern]
summary: "Scale and choose features before clustering, expect BIC, silhouette and seed agreement to disagree on k, shuffle columns as a null check, and only name clusters that survive reseeding."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--05-unsupervised-learning.md
---

# Choosing k and Naming Clusters Honestly

Worked case: clustering 2,182 tracks of one person's music library (nine audio features plus genre-map position and a hand-built eight-group taxonomy) to narrow candidates before a per-playlist ranker.

## Features decide what clusters mean

Unscaled, milliseconds of duration are the clustering: ARI with duration-only clusters 0.988 raw, 0.072 scaled. Scaling is not enough. A matrix adding 24 key and 8 decade one-hots has 9,407 parameters at full covariance for 2,182 rows; its clusters explain 3.1% of audio variance (0.357 for the nine audio features alone) and mostly sort by decade (NMI 0.714 vs 0.039).

## The criteria disagree on k

| k | BIC | k-means silhouette | GMM silhouette | Seed agreement ARI | Smallest cluster |
|---|---|---|---|---|---|
| 2 | 44389 | 0.258 | 0.086 | 0.999 | 830 |
| 3 | 40616 | 0.236 | 0.118 | 0.582 | 339 |
| 8 | 30825 | 0.191 | 0.032 | 0.718 | 92 |
| 11 | 30323 | 0.182 | 0.040 | 0.637 | 49 |
| 13 | 30356 | 0.177 | 0.027 | 0.610 | 11 |

BIC is lowest at 11 (11 to 13 within seed noise); silhouette peaks at 2 or 3 and favours k-means over a mixture's ellipses by construction; seed agreement is highest at 2. A k of 8 chosen to match eight taxonomy groups is a product reason, not a measurement, and should be stated as one. **Shuffle each column separately** to destroy real groups as a null: silhouette fell from 0.258 to 0.107 (so there is some structure), yet BIC still picked k=7, probably spending components on skewed features. A BIC minimum does not show groups exist.

## Soft assignment

Median top posterior 0.992 sits beside seed agreement 0.718: a posterior is confidence inside one fitted model, not evidence it is right. As a candidate filter, keeping any cluster with posterior at least 0.05 finds 92.5% of held-out playlist members but keeps 62% of the library; hard GMM (recall 0.457) loses to plain k-means (0.536).

## Naming

Name from the features, use the taxonomy as evidence, and only name clusters whose median Jaccard after matching across 10 seeds is at least 0.75 (a rough resampling mark, not a theorem; a stable cluster can still be meaningless). Three clusters passed (Jaccard 0.908, 0.844, 0.767), five were left unnamed (0.207 to 0.745). A cluster called "ambient" would be a false name when 62% of it is something else.

## Ranker lessons

Binary model per playlist (26 playlists, five-fold twice, scaler and mixture refit per training fold): AUC 0.870 and P@10 0.397 against a 0.038 base rate, but non-members are tracks in other playlists, so it measures filing, not taste. Cluster posteriors add nothing (AUC change -0.001); the proxy columns beat audio by 0.050. A feature that is the mean audio of a track's playlist leaks to AUC 1.000. Zero meaning "not on the map" (266 tracks) must be treated as missing. A previously recorded 0.954 AUC rebuilt to 0.947 on a smaller population: a check, not a reproduction.

## See Also
- [[Clustering Algorithms: k-means, Agglomerative and DBSCAN]] — prerequisite-for
- [[Clustering Validation Against Named Baselines]] — related
- [[Mixture Models and Label Switching]] — related
- [[Model Selection Criteria]] — related
