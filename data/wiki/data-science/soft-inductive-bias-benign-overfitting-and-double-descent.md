---
title: "Soft Inductive Bias, Benign Overfitting and Double Descent"
tags: [data-science, concept]
summary: "Wilson argues that benign overfitting and double descent are not specific to neural networks: a flexible model with a soft preference for simple solutions, and compressibility-based bounds, account for both."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-06-wilson-2025-deep-learning-not-so-mysterious.md
---

# Soft Inductive Bias, Benign Overfitting and Double Descent

Wilson's ICML 2025 position paper holds that benign overfitting, double descent and overparametrised models generally are described by older generalisation theory, so understanding deep learning does not require rethinking generalisation. The evidence is mostly argument, toy demonstrations and results cited from other papers.

## Soft versus restricted bias

The paper's advice is to keep a flexible hypothesis space and put a soft preference for simpler solutions that fit the data, rather than shrinking the space to avoid overfitting. The worked case is a 150th-order polynomial with a penalty that grows with the order of each term. It describes simple data and structured data reasonably, and fits pure noise perfectly; Wilson presents this as benign overfitting in a model that is not a neural network. In his toy demonstration (three target functions, 100 refits, 100 test samples), a regularised 15th-order polynomial matched or beat a 2nd-order and an unregularised 15th-order fit at every training size tried, 10 to 100 samples (self-reported). Another instance is soft equivariance via residual pathway priors, which the paper reports ties a hard-constrained model for an exact symmetry and wins for an approximate or absent one (cited result).

## The noisy-label test

Zhang et al.'s CIFAR-10 experiment showed networks fitting random labels and still generalising on real ones; this is the claim the paper sets out to rebut. In Wilson's demonstration, adapted from Wilson and Izmailov, a Gaussian process with an RBF kernel reproduces the pattern: it fits noisy labels with zero training error, and its generalisation worsens steadily as more labels are changed. Marginal likelihood for the GP (up to 25k labels altered) and for a PreResNet-20 (up to 50k) both fall as labels are changed, which Wilson reads as in line with PAC-Bayes bounds (self-reported). (See [[Gaussian Processes and Bayesian Optimisation]] for the GP.)

## Bounds the paper says explain it

Rademacher complexity, VC dimension and fat-shattering penalise the size of the hypothesis space, so the paper says they cannot explain benign overfitting or double descent. Wilson argues that PAC-Bayes and countable-hypothesis bounds pass the random-label test because they depend on how compressible the chosen solution is.

The recipe for a bound: train with any optimiser, measure training loss, measure the stored file size of the model as an upper bound on its Kolmogorov complexity, and substitute both into the bound. The paper cites a bound of 16.6% test error on CIFAR-10, with probability at least 95%, for a model with millions of parameters, and non-vacuous bounds for language models with billions of parameters. These were not re-run in the paper.

## Double descent

The paper dates double descent to Opper et al. (1989) at the latest, and notes Belkin et al. (2019) had shown it in random forests and random-feature models. In the paper's account, a linear random-feature model reproduces it. Once the number of features exceeds the number of samples, the model interpolates the data in infinitely many ways and the minimum-norm solution is chosen. Past that point all models fit the training data perfectly, so added flexibility cannot be what helps. Wilson's explanation is that flat, compressible solutions occupy a larger share of the space as parameters grow and are easier to find, and effective dimensionality falls. Maddox et al. (2020) found larger trained networks had fewer effective parameters than smaller ones.

## Other claims

- SGD's implicit bias is not required: large residual networks trained by full-batch gradient descent come close, and random sampling until the loss is low stays competitive (cited from Geiping et al. 2021 and Chiang et al. 2022). Wilson adds that SGD remains much more practical.
- The bias-variance "trade-off" is a misnomer in Wilson's view, since the order-dependent polynomial and ensembles show a model can have both low bias and low variance. See [[Bias-Variance Decomposition and Model Complexity]].
- What the paper calls distinctive about neural networks is representation learning, plus universality, in-context learning and mode connectivity, though even these have partial analogues (deep kernel learning, tree-ensemble mode connectivity).

## Limits

- Wilson does not say deep learning is fully understood, and calls the reason larger models gain a stronger compression bias an open question.
- Flatness changes under reparametrisation, and flatter solutions do not always generalise better; effective dimensionality gives intuition rather than a bound. Kolmogorov complexity cannot tell randomness from structure when a model is incompressible.
- PAC-Bayes bounds are descriptive, and their tightness depends on the prior. Restricting the model (sparsity, parameter sharing) can still save computation; the paper treats computation as free.
- Almost all evidence is cited or toy-scale: Figs 1 and 5 are the only experiments, giving no new large-scale results and no measure of how loose the language-model bounds are.
- The extraction could not recover Fig 1 and Fig 5 plot values or the exact penalty formula in Appendix D, and the Fig 1(f) caption names ResNet-18 while the text names CIFAR-100 cross-entropy and the appendix gives only the width sweep.

## See Also
- [[Bias-Variance Decomposition and Model Complexity]] — prerequisite-for
- [[Regularisation as a Prior]] — prerequisite-for
- [[Learning Curves and Bias-Variance Diagnosis]] — related
