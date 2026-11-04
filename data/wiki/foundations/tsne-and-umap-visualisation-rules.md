---
title: "t-SNE and UMAP Visualisation Rules"
tags: [foundations, concept]
summary: "t-SNE preserves neighbourhoods for 2-D pictures only; read cluster shape not size or distance, vary perplexity, and never feed it to a model."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--05-unsupervised-learning.md
---

# t-SNE and UMAP Visualisation Rules

t-SNE finds a 2-D layout that keeps neighbourhoods: points close in the original space stay close. It has no `transform`, so it cannot map new points. On the 8x8 digits, k-means with 10 clusters on the 2-D picture reaches adjusted Rand index 0.39 for a PCA projection and 0.89 for t-SNE against the true digit, without t-SNE seeing labels.

Rules for reading a plot:
- Cluster sizes and distances between clusters mean little; use it to look, never to measure.
- Run more than one `perplexity`; conclusions can change with it.
- Never use it as features for a model.

UMAP is from the same family of neighbour-graph methods and usually faster. In the authors' one-figure laptop timings, single-core UMAP took 87 seconds on MNIST against 292 for multi-core FIt-SNE and 1,450 for Barnes-Hut t-SNE, but on the 8x8 digits 9 against 17 for Barnes-Hut. Its better global-structure preservation is hedged ("arguably") and attributed to its initialisation and objective; using it for later clustering or anomaly detection is proposed, not evaluated, and mapping new points is left as future work. See [[PCA, NMF and Low-Rank Factorisation]] for the linear alternative.

## See Also
- [[PCA, NMF and Low-Rank Factorisation]] — alternative-to
- [[Clustering Algorithms: k-means, Agglomerative and DBSCAN]] — related
