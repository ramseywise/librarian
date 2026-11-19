---
title: "t-SNE and UMAP Visualisation Rules"
tags: [data-science, concept]
summary: "t-SNE preserves neighbourhoods for 2-D pictures only; read cluster shape not size or distance, vary perplexity, and never feed it to a model."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--05-unsupervised-learning.md
  - data/raw/papers/2026-11-07-mcinnes-2018-umap.md
---

# t-SNE and UMAP Visualisation Rules

t-SNE finds a 2-D layout that keeps neighbourhoods: points close in the original space stay close. It has no `transform`, so it cannot map new points. On the 8x8 digits, k-means with 10 clusters on the 2-D picture reaches adjusted Rand index 0.39 for a PCA projection and 0.89 for t-SNE against the true digit, without t-SNE seeing labels.

Rules for reading a plot:

- Cluster sizes and distances between clusters mean little; use it to look, never to measure.
- Run more than one `perplexity`; conclusions about how far apart two groups are change with it.
- Never use it as features for a model.

The common failure is reading distances: a conclusion about how far apart two groups sit changes with `perplexity`. The fix is to rerun with other settings and treat the plot as a way to look, not to measure.

On the digits, a PCA 2-D projection overlaps most classes while t-SNE separates nearly all ten without seeing labels. That is why it suits inspection of neighbourhood structure, and why the picture alone is not evidence of how many groups exist.

UMAP belongs to the neighbour-graph family and usually runs faster. The UMAP paper (self-reported) gives 87 seconds on MNIST for single-core UMAP against 1,450 for MulticoreTSNE; the course note's laptop timings add 292 for multi-core FIt-SNE and, on the 8x8 digits, 9 against 17 for Barnes-Hut. Its better global-structure preservation is hedged ("arguably") and attributed to its initialisation and objective; using it for later clustering or anomaly detection is proposed, not evaluated, and mapping new points is left as future work. The paper's own accuracy results are mixed (kNN accuracy on the embedding below t-SNE's on Fashion-MNIST at small k), and its authors concede that t-SNE started from the same layout can match UMAP on one global-structure measure. How the graph is built and laid out is on [[UMAP Graph Construction and Layout]]. See [[PCA, NMF and Low-Rank Factorisation]] for the linear alternative.

## Limits

The UMAP paper has no ablation, does not state the hyper-parameters behind its quality and runtime tables, and compares single-core UMAP with C++ baselines on different machines per experiment; its authors note there is no clear objective measure of global structure. Details are on the construction page.

## Check

- Was the plot rerun with more than one `perplexity`?
- Is the claim about shape and neighbourhood, not size or distance?

## See Also
- [[PCA, NMF and Low-Rank Factorisation]] — alternative-to
- [[UMAP Graph Construction and Layout]] — extends
- [[Clustering Algorithms: k-means, Agglomerative and DBSCAN]] — related
