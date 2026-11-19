---
title: "Feature Representation for Linear Models"
tags: [data-science, pattern]
summary: "Binning, interactions, polynomials, log transforms, selection and domain features give linear models shape; trees gain little from them."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--03-feature-engineering-and-pipelines.md
  - data/raw/papers/2026-11-08-intro-to-ml-with-python-ch04-representing-data-engineering-features.md
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

## Textbook results (Müller and Guido)

- **One-hot on a census table:** logistic regression on the one-hot adult-income features (32,561 rows, `get_dummies` to 44 features, default 75/25 split) scores 0.81 test accuracy.
- **Polynomials on Boston:** with 13 min-max-scaled features expanded to degree 2 (105 features including the constant, 379 training rows), ridge test R squared rises from 0.621 to 0.753 while a 100-tree random forest drops from 0.799 to 0.763.
- **Selection on noise-padded cancer data:** the cancer features plus 50 standard-normal noise columns (80 features, half the rows for training, logistic regression). Univariate selection of 50% keeps 40 features and takes test accuracy to 0.940, up from 0.930 with every feature; model-based selection (100-tree forest, median threshold) gives 0.951, and RFE down to 40 features with the same forest also gives 0.951.
- **Time features:** the Citi Bike table above is the chapter's (one station, August 2015, 3-hour bins, 184 training and 64 test points in time order), and it reports -0.04 for the forest on raw POSIX time where its text says -0.03. The Poisson-count figures above use 1,000 samples of 3 synthetic features.

The authors advise binning only for linear models, adding bin-by-feature interactions so each bin gets its own slope, adding polynomial features for linear and naive Bayes models, log-transforming skewed counts, fitting selection on the training split only, and keeping raw timestamps away from tree models.

## Limits

- The chapter uses single splits and seeds, so 0.930 against 0.940 rests on about 285 test rows. Its selection experiments differ in split and numbers from the ones above (for instance 0.951 against 0.961 for model-based selection).
- The authors themselves say selection seldom helps much on real data, and the noise-padded cancer example is synthetic. The Boston polynomial gain for ridge contrasts with the diabetes grid search above, which found no reason to expand.
- Its code is pre-0.20 scikit-learn (`.ix`, integer-only `OneHotEncoder`, `load_boston`). It does not cover target or frequency encoding, high-cardinality categories, `ColumnTransformer` or leakage inside cross-validation.
- Text and code slips: the log is applied twice in the Fig 4-8 code, value 2 is said to appear 62 times where `bincount` shows 68, and `get_dummies` is said to give 46 columns where the shape is 44.

## See Also
- [[Categorical Encoding Choices]] — related
- [[Penalised Linear Models: Ridge, Lasso and Elastic Net]] — related
- [[Pipelines Prevent Preprocessing Leakage]] — related
