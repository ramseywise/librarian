---
title: Shifted Beta Geometric Retention Model
tags: [foundations, concept]
summary: The sBG gives each customer a constant per-period churn probability drawn from a beta distribution, so aggregate retention rises with age without anyone becoming loyal, and it extrapolates a cohort's survival far better than curve fits.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--06-applied-analyses--notes--03-cohort-and-retention.md
---

# Shifted Beta Geometric Retention Model

Projecting a young cohort's two-year survival from a few months of data is the common need. Fitting an exponential, linear or quadratic curve to early points fails because they describe shape without a reason, and the fit in the calibration window says nothing about extrapolation. On a seven-year subscription dataset the linear and exponential curves fell short of year-12 survival by 81% and 30% and a quadratic overshot by 92%.

## The model

- Each customer leaves with constant probability theta each period (geometric lifetime).
- theta varies across customers, beta(alpha, beta).
- Survival S(t) = B(alpha, beta + t) / B(alpha, beta); retention rate r(t) = (beta + t - 1) / (alpha + beta + t - 1).

## The ruse of heterogeneity

Each individual's chance of staying is constant, yet the aggregate retention rate **rises** with t: likely leavers go first and the remainder are the sort who stay. An improving retention rate in an old cohort is therefore not evidence the product is improving. In the worked fit the modelled retention rate was 0.849 at month 1, 0.928 at month 6, 0.956 at month 12.

## Fit and check

Maximum likelihood on the aggregate survival curve. Replicating a published fit: one segment reproduced exactly (alpha 0.704, beta 1.182); for the other, the paper's printed alpha of 0.688 looks like a typo, since 0.668 fits the printed data better at the printed beta. Year-12 forecasts calibrated on seven years were off by about 4% and 2%, five years beyond the data, with two parameters. (The paper calls these overestimates; the replication gave errors of the same size below the actuals, unresolved.)

On a simulated retailer, calibrated on months 0-6 (alpha 0.689, beta 3.883): month 24 actual 0.238, sBG 0.251, exponential 0.087. Calibrated on only months 0-3 the sBG gave 25.8%, degrading gently, while the exponential fell to 5.3%. Caveat: the generator's churn was beta by construction, which flatters the sBG; the published replication is the real evidence.

## Applicability

Needs observed lifetimes (contractual settings). Non-contractual retail never observes churn, only silence; use Pareto/NBD or BG/NBD, or a repeat window as proxy.

## See Also
- [[Cohort Retention Triangle]] — prerequisite-for
- [[BG/NBD Customer Lifetime Value]] — alternative-to (non-contractual setting)
- [[Survival Analysis for Customer Lifetimes]] — related
- [[Maximum Likelihood and Estimator Bias]] — related
