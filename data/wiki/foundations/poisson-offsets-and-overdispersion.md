---
title: Poisson Offsets and Overdispersion
tags: [foundations, pattern]
summary: "Model rates by adding log exposure as an offset in a log-link count model, then check dispersion: when variance exceeds the mean the Poisson standard error is too small by a factor of three and robust or negative binomial errors are needed."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--06-regression-and-glms.md
---

# Poisson Offsets and Overdispersion

## Offsets

Counts depend on how long units were observed. A log-link model with `log(exposure)` as an **offset** (a term with its coefficient fixed at 1) models the rate per unit time. Exponentiated coefficients are rate ratios: 1.092 against a true 1.105 in the example. Dropping the offset when one arm was observed longer gave a ratio of about 1.82, measuring exposure as well as behaviour.

## Overdispersion

Poisson assumes variance equals the mean. Compute Pearson chi-square over residual df each time you fit one; 1.00 is fine. In the overdispersed example it was 8.3 and the SEs were:

| Fit | SE |
|---|---|
| Poisson | 0.0155 |
| Poisson with robust (HC1) errors | 0.0509 |
| Negative binomial | 0.0444 |

The Poisson SE understated uncertainty by over 3x and would call the effect highly significant when the robust test does not. Either keep Poisson with robust errors (valid for the mean model) or fit a negative binomial, which models the extra variance.

## See Also
- [[Generalised Linear Models and Deviance]] — prerequisite-for
- [[Robust Standard Errors]] — related
- [[Distribution Selection for Metrics]] — related
