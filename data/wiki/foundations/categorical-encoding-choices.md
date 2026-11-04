---
title: "Categorical Encoding Choices"
tags: [foundations, reference]
summary: "One-hot, ordinal, frequency and target encoding suit different models and cardinalities; fit the encoder on training data and handle unseen categories."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--03-feature-engineering-and-pipelines.md
---

# Categorical Encoding Choices

Which representation is best depends on the model. Linear models, SVMs and MLPs want scaled numeric features, plus expanded ones (bins, interactions, polynomials) for non-linear shapes. Trees and ensembles want raw features, need no scaling and find interactions themselves. kNN wants scaled features, few of them.

| Encoding | When |
|---|---|
| One-hot | Few categories; linear models |
| Ordinal (`OrdinalEncoder`) | Categories with an order; tree models |
| Frequency | Very many categories; reads no target, so it works with no labels, though it merges levels of equal size |
| Target encoding | Very many categories (IDs, zip codes); needs a target and cross-fitting to avoid leakage, so it cannot be used for clustering; weight of evidence is a target encoding learned on the training set only |
| Native support | `HistGradientBoostingClassifier(categorical_features=...)`, LightGBM |

## One-hot mechanics

A column with k categories becomes k binary columns. On the adult census data, six columns (four strings) go from 6 to 42 columns with `get_dummies`. Pitfalls:

- **Encode with a fitted encoder.** `get_dummies` on train and test separately can give different columns when a category appears in only one. Use `OneHotEncoder` inside a `ColumnTransformer`, which remembers training categories and applies scaling to numeric columns and encoding to categorical ones in one object.
- **`handle_unknown="ignore"`** in production encoders: an unseen category becomes all zeros instead of crashing, and new categories do appear after deployment.
- **Integers can be categories.** A survey code 1-5 or a zip code is categorical though numeric; convert to string first or a linear model learns a slope across zip codes.
- **Typos and whitespace.** "Male" vs "male", or " Private" vs "Private", become separate columns; check `value_counts()`.

Result: with the six adult columns, logistic regression reaches 0.811 test accuracy on 44 columns, against a 0.759 base rate. Adding the country column grows the matrix to 86 columns with no change in accuracy, because it is mostly one value.

## See Also
- [[Feature Representation for Linear Models]] — related
- [[Pipelines Prevent Preprocessing Leakage]] — related
- [[Weight-of-Evidence Logistic Scorecard]] — instance-of (weight of evidence as a target encoding)
- [[Clustering Categorical and Mixed Data]] — related
