---
title: "Validating Clusters Without Labels"
tags: [data-science, classical-ml, pattern]
summary: "Internal indices, stability and classifier accuracy all look good on data with no groups, so compare every one against a shuffled-column control and validate on outcomes from outside the data."
updated: 2026-11-20
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--05b-clustering-categorical-and-mixed-data.md
  - data/raw/papers/2026-11-08-intro-to-ml-with-python-ch03-unsupervised-learning-preprocessing.md
  - data/raw/papers/2026-11-08-islp-ch12-unsupervised-learning.md
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

## A textbook cross-check on named datasets

Müller and Guido compare two identical clusterings with swapped label names (`[0,0,1,1,0]` against `[1,1,0,0,1]`): accuracy is 0.00 and the adjusted Rand index is 1.00, so with ground truth they advise ARI or NMI rather than accuracy. On 200 two-moons points (noise 0.05, scaled) silhouette prefers k-means to DBSCAN even though DBSCAN gives the intuitive clustering. On the 2,063 face images, 10-cluster k-means and Ward agglomerative partitions of 100 whitened PCA components agree at ARI 0.13, and the dendrogram shows no natural cut-off. They conclude that, with no labels, reading the clusters by hand is the only way to learn whether they mean anything.

## Limits

- The textbook calls silhouette often poor in practice, develops no other label-free metric (no elbow, gap statistic or UMAP), and says robustness-based metrics were not in scikit-learn at the time.
- It gives the ARI and silhouette scores for two-moons only in figure titles, uses single runs, and its scikit-learn code is 2016-era.
- ISLP's chapter 12 offers no accepted way to validate a clustering, notes that results are not robust to dropping observations, and forces every point into a cluster.

## See Also
- [[Choosing k and Naming Clusters Honestly]] — related
- [[Clustering Validation Against Named Baselines]] — related
- [[Clustering Categorical and Mixed Data]] — related
- [[RFM Segmentation Validated on a Holdout]] — related
- [[Clustering Stability and Symmetry]] — related (when resampling stability is and is not informative)
