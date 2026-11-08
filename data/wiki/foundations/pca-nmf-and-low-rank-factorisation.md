---
title: "PCA, NMF and Low-Rank Factorisation"
tags: [foundations, concept]
summary: "PCA rotates to maximum-variance axes, NMF builds additive non-negative parts, collaborative filtering factorises a mostly missing matrix; scale before PCA."
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--05-unsupervised-learning.md
---

# PCA, NMF and Low-Rank Factorisation

With no labels there is no score saying the model did well, so unsupervised methods are mostly used for exploration and as preprocessing for a supervised model, where the downstream score gives feedback. Transformations give a new representation (fewer dimensions, interpretable parts, a 2-D picture); clustering partitions the data (see [[Clustering Algorithms: k-means, Agglomerative and DBSCAN]]).

## Scaling first

| Scaler | Result | Use when |
|---|---|---|
| `StandardScaler` | Mean 0, variance 1 | Default for SVMs, linear models, MLPs, PCA |
| `RobustScaler` | Median and IQR | Outliers |
| `MinMaxScaler` | Range [0, 1] | Bounded inputs needed |
| `Normalizer` | Each row to unit length | Only direction matters (cosine) |

Use the same fitted scaler on train and test; a second scaler fit on test displaces its points relative to training. On a kernel SVM for breast cancer: 0.63 unscaled, 0.97 min-max, 0.96 standard. Without scaling, PCA's first component is whichever feature has the biggest unit (except same-scale data such as pixels).

## PCA

PCA rotates the data so the first axis follows maximum variance, the second the maximum variance orthogonal to it, and so on; keep the first k. On scaled breast-cancer data (30 features), two components retain 0.443 and 0.19 of the variance. Computing it from the SVD of the covariance matrix, 17 components retain 99% of variance, and the directions agree with scikit-learn up to sign. Components mix all features with positive and negative weights, so they are hard to interpret.

As feature extraction: on a face-image set (5,655 pixels per image), 1-nearest-neighbour scores 0.23 on raw pixels and 0.31 after `PCA(100, whiten=True)`, because distances between component vectors measure face similarity better than pixel distances.

## NMF

Like PCA but components and coefficients are non-negative, so the data must be too (pixels, word counts, spectra). The result is additive parts.

| | PCA | NMF |
|---|---|---|
| Components | Orthogonal, ordered by variance | Not ordered, all equally important |
| Signs | Mixed | Non-negative |
| Changing `n_components` | First components unchanged | All components change |
| Good for | Compression, decorrelation, visualisation | Interpretable parts, separating additive sources |

NMF over word counts is a topic model.

## Collaborative filtering

Learn a feature vector per movie and a preference vector per user so that their dot product predicts the rating, minimising squared error over observed entries only plus L2 penalties. On a ratings matrix of 1,682 movies by 943 users, 100,000 ratings are observed (6.3%). **Mean-normalise** each movie's ratings, otherwise a user with no ratings is predicted 0 for everything. This is low-rank matrix factorisation, the same idea as PCA and NMF fitted only on observed entries, and the ancestor of embedding models: a movie vector is a learned embedding.

## See Also
- [[t-SNE and UMAP Visualisation Rules]] — related
- [[Clustering Algorithms: k-means, Agglomerative and DBSCAN]] — related
- [[Regularisation as a Prior]] — related
- [[DoRA Weight-Decomposed Low-Rank Adaptation]] — related (low-rank updates to model weights)
