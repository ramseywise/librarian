---
title: HDBSCAN with KMeans Fallback
tags: [foundations, pattern]
summary: Clustering selection strategy that tries density-based HDBSCAN first and falls back to KMeans when silhouette drops below 0.25 — plus the diagnostic discipline that treats a fallback as a feature-quality signal rather than a resolved choice.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/atlas/skills/segment-analysis/SKILL.md
  - data/raw/claude-docs/atlas/skills/eval-report/SKILL.md
---

# HDBSCAN with KMeans Fallback

An algorithm-selection pattern for unsupervised segmentation: attempt density-based
clustering, and fall back to centroid-based clustering only when the density result scores
poorly. Implemented in `core/segmentation/algorithms.py::select_best()`.

## Why HDBSCAN first

HDBSCAN does not require `n_clusters` and can label points as noise, so it discovers cluster
count from the data and tolerates outliers. KMeans requires a `k` chosen in advance and
assigns every point to a cluster — including outliers, which distort centroids. Trying the
method with fewer assumptions first, and only falling back when it fails to find structure,
avoids baking in a `k` that was never validated.

## The fallback trigger

Fall back to KMeans when **silhouette < 0.25**. The same 0.25 is the pass threshold for
segment quality overall, alongside Davies-Bouldin ≤ 1.5 and a minimum cluster size of 3.

## The critical discipline: a fallback is a symptom

> If KMeans was used: investigate whether feature quality is the root cause (not just
> algorithm choice).

This is the part that's easy to skip. A silhouette below 0.25 usually means the *embedding*
has no cluster structure, not that HDBSCAN was the wrong algorithm — and KMeans will happily
produce k clusters from structureless data, converting a visible failure into an invisible
one. The fallback keeps the pipeline running; it does not mean the problem is solved.

## Diagnosing poor silhouette

| Root cause | Diagnostic | Fix |
|------------|-----------|-----|
| Too many features, noise | Check `CustomerProfile` feature count | Feature selection / PCA |
| Time-series without embedding | Embedder was skipped | `embed_tsfresh()` or `embed_chronos()` |
| Wrong `n_clusters` (KMeans) | Silhouette for k=2..10 | Grid over k |
| Outlier customers dominating | Check cluster size distribution | Raise HDBSCAN `min_cluster_size` |

Two of the four root causes are upstream of clustering entirely — feature count and a skipped
embedding step. This is why the "check feature quality" instruction is load-bearing: the
majority of silhouette failures are not clustering problems.

Cluster sizes below 3 are called out separately from the aggregate scores, because a good
mean silhouette can hide a degenerate two-point cluster.

## See Also
- [[Atlas Project]] — instance-of
- [[Track2Vec Playlist Co-Occurrence Embeddings]] — alternative-to
