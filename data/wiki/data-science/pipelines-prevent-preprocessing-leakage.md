---
title: "Pipelines Prevent Preprocessing Leakage"
tags: [data-science, classical-ml, pattern]
summary: "Any fitted preprocessing step must be refit inside each CV fold; a Pipeline does that, and feature selection outside the loop turns pure noise into a strong score."
updated: 2026-11-20
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--03-feature-engineering-and-pipelines.md
  - data/raw/papers/2026-11-08-intro-to-ml-with-python-ch06-algorithm-chains-pipelines.md
  - data/raw/papers/2026-11-08-intro-to-ml-with-python-ch08-wrapping-up.md
  - data/raw/papers/2026-11-08-python-for-data-analysis-ch13-introduction-modeling-libraries.md
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

## Textbook results (Müller and Guido)

On a breast-cancer SVC (`random_state=0` split, 6 by 6 grid over C and gamma, 5-fold CV), scaling the training data first and then grid-searching gives CV 0.98, test 0.97, best gamma=1 and C=1; the same grid on a `Pipeline(MinMaxScaler, SVC)` gives the same headline numbers, so the leak barely mattered here. A pipeline of `StandardScaler`, `PolynomialFeatures` and `Ridge` searched over degree 1 to 3 and ridge alpha scores test R squared 0.77 on Boston at degree 2 and alpha 10, against 0.63 with no polynomial step. A search that also varies the preprocessing step (`StandardScaler` or `None`) and the classifier (SVC or a 100-tree forest) picks SVC with standard scaling (C=10, gamma=0.01), at 0.99 CV and 0.98 test.

The authors advise making cross-validation the outermost loop, tuning preprocessing jointly with the model, reaching fitted steps through `named_steps` (via `best_estimator_` once a search has run), writing explicit step names when a step type repeats, and not over-building a pipeline: check that each component is needed. They also advise wrapping any data-dependent preprocessing in a custom estimator (`BaseEstimator` plus `TransformerMixin`) so the step remains part of the cross-validated chain.

## Stateful transforms at prediction time (Python for Data Analysis)

McKinney notes that Patsy's centring and standardising transforms are stateful: applying them to new data must reuse the mean and standard deviation from the training sample, which is what `build_design_matrices` does when given the saved `design_info`. For missing values he computes the fill value on the training rows only and applies it to both train and test (his Titanic example fills missing Age with the training median).

## Limits

- The textbook calls scaling leakage usually mild and quantifies it only with the single 0.98 and 0.97 example. It notes that adding search parameters multiplies the number of models to build, and that searching over everything is usually not viable.
- Its noise example is described as 1,000 features and "most informative of 10" in the text, while the code uses 10,000 features (5% kept gives 500). Its model-selection text says iris where the code uses the cancer data. The extraction records no R squared values for the noise experiment, so the two figures on this page come from the course note.
- `load_boston` is removed from scikit-learn and the printed outputs show old defaults. The custom-estimator advice comes from the closing chapter, which reports no experiments.
- The Titanic model is a demonstration the author does not claim is good.

## See Also
- [[Tabular ML Leakage Taxonomy]] — related
- [[Train, Validation and Test Discipline]] — prerequisite-for
- [[Cross-Validation Variants and Nested Search]] — related
- [[Feature Representation for Linear Models]] — related
- [[Ordered Boosting and Ordered Target Statistics]] — related (ordered encoding avoids target leakage)
