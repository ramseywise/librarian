---
title: "Density Estimators: KDE Bandwidth, GMM Components and the Generative Classifier"
tags: [data-science, classical-ml, concept]
summary: "Kernel density estimation and Gaussian mixtures model a data distribution rather than predict a label; choose bandwidth or component count by held-out likelihood or AIC/BIC, and fit one density per class to get a Bayesian generative classifier."
updated: 2026-11-20
sources:
  - data/raw/papers/2026-11-08-python-data-science-handbook-ch05-machine-learning.md
---

# Density Estimators: KDE Bandwidth, GMM Components and the Generative Classifier

VanderPlas (*Python Data Science Handbook*, ch5) treats two estimators of a data distribution. **Kernel density estimation** (KDE) places one Gaussian component on every point, so it is essentially nonparametric. A **Gaussian mixture model** (GMM) fits a mixture of multidimensional Gaussians, found by expectation-maximisation. He advises using the GMM mainly as a density estimator and picking how many components to use with AIC, BIC or held-out likelihood.

## Choosing the knob

- **KDE bandwidth** is set by maximising held-out log-likelihood, with leave-one-out when the sample is small. On a 20-point bimodal sample (30% from N(0,1), the rest from N(5,1)), `GridSearchCV` over 100 bandwidths from 0.1 to 10 with leave-one-out picked 1.12.
- **GMM components:** on `make_moons(200, noise=.05)` with full covariance and 1 to 20 components, AIC favoured about 8 to 12 components and BIC a simpler model, so he concludes 16 was probably too many. On digits reduced by PCA to 41 dimensions (keeping 99% of variance, whitened), AIC over 50 to 200 components picked about 110.

## The generative classifier

Fit one KDE per class, store each class's log prior, score a new point under every class density, add the log priors and normalise. This is a Bayesian generative classifier; `predict` takes the argmax of `predict_proba`. On the 1,797 8x8 digits, searching bandwidth over 100 values from 1 to 100 gave 0.967 cross-validated accuracy at bandwidth 7.05, against 0.819 for Gaussian naive Bayes.

He uses the class to show the scikit-learn estimator pattern: subclass `BaseEstimator` and a mixin (`ClassifierMixin` here), have `__init__` only assign its named arguments, have `fit` return `self`, and end learned attributes with an underscore.

## Limits

- The 0.967 figure is the best score over the bandwidth search, not a held-out estimate. The chapter's accuracy figures come from one run each on small bundled datasets, with a single split and no intervals.
- The 0.819 naive Bayes comparison comes with no separate setup in the extraction.
- The code is 2016-era: `GMM` is now `GaussianMixture` and the `grid_search` and `cross_validation` modules are now `model_selection`.
- The chapter's Fig 5-17 caption says k-means where the code is a GMM. The chapter is explicitly not a comprehensive machine-learning introduction.

## See Also
- [[Expectation-Maximisation for Gaussian Mixtures]] — prerequisite-for
- [[Mixture Models and Label Switching]] — related
- [[Cross-Validation Variants and Nested Search]] — related (leave-one-out as a selection tool)
- [[Supervised Model Families and Complexity Knobs]] — related
