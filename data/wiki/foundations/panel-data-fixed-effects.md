---
title: Panel Data Fixed Effects
tags: [foundations, concept]
summary: "Fixed effects remove all stable differences between units by using only within-unit variation, turning a pooled estimate of -1.0 into the true 0.5, but they absorb time-invariant variables and do not remove time-varying confounders."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--08-panel-data-and-fixed-effects.md
---

# Panel Data Fixed Effects

Panel data observe the same units repeatedly. Variance splits into **between** (units differ) and **within** (a unit changes over time). Stable unit traits confound a pooled regression; fixed effects use only within-unit change.

## Numbers

True effect 0.5. Pooled OLS gave -1.005; store effects alone -0.041; store plus week effects 0.472, and hand demeaning matches the package exactly. Over 300 panels, two-way FE coverage was 0.947 against 0 for pooled and store-only.

## Within-between model

Splitting each regressor into unit mean and deviation reproduces FE (0.4722) and adds a between effect (-1.4884) that remains confounded.

## Limits

- Time-invariant regressors are absorbed (an AbsorbingEffectError).
- Time-varying confounders survive: competitor opening gave 0.199, controlled 0.502; a manager reacting gave 0.133.
- Little within variation inflates SEs (about 20x).
- The coefficient weights units by within variance (0.901 against an unweighted average of 0.5).
- Cluster by unit when the regressor persists ([[Clustered Standard Errors]]).

## See Also
- [[Difference-in-Differences as Two-Way Fixed Effects]] — extends
- [[Staggered Rollout Bias in Two-Way Fixed Effects]] — related
- [[Pseudoreplication and Intraclass Correlation]] — related
- [[Multilevel vs Fixed Effects vs Clustered Standard Errors]] — related
