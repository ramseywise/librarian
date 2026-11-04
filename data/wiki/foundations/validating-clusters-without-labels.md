---
title: "Validating Clusters Without Labels"
tags: [foundations, pattern]
summary: "Internal indices, stability and classifier accuracy all look good on data with no groups, so compare every one against a shuffled-column control and validate on outcomes from outside the data."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--05b-clustering-categorical-and-mixed-data.md
---

# Validating Clusters Without Labels

## Internal indices need a control

Silhouette; Calinski-Harabasz (between over within spread, higher better); Davies-Bouldin (lower better). In scikit-learn only silhouette accepts a precomputed matrix, so CH and DB are unavailable on Gower distances. True k is 4 in the test table:

| k | Silhouette (groups / control) | CH | DB |
|---|---|---|---|
| 2 | 0.216 / 0.121 | 329 / 125 | 1.653 / 2.919 |
| 4 | 0.243 / 0.110 | 277 / 117 | 1.534 / 2.264 |
| 6 | 0.254 / 0.129 | 232 / 120 | 1.472 / 1.866 |

No index picks 4 (silhouette says 6, CH 2, DB 5), and DB improves steadily with k on the control. One comparison of 30 indices on numeric data found silhouette best overall with no index winning everywhere. The message is in the gap between data and control, not the peak.

## Stability is not validity

Agreement (ARI) between fits on two overlapping 80% subsamples: FAMD with k-means 0.963 on data and 0.257 on control; Gower with PAM 0.802 and 0.304. Gower with PAM is stable at 0.802 while recovering truth at 0.263. Stability says you would get the same answer again, not the right one.

## Explaining segments is not proof

A boosted tree predicting the cluster labels, read with SHAP, describes segments well but validates nothing: 3-fold accuracy 0.958 with groups and 0.913 with none, with a confident ranking of columns either way, because the clustering carved regions the columns predict. Likewise "segments differ on revenue, p < 0.001" is near guaranteed since the clustering made them differ; classical tests between estimated clusters have an extremely inflated false-positive rate (a correction exists for hierarchical clustering of normal data only), so report such differences as description. A real test: split first, cluster the training part, transfer labels to held-out rows with a classifier, cluster the held-out rows independently and compare. The check that matters most comes from outside the data: do the segments predict something later, on customers or periods not used to fit them, better than a one-line rule?

## See Also
- [[Choosing k and Naming Clusters Honestly]] — related
- [[Clustering Validation Against Named Baselines]] — related
- [[Clustering Categorical and Mixed Data]] — related
- [[RFM Segmentation Validated on a Holdout]] — related
