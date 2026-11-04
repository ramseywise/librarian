---
title: Data Generating Process Simulation Check
tags: [foundations, pattern]
summary: "Before trusting an analysis, simulate data from a known process, run the estimator, and report bias, spread and coverage; a placebo run with a true zero effect exposes a model that invents effects."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--07-data-generating-process.md
---

# Data Generating Process Simulation Check

## Triple

Name the **estimand** (what you want), the **estimator** (the recipe) and the **estimate** (the number). The data generating process (DGP) links them. Write the DGP as code with a known true value, fit your model to many simulated datasets, and report:

- **bias** (mean estimate minus truth),
- **SD** (spread of estimates),
- **coverage** (how often the interval holds the truth).

## Placebo test

Set the true effect to zero and fit. A sound analysis finds nothing. A linear control on a curved confounder found an effect of 0.48 in 100% of datasets; a quadratic found a spurious effect in 6.0% (close to the nominal 5%). See [[Functional Form Misspecification]].

## Defining the estimand

The effect on log spend was 0.20, a 22.1% lift. In currency terms it depends on who: 15.29 for all customers against 18.98 for customers who received the coupon. State whose effect and on what scale before estimating.

## Uses

Check any interval ([[Confidence Interval Coverage and Wilson]]), any standard error ([[Clustered Standard Errors]]), selection into the sample ([[Data Defect Correlation]]), and model choice ([[Model Selection Criteria]]).

## See Also
- [[Explain vs Predict Modelling]] — related
- [[External Validity and Transportability]] — related
- [[Maximum Likelihood and Estimator Bias]] — prerequisite-for
