---
title: "Kernel SVM and the Kernel Trick"
tags: [data-science, classical-ml, concept]
summary: "A kernel SVM is a linear model in an implicit richer feature space; C and gamma must be tuned together and features must be scaled."
updated: 2026-11-20
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--02-supervised-learning.md
  - data/raw/papers/2026-11-07-cortes-1995-support-vector-networks.md
  - data/raw/papers/2026-11-07-pedregosa-2012-scikit-learn.md
  - data/raw/papers/2026-11-08-intro-to-ml-with-python-ch02-supervised-learning.md
  - data/raw/papers/2026-11-08-intro-to-ml-with-python-ch03-unsupervised-learning-preprocessing.md
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch19-support-vector-machines-kernel-methods.md
  - data/raw/papers/2026-11-08-islp-ch09-support-vector-machines.md
  - data/raw/papers/2026-11-08-python-data-science-handbook-ch05-machine-learning.md
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

## Scaling in Müller and Guido's chapters

On Wisconsin Breast Cancer (569 rows, 30 features, `random_state=0` split), the default `SVC` (C=1, gamma = 1/n_features) on raw features scores 1.00 train and 0.63 test. After min-max scaling with the training minimum and range it scores 0.948 train and 0.951 test, which the chapter reads as underfitting, and raising C to 1000 gives 0.988 and 0.972. In the preprocessing chapter, `SVC(C=100)` gets 0.63 test accuracy on raw features, 0.97 after `MinMaxScaler` and 0.96 after `StandardScaler`, each fit on the training part only. The scaled test set does not span exactly 0 to 1, because the training transform is reused.

The authors advise scaling all features to a similar range such as 0 to 1, tuning C and gamma together, and note the method is practical up to about 10,000 samples and hard at 100,000.

## Loss, tuning and a faces run (CASI, ISLP, Python Data Science Handbook)

Efron and Hastie say that at the population level, with two classes and equal costs, the function minimising the hinge loss is the Bayes classifier, while the one minimising binomial deviance is the logit of the class probability. They also note that a ridged logistic regression's coefficient direction approaches the SVM's on separable data as lambda goes to zero. Their examples are two small, single-run illustrations from 2016.

For the support-vector classifier's slack budget see [[Support Vector Classifier, Slack Budget and Hinge Loss]]. Two further points from ISLP's chapter 9 lab: a radial SVM whose cost and gamma were tuned by cross-validation misclassified 12% of the test points on the simulated data, and in the book's slack-budget formulation a large C allows more slack and a wider margin. The authors advise choosing C by cross-validation rather than keeping the default.

VanderPlas's handbook runs an RBF SVM on faces: Labeled Faces in the Wild people with at least 60 images (1,348 images of 62 by 47 pixels, 8 people), reduced by whitened randomised PCA to 150 components, then `SVC(kernel='rbf', class_weight='balanced')`. A grid search over four values of C (1 to 50) crossed with four of gamma (0.0001 to 0.005) picked C=10 and gamma=0.001 and took 26 seconds of wall time (hardware not stated). On the 337 held-out faces precision, recall and F1 all average about 0.85. He suggests a naive Bayes model as the quick first baseline, with an SVM reserved for when simpler methods fall short.

## Limits

- The course-note figure above (0.629 unscaled) is stated with C=1000, while the chapter's unscaled 0.63 uses the default C; the two setups differ.
- The chapters give single splits with no variance. The chapter's kernel formula drops the minus sign in the exponent, and the RBF `gamma` default has since changed to `'scale'`.
- The faces result is one split on 337 images; the code is 2016-era scikit-learn API.
- The hinge-versus-logistic claim is a cited result of Wahba and colleagues (2000), and the ISLP simulations are tiny with the LDA comparison read off a plot.

## See Also
- [[Supervised Model Families and Complexity Knobs]] — prerequisite-for
- [[Penalised Linear Models: Ridge, Lasso and Elastic Net]] — related
- [[Platt Scaling for SVM Probabilistic Outputs]] — related
- [[Margin Classifiers, Hinge Loss and Kernel Smoothing]] — extends
- [[Support Vector Classifier, Slack Budget and Hinge Loss]] — related
