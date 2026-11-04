---
title: "Clustering Algorithms: k-means, Agglomerative and DBSCAN"
tags: [foundations, comparison]
summary: "k-means needs round similar clusters, agglomerative gives a dendrogram without prediction, DBSCAN finds arbitrary shapes and noise; with no ground truth, inspect the clusters."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--05-unsupervised-learning.md
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

## See Also
- [[Choosing k and Naming Clusters Honestly]] — extends
- [[Clustering Categorical and Mixed Data]] — extends
- [[Clustering Validation Against Named Baselines]] — related
- [[Expectation-Maximisation for Gaussian Mixtures]] — related
- [[Isolation Forest vs Gaussian Anomaly Detection]] — related
