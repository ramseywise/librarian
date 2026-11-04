---
title: "Cross-Validation Fold Spread and Choosing the Splitter"
tags: [foundations, pattern]
summary: "Fold spread sizes up noise but is not a clean standard error; compare models fold by fold, and pick the splitter (stratified, group, forward-in-time) that mimics how new data will arrive."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--09-training-and-tuning.md
---

# Cross-Validation Fold Spread and Choosing the Splitter

The splitter variants and nested search are in [[Cross-Validation Variants and Nested Search]]; this page covers what the fold scores say and when the default folds lie. Figures: adult census, 5-fold, AUC.

## Reading the spread

Logistic folds: mean 0.9082, sd 0.0043. Boosting: mean 0.9279, sd 0.0041. So configurations 0.001 apart are not meaningfully different.

**Compare fold by fold.** Boosting beat logistic by 0.0197 and won all five folds; the paired differences have sd 0.0025, smaller than either model's, because an easy fold is easy for both. Pairing removes the shared luck.

**Fold sd divided by sqrt(k) is not a clean standard error.** Repeating 5-fold on disjoint samples: at 500 rows the true sd of the CV mean was 0.0252 (20 samples) while the naive figure averaged 0.0147, about 40% too confident; at 2,000 rows 0.0066 against 0.0069 on average, but single-run naive values ranged 0.0042 to 0.0116 (13 samples, rough). No universal unbiased estimator of k-fold variance exists: folds share training rows, so their scores correlate, and the part a naive estimate captures was 50 to 70% of the total in published experiments. Treat spread as a rough noise guide and use paired differences.

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
