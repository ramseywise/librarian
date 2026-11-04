---
title: "Isolation Forest vs Gaussian Anomaly Detection"
tags: [foundations, comparison]
summary: "A per-feature Gaussian scores how likely a point is, an isolation forest how easy it is to cut off; pick by the shape of normal data, and irrelevant columns wreck the forest."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--05-unsupervised-learning.md
---

# Isolation Forest vs Gaussian Anomaly Detection

## Gaussian density

Model normal behaviour with a Gaussian per feature and flag points with low density. Train on unlabelled normal data; choose the threshold epsilon on a labelled validation set by F1 (accuracy is useless as anomalies are rare). On a server latency/throughput set: epsilon 9.00e-05, F1 0.875, 6 of 307 flagged. Use density estimation when positives are very few and future anomalies may look unlike past ones; use a classifier when there are many positives of a stable kind.

## Isolation forest

Anomalies are few and different, so random splitting separates them fast. Each tree picks a random column and split value until each point is alone; a point's path length is the number of splits; short average paths mean anomalies. Score = 2 to the power of minus (average path length divided by the average for n points), near 1 for anomalies. Defaults: 100 trees on 256 sampled rows each. It models no density.

## Head to head

On the server data there is no winner: AUC 0.870 Gaussian vs 0.878 forest, both best F1 0.875; forest AUC across five seeds ranges 0.870 to 0.887, wider than the gap, with nine anomalies. A round cloud in two columns is what a Gaussian is built for. On tables that break its assumptions (normal rows in two regimes across six columns, mean AUC over five seeds):

| Detector | Far-out anomaly | Anomaly in the valley between regimes |
|---|---|---|
| Gaussian per feature | 0.935 | 0.000 |
| Gaussian, full covariance | 1.000 | 0.001 |
| Isolation forest | 0.929 | 1.000 |

AUC 0.000 is the worst possible: the valley sits near the overall mean, so a single Gaussian rates those points most normal. With one column on an exponential scale, full Gaussian 0.493 against forest 0.952. The forest is not simply better: full-covariance Gaussian wins on far-out anomalies. Pick by the shape of normal data; a skewed column (an amount) is the other common break.

## Two limits

- **Fewer rows per tree can be better.** Clumped anomalies mask each other with more rows: AUC 1.000 at 16 rows, 0.998 at 256, 0.969 at 1024, 0.928 at 4096.
- **Irrelevant columns hurt badly.** Each split picks a column at random, so noise columns waste splits: mean AUC 0.965 with none, 0.844 with 6, 0.616 with 20, 0.489 with 60 (chance), while the per-feature Gaussian stays near 0.5. On wide tables choose columns first. Against another detector the forest won on one dataset and lost on two others, so it is not one-sided.

Other scikit-learn detectors: `EllipticEnvelope`, `LocalOutlierFactor`, `OneClassSVM`.

## See Also
- [[Classification Metrics, Confusion Matrix and Thresholds]] — related
- [[Clustering Algorithms: k-means, Agglomerative and DBSCAN]] — related
- [[Population Stability Index]] — related
