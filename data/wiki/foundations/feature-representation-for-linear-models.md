---
title: "Feature Representation for Linear Models"
tags: [foundations, pattern]
summary: "Binning, interactions, polynomials, log transforms, selection and domain features give linear models shape; trees gain little from them."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--03-feature-engineering-and-pipelines.md
---

# Feature Representation for Linear Models

How data is represented usually matters more than which model is chosen. A domain feature can beat a stronger model fed raw input.

## Giving a linear model shape

| Technique | Helps | Cost |
|---|---|---|
| Binning (cut into intervals, one-hot) | Linear models on low-dimensional data | Loses within-bin information |
| Interactions (bin indicator times the feature) | Effects that combine; each bin gets its own slope | Feature count grows quadratically |
| Polynomials | Smooth non-linear trends | Extreme edge values at high degree; overfitting |

On a noisy wave toy, a line on the raw feature scores R squared 0.751 and a line on 10 bins 0.864. A decision tree on the binned features makes *identical* predictions to the linear model: binning gives the linear model the tree's flexibility and nothing to the tree. Degree-2 polynomials on the diabetes data (10 to 65 features): ridge 0.357 to 0.366, forest 0.247 to 0.202. Expanded features can help linear models and are mostly noise to trees. A grid search over polynomial degree and ridge alpha on that data finds no reason to expand (degree 1, alpha 10); let the search decide.

## Skewed counts

Counts are heavy-tailed; linear models and networks prefer roughly Gaussian inputs. On simulated Poisson counts with a log-normal-ish rate, ridge scores 0.622 on raw and 0.875 on `log1p` features (log of x plus 1 handles zeros). Alternatives: sqrt, Box-Cox or Yeo-Johnson (`PowerTransformer`), `QuantileTransformer`; skewed regression targets can be transformed too (`TransformedTargetRegressor`). Trees ignore monotone transforms.

## Automatic feature selection

| Strategy | How |
|---|---|
| Univariate (`SelectKBest`, `SelectPercentile`) | Test each feature against the target alone |
| Model-based (`SelectFromModel`) | Keep features above an importance or L1 threshold |
| Iterative (`RFE`, sequential) | Fit, drop the weakest, refit |

Experiment: 30 real breast-cancer features plus 50 noise features, logistic regression. All 80: 0.954. Univariate 50%: 0.965 (26 real kept); model-based: 0.961 (28); RFE to 40: 0.986 (29). Every selector beats keeping the noise, but the ordering among selectors moves with the split; only the gain over no selection is stable. Selection pays off when many features are noise; a regularised model on clean data rarely gains. Selection is a fitted step and must sit inside the pipeline ([[Pipelines Prevent Preprocessing Leakage]]).

## Domain knowledge beats the raw timestamp

Rentals per 3-hour slot for one station over August, 248 slots; first 184 train, the rest test in time order.

| Features, model | Test R squared |
|---|---|
| POSIX time, forest | -0.04 |
| Hour, forest | 0.6 |
| Hour + weekday, forest | 0.84 |
| Hour + weekday as numbers, linear | 0.13 |
| One-hot hour-weekday, ridge | 0.62 |
| One-hot pairs (interactions), ridge | 0.85 |

The forest on the timestamp has nothing to split on past the training range and predicts about the last value seen. Treating weekday and hour as numbers gives the linear model a slope it should not have; one-hot encoding repairs it. Commute and weekend effects are known to a person, not discovered from a timestamp, and the final ridge model has one readable coefficient per cell.

## Rules

- Expand features for linear models, not trees.
- Log-transform skewed counts.
- Try a domain feature before a bigger model.
- Split time-ordered data in time order; see [[Time-Series Leakage: Shift and Rolling Windows]].

## See Also
- [[Categorical Encoding Choices]] — related
- [[Penalised Linear Models: Ridge, Lasso and Elastic Net]] — related
- [[Pipelines Prevent Preprocessing Leakage]] — related
