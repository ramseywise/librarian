---
title: Entropy Balancing
tags: [foundations, pattern]
summary: "Entropy balancing finds control weights closest to uniform whose covariate moments equal the treated group's exactly, skipping the propensity model; limited overlap shows up as extreme weights, so check effective sample size alongside balance."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--03-experimentation-and-causality--notes--05-matching-and-weighting.md
---

# Entropy Balancing

Propensity weighting models who was treated and hopes balance follows. Entropy balancing skips the model: it asks directly for control weights that make the control covariate means equal the treated means exactly, while staying as close to equal weights as possible. The primal problem looks large, but the dual has one parameter per covariate, so a general optimiser (BFGS on the log of summed exponentials) solves it in a few lines; weights are exp(-C z) normalised.

## Results (club data, 10 covariates)

- Keeps all 3,746 treated units, max SMD 0.000 on the balanced covariates, control effective sample 267 against 107 for propensity weights; largest control weight share 4.3% against 8.6%.
- ATT estimate 26.49 against a true 23.38; mean gap 3.59 over 20 datasets (sd 1.36), steadier than matching with replacement or plain weights.
- Because it does not model the outcome, a floor on spend barely touches it, unlike linear regression.
- With the hidden engagement trait added to the balance set, the mean gap fell to 0.15, inside its standard error: the bias is from what was not logged, not from the estimator.

## Cautions

- Limited overlap produces extreme weights; balance says nothing about what it did to effective sample size.
- Perfect balance on logged covariates can leave or even widen imbalance on unlogged ones ([[Sensitivity Analysis for Unmeasured Confounding]]).
- Dropping prior orders from the balance set raised the ATT from 26.49 to 32.93, with the omitted-bias arithmetic predicting 7.16 against an observed rise of 6.44.

## See Also
- [[Matching and Weighting Estimators]] — related
- [[Covariate Balance and Overlap Checks]] — related
