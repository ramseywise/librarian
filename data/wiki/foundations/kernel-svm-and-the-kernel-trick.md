---
title: "Kernel SVM and the Kernel Trick"
tags: [foundations, concept]
summary: "A kernel SVM is a linear model in an implicit richer feature space; C and gamma must be tuned together and features must be scaled."
updated: 2026-11-09
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--02-supervised-learning.md
---

# Kernel SVM and the Kernel Trick

A kernelised support vector machine is a linear model in a richer feature space. Adding a squared feature turns a curved boundary into a plane in a higher dimension. The **kernel trick** computes inner products in that expanded space without building it.

| Kernel | Implicit features |
|---|---|
| Polynomial | All products of features up to a degree |
| RBF (Gaussian) | Infinite-dimensional; similarity `exp(-gamma * squared distance)`, with gamma = 1 / (2 sigma squared) |

Only the training points on or inside the margin, the **support vectors**, define the boundary. The soft-margin formulation, where `C` prices each margin violation so that non-separable data still has a solution, was the original contribution. In its original experiments, polynomial kernels of degrees 2 to 7 on a small digit set all reached 4.2 to 4.7% error against 12.0% for linear, with the implicit space growing from about 33,000 to about 10^16 dimensions; that is one dataset with no error bars, and used a different slack penalty than `SVC`, so it does not support tuning advice.

## Knobs

| Knob | Small value | Large value |
|---|---|---|
| `gamma` | Wide kernel, smooth boundary | Narrow kernel, every point its own island |
| `C` | Heavy regularisation | Fit every training point |

Tune them together in one grid search ([[Cross-Validation Variants and Nested Search]]).

## Scaling is not optional

Distances are dominated by the largest-valued features. On the breast-cancer split an RBF SVC with C=1000 scores 0.629 test accuracy unscaled and 0.972 after min-max scaling fit on the training set only. Put the scaler in a pipeline ([[Pipelines Prevent Preprocessing Leakage]]).

## When it fits

Good: small and medium data (up to about 10k samples), similar-scale features, complex boundaries in few dimensions. Fails: 100k+ samples (memory and time), unscaled features, interpretation.

## See Also
- [[Supervised Model Families and Complexity Knobs]] — prerequisite-for
- [[Penalised Linear Models: Ridge, Lasso and Elastic Net]] — related
- [[Platt Scaling for SVM Probabilistic Outputs]] — related
