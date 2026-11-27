---
title: "PCA, NMF and Low-Rank Factorisation"
tags: [data-science, classical-ml, concept]
summary: "PCA rotates to maximum-variance axes, NMF builds additive non-negative parts, collaborative filtering factorises a mostly missing matrix; scale before PCA."
updated: 2026-11-20
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--05-unsupervised-learning.md
  - data/raw/papers/2026-11-08-intro-to-ml-with-python-ch03-unsupervised-learning-preprocessing.md
  - data/raw/papers/2026-11-08-practical-statistics-for-data-scientists-ch07-unsupervised-learning.md
  - data/raw/papers/2026-11-08-islp-ch12-unsupervised-learning.md
  - data/raw/papers/2026-11-08-python-data-science-handbook-ch05-machine-learning.md
  - data/raw/papers/2026-11-08-islp-ch06-linear-model-selection-regularization.md
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

Use the same fitted scaler on train and test; a second scaler fit on test displaces its points relative to training. On a kernel SVM for breast cancer (`SVC(C=100)`, split `random_state=0`, scalers fit on the training part only): 0.63 unscaled, 0.97 min-max, 0.96 standard. The scaled test set's minimum and maximum are not exactly 0 and 1, because the training transform is reused. Without scaling, PCA's leading component is dominated by the highest-variance feature (on USArrests, Assault, with variance 6,945.16 against 18.97 to 209.5 for the others; same-scale data such as pixels excepted).

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

## Faces and mixed signals in the textbook

Müller and Guido run 1-nearest-neighbour on the Labeled Faces in the Wild images (people with at least 20 images, capped at 50 each: 2,063 images of 62 people, 1,537 in a stratified training split). Raw pixels give 26.6% test accuracy against about 1.5% chance, and 100 whitened PCA components fit on the training part give 35.7%.

On synthetic data (three source signals of 2,000 time steps mixed into 100 measured signals), `NMF(n_components=3)` recovers the three sources while `PCA(n_components=3)` does not, concentrating most of the variance in component one. The authors advise NMF for additive data such as audio, gene expression and text, with a fixed `random_state`, and whitened PCA before distance-based classifiers.

## Stock returns and choosing components (Practical Statistics for Data Scientists)

In the book's R worked example on S&P 500 daily returns, for the two oil stocks CVX and XOM, the leading component of the PCA works out close to the mean of both. In a later PCA on 18 stocks from 2005 that includes GOOGL and AMZN, run on unscaled data, the first two components are almost entirely those two stocks (PC1 loadings 0.781 and 0.593). The authors note that standardising to z-scores amounts to running PCA on the correlation matrix rather than the covariance matrix.

They list four ways to pick the number of components: a screeplot, a cumulative-variance cut-off such as 80%, whether the loadings can be interpreted, and cross-validation. When one or two variables dominate the loadings, they say to keep them as they are, rescale them, or drop them and treat them separately, with no single correct choice.

## PVE, scaling and digits (ISLP, Python Data Science Handbook)

On USArrests (50 states, 4 variables) scaled to unit variance, the first component explains 62.0% of the variance and the second 24.7%, almost 87% together, with first-component loadings of 0.54, 0.58 and 0.54 on the three crime variables and 0.28 on urban population. Unscaled, the variances are 18.97, 87.73, 6,945.16 and 209.5, and the first component loads almost entirely on Assault, the variable with the largest variance. On NCI60 (64 cell lines by 6,830 genes) the first seven components explain about 40% of the variance. The authors read the number of components to keep off the scree plot by eye and give no formal rule. In ISLP's chapter 6 Hitters data, PCA on standardised predictors gives 38.31% of variance for one component, 60.15% for two and 88.63% for six.

In the digits data, read from a figure, the first 10 components hold about 75% of the variance and about 20 hold 90%. Keeping components that explain 50% of variance on digits with Gaussian noise (sigma 4, seed 42) retains 12 components. On the LFW faces (1,348 images, 2,914 pixels each), the first 150 components just exceed 90%, while the larger set of 2,370 images (at least 30 per person) needs nearly 100.

## Limits

- The face accuracies above (0.23 and 0.31) come from a course note whose setup is not matched to the chapter's 26.6% and 35.7%.
- The chapter gives the image shape as 87 by 65 in one place and 50 by 37 in the text on components (the component array has 5,655 columns, which is 87 times 65).
- It uses single splits, and its 2016 scikit-learn API has since changed. Sparse coding, ICA and factor analysis are only pointed to.
- The stock-return results are single worked examples in R (`princomp`), with no repeats or error bars; the formulas in that chapter are images, not text.
- The digits variance figures are read from a plot, and the USArrests and NCI60 numbers are single analyses with the scree-plot choice made by eye.

## See Also
- [[t-SNE and UMAP Visualisation Rules]] — related
- [[Clustering Algorithms: k-means, Agglomerative and DBSCAN]] — related
- [[Regularisation as a Prior]] — related
- [[DoRA Weight-Decomposed Low-Rank Adaptation]] — related (low-rank updates to model weights)
- [[UMAP Graph Construction and Layout]] — alternative-to
- [[Matrix Completion by Iterated Low-Rank Fits]] — extends
