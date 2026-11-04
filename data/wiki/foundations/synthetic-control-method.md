---
title: Synthetic Control Method
tags: [foundations, pattern]
summary: "With one treated unit and many untreated donors, fit non-negative weights summing to one on the pre-period so the weighted donors track the treated unit, then read the post-launch gap; inference comes from placebo runs, not conventional standard errors."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--03-experimentation-and-causality--notes--04-correlation-and-causation.md
---

# Synthetic Control Method

One city gets a policy. No single other city matches, but a weighted mix may. Fit non-negative weights summing to one on the pre-period (a constrained optimisation), build the synthetic series, and compare after launch.

## Numbers

Simulation: 12 donors, 36 months, launch at month 24, true effect 2.00. The largest donor weights were 0.55, 0.21, 0.14 and 0.05 (the three donors used to generate the city carried most weight); pre-launch fit RMSE 0.17; estimated effect 2.01. A naive before/after in the city gave 6.09.

## Properties

- Weights are sparse and readable, an advantage over a regression with many controls.
- Needs a long pre-period; assumes the pre-period fit carries forward.
- With a single treated unit conventional standard errors do not apply. Treat each donor in turn as if it had been treated (placebo runs) and ask whether the real gap is unusually large.

## See Also
- [[Causal Design Selection Beyond Randomisation]] — related
- [[Difference-in-Differences as Two-Way Fixed Effects]] — alternative-to
