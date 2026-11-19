---
title: Support Vector Classifier, Slack Budget and Hinge Loss
tags: [data-science, concept]
summary: "A support vector classifier maximises a margin while a slack budget C lets some points fall inside it or across it; the same fit is a hinge loss with a ridge penalty, which explains why it behaves like logistic regression."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-islp-ch09-support-vector-machines.md
---

# Support Vector Classifier, Slack Budget and Hinge Loss

ISLP's Chapter 9 builds the SVM in steps and compares it with logistic regression. A **hyperplane** is a flat subspace of dimension p - 1. The **margin** is the shortest perpendicular gap between any training point and the separating hyperplane, and a **support vector** is an observation on the margin or violating it; only support vectors affect the fitted classifier.

## The slack budget

The support vector classifier maximises the margin M subject to the squared coefficients summing to 1. Each observation gets a **slack variable** eps_i, positive when it is on the wrong side of the margin and above 1 when it is on the wrong side of the hyperplane. A budget C bounds the sum of the slacks, so no more than C observations may cross the hyperplane. With C = 0 the method is the maximal margin classifier. A large C widens the margin, brings in many support vectors and trades low variance for high bias; a small C does the reverse, with a tight margin with few support vectors, trading low bias for high variance. In ISLP's Fig 9.7 (four values of C on simulated two-dimensional data) the bottom-right panel has eight support vectors. The authors stress that C is not a nuisance parameter to leave at its default of 1, and choose it by cross-validation.

In the lab, with 25 points per class barely separable by a line and a linear kernel, C = 1e5 gave zero training errors with three support vectors, all on the margin. C = 0.1 likewise had no training errors, with a far wider margin and 12 support vectors, and the authors expected it to test better. On 50 non-separable simulated points, five-fold CV across C from 0.001 to 100 selected C = 1 (accuracy 0.74, tied with C = 5, 10 and 100; 0.46 at C = 0.001 and 0.01), and that model classified 70% of 20 test points correctly against 60% for C = 0.001.

## Hinge loss and logistic regression

The support vector classifier equals the **hinge loss**, the sum of max[0, 1 - y_i f(x_i)], plus a ridge penalty, with a small lambda corresponding to a small C in the budget form. The hinge loss is exactly zero once y_i f(x_i) is at least 1, while the logistic loss is never exactly zero but is very small far from the boundary, so the two often give similar results. As a rule of thumb the authors say SVMs tend to do better when classes are well separated and logistic regression is often preferred when they overlap; kernels are not specific to SVMs, since logistic regression can use them too.

## Kernels and more than two classes

A **kernel** K(x_i, x_i') measures the similarity of two observations. The solution needs only the pairwise inner products, and the coefficients are non-zero only for support vectors. The radial kernel has an infinite-dimensional feature space and is very local, so distant training points have almost no effect on a test point's class. On the Heart data (297 subjects after dropping 6 with missing values, 207 train and 90 test, 13 predictors), a radial SVM with gamma = 1e-1 gave a near-perfect training ROC and the worst test ROC, while gamma = 1e-2 and 1e-3 matched the linear classifier. For K > 2 classes, one-versus-one trains a classifier for every pair of classes and lets them vote; one-versus-all trains K classifiers, one per class, and takes the class scoring highest. On the Khan data (63 train, 20 test, 2,308 genes, 4 classes) a linear SVC with C = 10 made 0 training errors and 2 test errors; the authors say a linear kernel suffices when p is far above n.

## Limits

- The authors call the optimisation and kernel details beyond the book's scope.
- The lab sets are small simulations (20 to 100 test points), so gaps of a few points mean little.
- On Heart the support vector classifier's edge over LDA is read from ROC curves, and the text says it is not significant; the claim that small C tests better than large C is left to an exercise.
- In places the lab's prose and its printed output give different tuned parameters.

## See Also
- [[Kernel SVM and the Kernel Trick]] — extends
- [[Penalised Linear Models: Ridge, Lasso and Elastic Net]] — related
- [[Logistic Regression Odds Ratios vs Marginal Effects]] — related
