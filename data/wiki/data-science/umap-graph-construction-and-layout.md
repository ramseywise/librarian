---
title: "UMAP Graph Construction and Layout"
tags: [data-science, classical-ml, concept]
summary: "UMAP builds a weighted nearest-neighbour graph with a per-point connectivity offset, merges it with a fuzzy union, and lays it out by minimising edge-wise cross entropy; the paper reports it faster than t-SNE, with mixed accuracy results."
updated: 2026-11-20
sources:
  - data/raw/papers/2026-11-07-mcinnes-2018-umap.md
---

# UMAP Graph Construction and Layout

McInnes, Healy and Melville test a dimension reduction method grounded in Riemannian geometry and fuzzy simplicial sets against t-SNE on picture quality, retention of global structure, speed and freedom to choose the output dimension. The visualisation rules for reading such plots are on [[t-SNE and UMAP Visualisation Rules]]; this page is the construction.

## Construction

1. **Graph.** Build a weighted k-nearest-neighbour graph. Each point i gets a local-connectivity offset rho_i, the distance to its nearest neighbour, and each distance is taken net of that offset, which ties every point to some neighbour at full weight 1. A bandwidth sigma_i is found per point so that the edge weights sum to log2(k).
2. **Symmetrise.** Directed edge weights A are merged with the probabilistic t-conorm (A plus its transpose minus their elementwise product), read as the chance that either directed edge is present.
3. **Initialise** the layout spectrally.
4. **Optimise** the layout by SGD on the edge-wise fuzzy-set cross entropy, with edge sampling and negative sampling (the optimisation follows LargeVis).

Approximate neighbour search uses Nearest-Neighbor-Descent, whose empirical complexity the authors report as about O(N^1.14).

Two parameters carry the trade-offs. **n** (neighbours) sets the scale over which the manifold counts as roughly flat, trading fine detail for big-picture structure. **min-dist** sets how far apart nearby points should sit in the output, and the authors call it largely aesthetic. With the implementation's defaults the fitted curve has a near 1.929 and b near 0.7915, and setting both to 1 gives back the Student t kernel of t-SNE. Appendix C restates t-SNE and LargeVis as a graph-construction step plus a graph-layout step.

## Results (self-reported)

- **Speed.** Single-core UMAP was fastest on every Table 3 dataset except the small Pen digits set: MNIST (70000 x 784) in 87 s against 1450 s for MulticoreTSNE on a MacBook Pro (3.1 GHz i7, 8 GB). GoogleNews subsampled to 200,000 x 300 with cosine distance took 361 s against 16906 s.
- **Scale.** The full 3 million GoogleNews vectors took about 200 minutes with UMAP against several days for MulticoreTSNE, on a Xeon E5-2697v4 server with 512 GB. A set of 30,000,000 sparse binary prime-divisibility vectors, roughly 1.8 million dimensions each, took about 2 weeks on a large-memory SMP machine.
- **kNN-classifier accuracy on the embedding.** COIL-20 at k = 160: UMAP much higher than t-SNE, though t-SNE was slightly higher at k = 10 (10-fold stratified CV). Shuttle at k = 3200 (10-fold CV): UMAP far higher than t-SNE and LargeVis. MNIST (20-fold CV): 0.967 for both at k = 100, 0.964 against 0.946 at k = 3200. PenDigits (10-fold stratified CV): 0.973 against 0.977 at k = 10. Fashion-MNIST (20-fold CV): UMAP below t-SNE at small k (0.790 against 0.818 at k = 100), comparable only at large k.
- **Stability.** On flow cytometry (1M points), embedding a 5% subsample with UMAP gave a smaller per-point Procrustes error against the full-data embedding than every t-SNE figure; t-SNE was run for 1500 iterations instead of 1000.

## Limits

- Kobak and Linderman found that t-SNE with a similar spectral-style start can equal UMAP on a global-structure measure, and the authors accept that the starting layout accounts for much of UMAP's global structure.
- The case for global structure rests on eyeballing plots and on kNN accuracy with a large k, and the authors say no clear objective measure of it exists.
- The paper has no ablation of components or hyper-parameters, and the settings of n, min-dist, n-epochs and embedding dimension behind its accuracy and timing tables are missing; baselines were tuned only where the authors could. No seed counts or repeat runs are reported for the accuracy figures.
- Timings pit single-core UMAP against optimised C++ baselines, and the machine changes between experiments. Table 3 mixes subsampled with PCA-reduced data, and two of its sizes contradict the text: scRNA is 20,921 cells in the text and 21086 x 1000 in the table; Flow is 10% of 1M in the text and 100000 x 17 in the table.
- Isomap did not complete on any dataset above COIL-20 in size, and on the GoogleNews vectors Laplacian Eigenmaps failed.
- The authors list as weaknesses: no PCA-style interpretability, possible spurious "constellation" structure in noise, topology traded against metric preservation, and suboptimal embeddings under about 500 samples (a claim with no experiment).

## See Also
- [[t-SNE and UMAP Visualisation Rules]] — prerequisite-for
- [[PCA, NMF and Low-Rank Factorisation]] — alternative-to (linear reduction)
- [[Embedding Clustering and Anomaly Detection]] — related (UMAP as the reduction step before clustering)
