---
title: "Cross-Validation Fold Spread and Choosing the Splitter"
tags: [data-science, classical-ml, pattern]
summary: "Fold spread sizes up noise but is not a clean standard error; compare models fold by fold, and pick the splitter (stratified, group, forward-in-time) that mimics how new data will arrive."
updated: 2026-11-20
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--09-training-and-tuning.md
  - data/raw/papers/2026-11-08-bengio-2004-no-unbiased-estimator-variance-k-fold.md
  - data/raw/papers/2026-11-08-intro-to-ml-with-python-ch05-model-evaluation-improvement.md
---

# Cross-Validation Fold Spread and Choosing the Splitter

The splitter variants and nested search are in [[Cross-Validation Variants and Nested Search]]; this page covers what the fold scores say and when the default folds lie. Figures: adult census, 5-fold, AUC.

## Reading the spread

Logistic folds: mean 0.9082, sd 0.0043. Boosting: mean 0.9279, sd 0.0041. So configurations 0.001 apart are not meaningfully different.

**Compare fold by fold.** Boosting beat logistic by 0.0197 and won all five folds; the paired differences have sd 0.0025, smaller than either model's, because an easy fold is easy for both. Pairing removes the shared luck.

**Fold sd divided by sqrt(k) is not a clean standard error.** Repeating 5-fold on disjoint samples: at 500 rows the true sd of the CV mean was 0.0252 (20 samples) while the naive figure averaged 0.0147, about 40% too confident; at 2,000 rows 0.0066 against 0.0069 on average, but single-run naive values ranged 0.0042 to 0.0116 (13 samples, rough). Treat spread as a rough noise guide and use paired differences.

**Bengio and Grandvalet's result.** No estimator of the variance of k-fold CV is unbiased under every data distribution (their Theorem 6), including leave-one-out and two-fold. By permutation symmetry the covariance of the CV errors has three values (sigma^2, omega, gamma), and the three constraints an unbiased quadratic estimator needs cannot hold together. Omega is the covariance of test errors within a block, from the shared training set; gamma is the covariance between blocks, from overlapping training sets. In their Letter experiment (2 classes, decision trees, K=10, training sets drawn with replacement from 20,000 examples) the sigma^2 component alone was 50 to 70% of the total variance depending on training size (self-reported), so an estimator built on it alone would understate the variance by roughly its own size. With outliers in synthetic regression (OLS, 30 features, K=10, outlier mixture p=0.95) gamma's contribution was comparable to sigma^2 even with up to 20 examples per parameter. They found no general trend of variance with K: the lowest variance appeared at K=n in some settings and at a middle K in others (n=120).

The chapter authors advise stratified k-fold for classification, plain k-fold for regression, a shuffle with fixed random_state for ordered data, and GroupKFold when samples from one patient or speaker must not span train and test. On class-ordered iris, unshuffled 3-fold logistic regression scored zero in every fold, in their example.

## Limits

- Bengio and Grandvalet's theorem is about universality, so it does not rule out a useful estimator for particular cases; they propose modelling the dependence structure next. Their experiments use a linear model and trees on Letter cut to 2 classes, the number of Monte Carlo training sets for experiments 2 and 3 is not stated, and the analysis assumes symmetric algorithms, n a multiple of K, and does not cover repeated k-fold.
- The chapter's examples are single splits on small toy data.

## Choose the splitter by how data arrives

| Data | Splitter | Measured |
|---|---|---|
| Rare classes or few rows | Stratified | On 200 rows plain folds had positive rates 0.2 to 0.35; stratified held 0.275 in all five |
| Rows in groups, new groups at serving time | Group k-fold | Holding out occupations dropped mean AUC from 0.9279 to 0.9122, sd 0.0041 to 0.0286, worst fold 0.8625 |
| Rows over time | Forward-only (time-series split) | Shuffled folds claimed R-squared 0.648; forward folds 0.590, climbing 0.374 to 0.761 as history grew |

The group split asks how the model does on a segment it has never seen, usually the honest question where groups stand for customers, patients or stores. Shuffling lets a model train on next Tuesday to predict this Monday; see [[Time-Series Leakage: Shift and Rolling Windows]] and [[Tabular ML Leakage Taxonomy]].

For a churn task with several rows per customer over four years, both structures apply: train on earlier quarters, score a later one, and keep each customer on one side if future customers will be new; expect a lower score and wider spread than shuffled folds.

## See Also
- [[Cross-Validation Variants and Nested Search]] — extends
- [[Train, Validation and Test Discipline]] — prerequisite-for
- [[Hyperparameter Search Budgets and Selection Optimism]] — related
- [[Pseudoreplication and Intraclass Correlation]] — related
