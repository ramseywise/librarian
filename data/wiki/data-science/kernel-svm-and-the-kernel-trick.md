---
title: "Kernel SVM and the Kernel Trick"
tags: [data-science, concept]
summary: "A kernel SVM is a linear model in an implicit richer feature space; C and gamma must be tuned together and features must be scaled."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--02-supervised-learning.md
  - data/raw/papers/2026-11-07-cortes-1995-support-vector-networks.md
  - data/raw/papers/2026-11-07-pedregosa-2012-scikit-learn.md
---

# Kernel SVM and the Kernel Trick

A kernelised support vector machine is a linear model in a richer feature space. Adding a squared feature turns a curved boundary into a plane in a higher dimension. The **kernel trick** computes inner products in that expanded space without building it.

| Kernel | Implicit features |
|---|---|
| Polynomial | All products of features up to a degree |
| RBF (Gaussian) | Infinite-dimensional; similarity `exp(-gamma * squared distance)`, with gamma = 1 / (2 sigma squared) |

The boundary rests on the **support vectors**, meaning the training points that sit on or inside the margin. The original contribution was the soft-margin formulation: `C` puts a price on each margin violation, so data that cannot be separated still has a solution. In its original experiments, polynomial kernels of degrees 2 to 7 on a small digit set all landed between 4.2 and 4.7% error while the linear one had 12.0%, and the implicit space grew from roughly 33,000 to roughly 10^16 dimensions; support vectors rose only from 127 to 190 (Cortes and Vapnik, 1995, USPS; self-reported), and ten degree-4 polynomial SVMs reached 1.1% test error on NIST digits (60,000 train, 10,000 test, no pre-processing; self-reported). Those are single runs with no error bars. They used a squared slack penalty, reported no value of C and no RBF result, so they do not support tuning advice.

Scikit-learn's `SVC` wraps libsvm; Pedregosa et al. (2011) report bindings with overhead as much as 40% lower than the first libsvm Python bindings (no measurement setup given for the 40%) and an SVC fit of 5.2 s on Madelon (4400x500), the lowest in their 2011 timing table (hardware and settings unstated; self-reported).

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
