---
title: "Clustering Algorithms: k-means, Agglomerative and DBSCAN"
tags: [programming, comparison]
summary: "k-means needs round similar clusters, agglomerative gives a dendrogram without prediction, DBSCAN finds arbitrary shapes and noise; with no ground truth, inspect the clusters."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--05-unsupervised-learning.md
  - data/raw/papers/2026-11-08-intro-to-ml-with-python-ch03-unsupervised-learning-preprocessing.md
  - data/raw/papers/2026-11-08-islp-ch12-unsupervised-learning.md
---

# Clustering Algorithms: k-means, Agglomerative and DBSCAN

| Algorithm | Specify | New points | Shapes | Noise |
|---|---|---|---|---|
| k-means | `n_clusters` | `predict` | Round, similar size | No |
| Agglomerative | `n_clusters` or distance cut | No | Depends on linkage | No |
| DBSCAN | `eps`, `min_samples` | No | Any | Yes |
| Gaussian mixture | `n_components` | `predict_proba` | Ellipses | Via low likelihood |

## k-means

Alternate: assign each point to the nearest centre; move each centre to the mean of its points. The default `init="k-means++"` spreads the first centres apart, and the seeding alone is provably O(log k)-competitive with the optimal clustering. Results depend on initialisation, hence `n_init`. It uses only distance to the centre, so it fails on stretched clusters, different densities and non-convex shapes. Uses beyond grouping: vector quantisation (cluster pixel colours into 16 colours, a 4-bit index instead of 24 bits per pixel) and feature expansion with many clusters (10 cluster distances make two interleaved moons linearly separable). Input must be coordinates; with only a distance matrix (journey sequences) use hierarchical clustering.

## Agglomerative

Start with every point alone and repeatedly merge the most similar pair. Linkage: `ward` (least increase in within-cluster variance, equal sizes, default), `average`, `complete` (smallest maximum distance), `single` (chains into one giant cluster). Long vertical lines in the dendrogram show merges of very different clusters, a natural cut.

## DBSCAN

A point with at least `min_samples` neighbours within `eps` is a core point; clusters are connected core points plus neighbours; the rest is noise (label -1). On two interleaved moons it finds 2 clusters with ARI 1.0 where k-means gets 0.5. It finds the number of clusters itself and flags outliers; `eps` is the hard parameter (too small, everything is noise; too large, one cluster) and is a distance, so scale first. `HDBSCAN` removes most of that sensitivity; see [[HDBSCAN with KMeans Fallback]].

## Evaluating without labels

| With ground truth | Without |
|---|---|
| Adjusted Rand Index, NMI: 1 same partition, about 0 random; ignore label names. Never accuracy, since cluster 0 vs label 0 is arbitrary | Silhouette (-1 to 1) favours round clusters: DBSCAN's correct moons get a worse silhouette than k-means's wrong ones. Check robustness to noise, parameters, subsampling |

The only reliable check is to inspect clusters by hand. On eigenface features, DBSCAN found one big cluster plus noise (faces with hats, open mouths, odd angles: an outlier detector), k-means gave blurred pose and lighting "average faces", agglomerative similar groups with less uniform sizes; none found identity.

## Textbook runs (Müller and Guido)

On 200 two-moons points (noise 0.05, standard-scaled), DBSCAN with the default `eps=0.5`, `min_samples=5` recovers the two moons; shrinking `eps` to 0.2 splits the data into eight clusters, and raising it to 0.7 merges it into one. The adjusted Rand index is about 0 for random assignment and 1 for DBSCAN, with k-means and two-cluster agglomerative scoring lower; silhouette prefers k-means.

On 2,063 face images (100 whitened PCA components), DBSCAN with defaults or `min_samples=3` labels everything noise; with `eps=15` and `min_samples=3` the result is a single cluster of 2,036 images plus 27 noise points; `eps=7` gives 2,006 noise points and 13 clusters of 3 to 9 points. It never yields more than one large cluster across `eps` 1 to 13. Ten-cluster k-means gives sizes 64 to 386 and Ward agglomerative gives 26 to 623, with ARI 0.13 between the two partitions, and the dendrogram shows no natural cut. scikit-learn's k-means runs 10 random initialisations by default and keeps the best (2016 version).

The authors advise scaling before choosing `eps` (which matters more than `min_samples`), watching for label -1 when indexing with cluster labels, using Ward linkage by default, switching to average or complete linkage if cluster sizes differ greatly, and `MiniBatchKMeans` for very large data.

## k-means restarts, linkage and NCI60 (ISLP)

K-means finds only a local optimum, so ISLP's lab runs it from many random starts. On simulated 50-by-2 data with two true clusters (the first 25 points shifted), K-means with K=3 and a single start gave inertia 78.06 against 75.04 with `n_init=20`, and they advise 20 or 50 restarts (`n_init`) and a fixed `random_state`. In a separate run on 150 simulated points in two dimensions (K=3, six random starts) the best objective was 235.8 while the other local optima scored 320.9 and 310.9. For hierarchical clustering they prefer average or complete linkage to single, and warn that centroid linkage can produce inversions. On NCI60 (64 cell lines by 6,830 genes), complete linkage cut at four clusters puts all the leukaemia lines together and spreads the breast cancer lines over three clusters; K-means with four clusters and 20 restarts agrees with it on only one nine-line cluster.

## Limits

- The numeric ARI values for k-means and agglomerative clustering on two moons appear only in figure titles in the chapter, so none is quoted here beyond the ordering.
- The chapter uses single runs, 2016-era API defaults (`KMeans` `n_init`, `fetch_lfw_people`) that have since changed, and notes it gives no citation for DBSCAN.
- The ISLP lab results are single runs on simulated data and one gene-expression set, and its clusterings are not robust to dropping observations.

## See Also
- [[Choosing k and Naming Clusters Honestly]] — extends
- [[Clustering Categorical and Mixed Data]] — extends
- [[Clustering Validation Against Named Baselines]] — related
- [[Expectation-Maximisation for Gaussian Mixtures]] — related
- [[Isolation Forest vs Gaussian Anomaly Detection]] — related
- [[Clustering Stability and Symmetry]] — extends (large-sample stability of k-means and spectral clustering)
- [[HDBSCAN: Mutual Reachability and Stability Extraction]] — extends (DBSCAN over varying epsilon)
