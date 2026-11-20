---
title: Margin Classifiers, Hinge Loss and Kernel Smoothing
tags: [data-science, classical-ml, concept]
summary: "A support-vector classifier minimises hinge loss plus a ridge penalty and depends on the data only through inner products, so a kernel gives a nonlinear boundary at no extra cost; the same inner-product idea underlies string kernels and kernel smoothing."
updated: 2026-11-20
sources:
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch19-support-vector-machines-kernel-methods.md
---

# Margin Classifiers, Hinge Loss and Kernel Smoothing

Efron and Hastie (Computer Age Statistical Inference, ch. 19) ask how support-vector machines build a classifier directly through margins, how the kernel trick extends them to nonlinear boundaries, and where they sit relative to logistic regression, RKHS fitting and kernel smoothing.

## Margin, hinge loss and the kernel trick

The optimal separating hyperplane is the linear classifier with the largest margin between the classes. The soft-margin version allows margin violations xi_i with a total budget B, and the fit can also be written as minimising summed hinge loss plus a ridge penalty. The solution is a sum over the support set S, the points on the margin plus violators. Because the solution depends on the data only through inner products, a kernel (the inner product of two feature-mapped points) fits in a much larger feature space for free. The radial kernel exp(-gamma ||x - z||^2) is the usual practical choice; polynomial kernels are, in the authors' words, mainly useful as existence proofs. Any positive-semidefinite similarity measure can serve as a kernel for objects that are not vectors; a string kernel counts shared m-grams (3-grams over 20 amino acids mean 8,000 features, never built explicitly).

Computing through the n x n gram matrix costs O(n^2 p) rather than O(n p^2) for ridge regression on wide data (p much greater than n); support-vector fitting is linear in p but can be cubic in n, and in practice runs near n squared times the support-set size.

## Hinge versus logistic loss

At the population level, with two classes and equal costs, the hinge minimiser is the Bayes classifier and the binomial deviance minimiser is the logit of the class probability (derivation by Wahba et al. 2000). On separable data the direction of ridged logistic regression converges to the SVM direction as lambda goes to 0. The authors advise the SVM for separable data and logistic regression for overlapping classes, since it targets the logit of the class probability; they advise a soft margin even for separable data, with B (equivalently lambda) chosen by cross-validation, larger B giving more support points and lower variance. Swapping the ridge for a lasso penalty gives a sparse linear classifier (liblineaR).

Setup for the results below: single runs, no repetition.
- Leukemia gene expression (3571 genes, 72 patients, 47 ALL and 25 AML), optimal margin classifier without a kernel: 42 of 72 observations are support vectors. Fitted on a random 50 patients, all 22 held-out patients are classified correctly, even though they lie within the margin band.
- Protein classification (1708 proteins, 1663 negative and 45 positive, 3-gram string kernel, 10-fold cross-validated ROC, lambda chosen by CV): by AUC the kernel SVM outperforms kernel logistic regression.

## Kernel smoothing

The Nadaraya-Watson estimator is a kernel-weighted average of the responses. Local linear regression solves a kernel-weighted least-squares fit at each point, which removes boundary bias to first order, and the authors advise it over Nadaraya-Watson. The tricube kernel is (1 - u^3)^3 for u <= 1, with span s = m/n; their illustration uses a span of 25% of the data, normally picked by cross-validation. These are memory-based methods: all training data is kept and the local fit recomputed per prediction.

## Limits

- Evidence is two small examples (leukemia and one protein set), each a single run with no error bars.
- The quadratic penalty keeps all features in the model, so sparsity needs the lasso penalty instead.
- Both kernel SVMs and kernel smoothing hit the curse of dimensionality, since in many dimensions no neighbourhood is truly local.
- A small budget B with a radial kernel makes islands (overfit).
- The chapter is dated 2016 and makes no deep-learning comparison; the sign of the exponent in the radial kernel is unconfirmed in the extraction.

## See Also
- [[Kernel SVM and the Kernel Trick]] — prerequisite-for
- [[Penalised Linear Models: Ridge, Lasso and Elastic Net]] — related (the penalty swapped for sparsity)
- [[Platt Scaling for SVM Probabilistic Outputs]] — related
- [[Regularisation Knobs and Early Stopping]] — related
