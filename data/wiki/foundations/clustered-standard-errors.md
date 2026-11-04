---
title: Clustered Standard Errors
tags: [foundations, pattern]
summary: "When rows share a group that was randomised or shares shocks, cluster the standard errors at that level: ignoring it understated the SE by half and inflated the false-positive rate to 28 percent, and it still fails with few clusters."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--06-regression-and-glms.md
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--08-panel-data-and-fixed-effects.md
---

# Clustered Standard Errors

## Rule

Cluster at the level at which treatment was assigned (or errors correlate): users, stores, schools. Rows within a cluster are not independent ([[Pseudoreplication and Intraclass Correlation]]), so the effective sample is closer to the cluster count.

## Numbers

Group-randomised example: naive SE 0.0411, clustered SE 0.0781. Under a true null, the naive false-positive rate was 27.8% against 3.5% clustered. In the panel setting, clustering mattered when the regressor persisted over time: coverage 0.697 naive against 0.940 clustered ([[Panel Data Fixed Effects]]).

## Limits

- **Few clusters:** the cluster-robust formula needs many; with 5 clusters about 21% of true nulls were rejected. "Few" can mean under 20 to under 50.
- **It fixes the SE, not the estimate.** If a group effect correlates with the predictor the coefficient itself is biased; use fixed effects or a multilevel model.
- Cluster for the unit of randomisation, not the finest available grouping.

A resampling alternative is the cluster bootstrap ([[Bootstrap Resampling and Its Failures]]), and ratio metrics need the same thinking ([[Delta Method for Ratio Metrics]]).

## See Also
- [[Robust Standard Errors]] — extends (for correlated rather than unequal-variance errors)
- [[Independence Pitfalls]] — related
- [[Regression Covariate Adjustment]] — related
