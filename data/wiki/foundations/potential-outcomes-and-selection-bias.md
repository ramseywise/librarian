---
title: Potential Outcomes and Selection Bias
tags: [foundations, concept]
summary: "Each unit has two potential outcomes but only one is seen, so a naive treated-minus-untreated comparison equals the effect on the treated plus selection bias; opt-in comparisons mostly measure selection (1.21 against a true 0.30), and controlling for the selection driver recovers it only if nothing unmeasured matters."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--03-experimentation-and-causality--notes--04-correlation-and-causation.md
---

# Potential Outcomes and Selection Bias

Every unit has Y(1) with treatment and Y(0) without; only one is observed. The naive comparison splits:

E[Y | treated] - E[Y | untreated] = E[Y(1) - Y(0) | treated] (effect on those who opted in) + E[Y(0) | treated] - E[Y(0) | untreated] (selection bias).

Randomisation makes the second term zero. Opting in does not.

## Numbers (simulated opt-in email, true effect 0.30)

- Opt-in rate 44.2%. Naive difference 1.21 orders; opted-in customers had 2.84 past orders against 1.34. So 0.91 of the 1.21 is selection.
- Regression on past orders recovers 0.311, because past orders explain opting in.
- Propensity weighting gives 0.336; the gap in past orders falls from 1.50 to 0.04 after weighting, but propensities from 0.232 to 1.000 give a largest weight of 48.3, one user counting as 48.
- An unmeasured cause of both opting in and ordering leaves control for past orders biased: 0.642 against a true 0.30; with the hidden cause logged, 0.3. Nothing in the data warns you. Propensity scores balance only observed covariates.

That "if" is the assumption of no unmeasured confounders. Propensities near 0 or 1 signal poor overlap: trim or report an effect only for the overlapping population. Checks on this assumption are in [[Sensitivity Analysis for Unmeasured Confounding]]; designs for when you do not believe it are in [[Causal Design Selection Beyond Randomisation]].

## See Also
- [[Matching and Weighting Estimators]] — extends
- [[Covariate Balance and Overlap Checks]] — prerequisite-for
- [[Confounders, Mediators and Colliders]] — related
- [[Explain vs Predict Modelling]] — related
