---
title: "Pipelines Prevent Preprocessing Leakage"
tags: [foundations, pattern]
summary: "Any fitted preprocessing step must be refit inside each CV fold; a Pipeline does that, and feature selection outside the loop turns pure noise into a strong score."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--03-feature-engineering-and-pipelines.md
---

# Pipelines Prevent Preprocessing Leakage

**Rule:** any step with a `fit` (scaling, imputation, encoding, selection, PCA, target encoding, text vectorising) must be refit inside each cross-validation fold. If a scaler is fit on all training data first, the validation fold shaped the preprocessing and the CV score is optimistic. A `Pipeline` chains transformers and a final estimator into one estimator so `fit`, `predict`, `score` and cross-validation treat the whole chain as one model.

## How big the bias is

- **Scaling**: small. A grid search on a min-max-scaled SVC with the scaler fit on all training data reports best CV 0.981.
- **Feature selection**: enormous. Take 100 rows of 10,000 pure-noise features and a random target, keep the top 5% by univariate score, then cross-validate ridge: R squared 0.89. Cross-validating the pipeline (select then ridge) gives -0.03, which correctly says there is no signal.
- **Resampling** is the same kind of step; see [[Resampling Before the Split Leaks]].

## Using pipelines

- Parameters of steps are addressed as `<step name>__<parameter>`; `make_pipeline` names steps automatically in lowercase.
- Preprocessing has hyperparameters too and can be searched jointly with the model (for example polynomial degree and ridge alpha), and a whole step can be treated as a parameter (scaler or none, SVC or forest) with a list of parameter grids.
- `Pipeline(memory=...)` caches fitted transformers so an expensive step is not refit for every model parameter.
- Every step but the last needs `fit` and `transform`; `fit` calls `fit_transform` down the chain, `predict` calls `transform` then the final `predict`.
- The fitted chain is the artefact to deploy, which matters beyond leakage.

## Pitfalls

| Pitfall | Fix |
|---|---|
| Scaler, selector or encoder fit on all data | Put the step in a pipeline and cross-validate the pipeline |
| Random split on time data | Split in time order; a rolling-origin backtest repeats it |

## See Also
- [[Tabular ML Leakage Taxonomy]] — related
- [[Train, Validation and Test Discipline]] — prerequisite-for
- [[Cross-Validation Variants and Nested Search]] — related
- [[Feature Representation for Linear Models]] — related
