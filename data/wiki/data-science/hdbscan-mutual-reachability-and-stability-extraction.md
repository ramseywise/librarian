---
title: "HDBSCAN: Mutual Reachability and Stability Extraction"
tags: [data-science, concept]
summary: "HDBSCAN replaces DBSCAN's single epsilon with a hierarchy over mutual reachability distance and picks flat clusters by total stability; McInnes and Healy speed it up with tree-based neighbour search and a dual-tree minimum spanning tree."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-mcinnes-2017-accelerated-hierarchical-density-clustering.md
  - data/raw/papers/2026-11-08-mcinnes-2017-hdbscan-joss.md
---

# HDBSCAN: Mutual Reachability and Stability Extraction

The hdbscan library paper summarises HDBSCAN as DBSCAN run across a range of epsilon values, integrated to select the clustering that is most stable over epsilon. It asserts, with no measurement, that the method handles clusters of differing density and is less sensitive than DBSCAN to parameter choice. The package also ships Robust Single Linkage, GLOSH outlier scores, exploration and plotting tools, prediction, and soft clustering. The algorithm credit goes to Campello and colleagues; the library paper presents no new method.

## The pipeline

McInnes and Healy ask whether HDBSCAN* can approach N log N average run-time without giving up density variation or the freedom from an epsilon parameter. The steps are:

1. **Core distance.** For each point, the distance to its kth nearest neighbour.
2. **Mutual reachability distance.** For two points, the larger of their two core distances and their distance apart.
3. **Spanning tree.** Build the minimum spanning tree of the mutual-reachability graph.
4. **Hierarchy.** Sort the edges, then build a single-linkage tree with union-find, then condense it using a minimum cluster size m: a child with fewer than m points is a spurious split, and its points fall out of the parent.
5. **Extraction.** A cluster's stability is the sum over its points of the range of lambda (1 over epsilon) for which the point belongs to it. The flat clustering maximises total stability without overlapping clusters.

HDBSCAN is clustering, not partitioning: it need not assign every point.

## What the acceleration changes

The original has O(N^2) steps, namely core distances and the spanning tree. The accelerated version takes core distances from kd-tree or ball-tree neighbour queries and the spanning tree from a Dual-Tree Boruvka algorithm adapted to mutual reachability, with core-distance filtering and a tie-handling trick that makes the tree approximate. The authors argue, with no strict bound, that average cost approaches O(N log N), depending on the data and the tree.

Reported timings (self-reported, run-time only, synthetic data, a 3.1 GHz i7 laptop with 8 GB):

- Roughly 100 times quicker than the Java reference implementation on 200,000 points, whether 2-d or 50-d.
- With scikit-learn v0.18.1 default settings, K-Means, DBSCAN and HDBSCAN* were the quickest trio and hard to separate, while Affinity Propagation, Spectral Clustering and Mean Shift slowed badly past a few thousand points.
- Run-time comparable to scikit-learn DBSCAN on Gaussian-ball mixtures, where DBSCAN's epsilon and k were tuned by a Gaussian-process search that maximised its adjusted Rand index against the HDBSCAN* output.

## Limits

- Run-time only: clustering quality is not evaluated, and is deferred to earlier HDBSCAN* papers.
- Only synthetic Gaussian mixtures were benchmarked; real data and noisy background are left for later.
- Comparing against a Java reference mixes implementation with algorithm.
- The tie-handling trick gives an approximate tree; the authors say the effect is small after condensing and worst for high-dimensional kd and ball trees.
- The implementation is serial and lacks cover trees, which limits scaling with dimension; the HDBSCAN k and m used in the benchmarks are not stated.
- DBSCAN received parameters tuned to match, something a user could not know beforehand (the authors say so).
- The library paper has no benchmarks, complexity or parameter guidance (min_cluster_size, min_samples).

## See Also
- [[HDBSCAN with KMeans Fallback]] — extends
- [[Embedding Clustering and Anomaly Detection]] — related (HDBSCAN after a UMAP reduction)
- [[Clustering Algorithms: k-means, Agglomerative and DBSCAN]] — alternative-to (DBSCAN, with a fixed epsilon)
