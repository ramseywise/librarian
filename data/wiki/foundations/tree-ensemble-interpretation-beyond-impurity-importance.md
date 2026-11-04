---
title: "Tree Ensemble Interpretation Beyond Impurity Importance"
tags: [foundations, pattern]
summary: "Impurity importance rewards overfit noise; permutation importance on held-out data fixes that but is fooled by correlated columns, and partial dependence needs ICE lines and describes the model, not causes."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--08-model-interpretability.md
---

# Tree Ensemble Interpretation Beyond Impurity Importance

All post-hoc tools describe a model without being it. Pick by question: what it relies on (permutation importance), the shape of one effect (partial dependence with ICE), why one row scored as it did ([[SHAP Attributions and the Limits of Explanations]]). Examples below use a boosted model on the adult census (test AUC 0.9248, 180 rounds) with a pure-noise column and a random 5,000-level column added on purpose.

## Impurity (gain) importance misleads

It is summed loss reduction on training data, so it credits what the model overfit and favours columns with many values. The two junk columns took about 5% of gain between them (0.028 and 0.023) and outranked four real columns (workclass 0.009, gender 0.007, native-country 0.005, race 0.001); age ranked only fifth. See also the caveats in [[Random Forests and Bagging]].

## Permutation importance

Shuffle one column in held-out data and measure the score drop; no retraining. Overfit features earn nothing: the junk columns fell to 0.0003 and 0.0002 (within about one standard deviation of zero), age rose to second (0.0564) and the leading gain column dropped to fifth. Cheap and model-agnostic.

**Correlated-column trap.** Adding a noisy near-copy of age cut age's drop from 0.0564 to 0.0061 (the copy got 0.0294; together about 0.036), because the model reads whichever copy is intact. Group correlated columns and permute together, or drop one and refit. Shuffling also creates impossible rows the model must extrapolate to; conditional or refit-based alternatives exist.

## Partial dependence and ICE

Partial dependence sets one column to each grid value for every row, predicts and averages. ICE keeps one line per row. For age the average rose from 0.031 (age 19) to 0.281 (age 51) and eased to 0.248 (63), yet ICE at age 51 ran from 0.013 (10th percentile) to 0.781 (90th): age matters only for rows whose other features make them plausible. The observed rate at 51 was higher (0.394) because older people differ in other ways while partial dependence holds the rest fixed. Limits: it describes the model, not what happens if you change a person; it evaluates unlikely feature combinations (accumulated local effects or observed-combination plots help); a flat average can hide opposite effects, so always draw ICE. A two-way plot of age and hours worked showed an interaction the one-way curves miss: extra hours added about 0.016 at age 20 against 0.158 at age 52 (600-row sample).

## Checklist

| Pitfall | Fix |
|---|---|
| Quoting impurity importance as a finding | Permutation importance on held-out data |
| Two copies of an important feature both look minor | Permute as a group, or refit without one |
| Reading a dependence curve as causal | Treat it as a model description |
| Explaining a poor model | Check the model first; explaining noise yields noise |

## See Also
- [[SHAP Attributions and the Limits of Explanations]] — extends
- [[Random Forests and Bagging]] — related
- [[Gradient Boosting Mechanics and Library Choice]] — related
- [[Explain vs Predict Modelling]] — related
