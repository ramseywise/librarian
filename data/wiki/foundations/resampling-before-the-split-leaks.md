---
title: "Resampling Before the Split Leaks"
tags: [foundations, pattern]
summary: "Resampling then cross-validating puts copies or interpolations of training rows into validation folds, turning a true 0.70 AUC into 0.98; keep the sampler inside the pipeline so it runs only on training folds."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--10-imbalance-errors-and-drift.md
---

# Resampling Before the Split Leaks

If the data is oversampled first and split afterwards, validation folds contain exact copies of training rows or points interpolated from them, so cross-validation measures memory. The mistake is easy because `fit_resample` followed by `cross_val_score` is short and raises no error.

Measured on the 3% default book ([[Imbalance Remedies Versus a Tuned Threshold]]), ROC-AUC (ignores the class mix): a single run gave leaked 0.934, pipeline 0.726, test 0.742. Over repeats with one large fixed model: random oversampling leaked 0.964 against pipeline 0.735 and test 0.748; SMOTE leaked 0.984 against pipeline 0.697 and test 0.703. The pipeline estimate tracks the test score; the leaked one promises 0.98 for a model that truly scores 0.70. The leak does not vanish with exact copies instead of interpolations: a tree memorises copies of a defaulter that land in both sides.

Fix: use an imbalanced-learn style pipeline, in which a sampler is a step that runs during fit and is skipped during predict, so validation and test data are never resampled and cross-validation refits it inside each training fold. Also set automatic early stopping off or supply your own validation: a histogram booster turns it on above 10,000 rows and would hold out resampled rows.

This is one case of the general rule that every fitted step belongs inside the fold ([[Pipelines Prevent Preprocessing Leakage]], [[Tabular ML Leakage Taxonomy]]).

## See Also
- [[Pipelines Prevent Preprocessing Leakage]] — extends
- [[Tabular ML Leakage Taxonomy]] — instance-of
- [[Imbalance Remedies Versus a Tuned Threshold]] — related
- [[Cross-Validation Variants and Nested Search]] — related
