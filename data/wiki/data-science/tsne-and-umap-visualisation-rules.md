---
title: "t-SNE and UMAP Visualisation Rules"
tags: [data-science, classical-ml, concept]
summary: "t-SNE preserves neighbourhoods for 2-D pictures only; read cluster shape not size or distance, vary perplexity, and never feed it to a model."
updated: 2026-11-20
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--05-unsupervised-learning.md
  - data/raw/papers/2026-11-07-mcinnes-2018-umap.md
  - data/raw/papers/2026-11-08-chari-2023-specious-art-single-cell.md
  - data/raw/papers/2026-11-08-intro-to-ml-with-python-ch03-unsupervised-learning-preprocessing.md
---

# t-SNE and UMAP Visualisation Rules

t-SNE finds a 2-D layout that keeps neighbourhoods: points close in the original space stay close. It has no `transform`, so it cannot map new points. On the 8x8 digits, k-means with 10 clusters on the 2-D picture reaches adjusted Rand index 0.39 for a PCA projection and 0.89 for t-SNE against the true digit, without t-SNE seeing labels.

Rules for reading a plot:

- Cluster sizes and distances between clusters mean little; use it to look, never to measure.
- Run more than one `perplexity`; conclusions about how far apart two groups are change with it.
- Never use it as features for a model.

The common failure is reading distances: a conclusion about how far apart two groups sit changes with `perplexity`. The fix is to rerun with other settings and treat the plot as a way to look, not to measure.

On the digits (the scikit-learn digits set of 8x8 images, with t-SNE seeded at 42 and left at default perplexity, against a two-component PCA), a PCA 2-D projection overlaps most classes while t-SNE pulls apart nearly all ten although it never sees the labels. In the PCA plot only zero, six and four are relatively separated. That is why it suits inspection of neighbourhood structure, and why the picture alone is not evidence of how many groups exist.

UMAP belongs to the neighbour-graph family and usually runs faster. The UMAP paper (self-reported) gives 87 seconds on MNIST for single-core UMAP against 1,450 for MulticoreTSNE; the course note's laptop timings add 292 for multi-core FIt-SNE and, on the 8x8 digits, 9 against 17 for Barnes-Hut. Its better global-structure preservation is hedged ("arguably") and attributed to its initialisation and objective; using it for later clustering or anomaly detection is proposed, not evaluated, and mapping new points is left as future work. The paper's own accuracy results are mixed (kNN accuracy on the embedding below t-SNE's on Fashion-MNIST at small k), and its authors concede that t-SNE started from the same layout can match UMAP on one global-structure measure. How the graph is built and laid out is on [[UMAP Graph Construction and Layout]]. See [[PCA, NMF and Low-Rank Factorisation]] for the linear alternative.

## Limits

The single-cell evidence concerns RNA-seq data only; carrying it to other data is an inference. Methods and most supporting figures are in a supplement the extraction did not have, the paper is a perspective with no significance tests in its main text, and the authors concede 2-D embeddings can reflect broader strokes such as cell-type inter-distances. Its distance-preservation theory (Johnson-Lindenstrauss, O(sqrt n)) concerns distances while t-SNE and UMAP aim mainly at local structure.

The scikit-learn course example dates from 2016, and its t-SNE defaults (perplexity, initialisation, learning rate) have since changed, so the code needs updating before a rerun.

The UMAP paper has no ablation, does not state the hyper-parameters behind its quality and runtime tables, and compares single-core UMAP with C++ baselines on different machines per experiment; its authors note there is no clear objective measure of global structure. Details are on the construction page.

## What argues against it

Chari and Pachter re-analysed public single-cell RNA-seq datasets (cells reduced to 50 PCA dimensions, then to 2-D t-SNE or UMAP) and measured the distortion. The page's claims that t-SNE keeps neighbourhoods and that cluster shape can be read from a plot meet this evidence:

- The mean Jaccard distance between 30-nearest-neighbour sets in the 2-D embedding and in the original (ambient) space was above 0.7 across the datasets (L2 distance, k = 30); the extraction notes local overlap was poor, not only global structure.
- Neighbour ranking of cell types correlated with the ambient ranking at 0.4 or below, at least 33% lower than for the PCA spaces.
- Reduction to 2-D can narrow or widen the gap between within-type and between-type distance distributions depending on the dataset, so separation seen in a plot is not reliable.
- Changing n_neighbors (UMAP) or perplexity (t-SNE) from 5 to 50 created and removed condition-specific populations in one embryo dataset.
- Predicting a cell's label from its neighbours did worse on the 2-D coordinates than on higher-dimensional ones, supervised UMAP included (30% held out, 50 nearest neighbours).
- Max-to-min distance ratios rose 4- to 200-fold against PCA or ambient space (measured on the E10.5 ex utero and in utero embryo data and the 10x VMH neurons; groups of equidistant cells and groups of nearest neighbours).

Their advice is to treat the plots as cartoon diagrams shown after the analysis, never for quantitative claims about distance, density, mixing or trajectories, and to cluster in the PCA or ambient space, not on 2-D coordinates. This sits against the digits result above, where k-means on the 2-D t-SNE picture recovered the digits; the two use different data and the wiki has not reconciled them.

## Check

- Was the plot rerun with more than one `perplexity`?
- Is the claim about shape and neighbourhood, not size or distance?

## See Also
- [[PCA, NMF and Low-Rank Factorisation]] — alternative-to
- [[UMAP Graph Construction and Layout]] — extends
- [[Clustering Algorithms: k-means, Agglomerative and DBSCAN]] — related
