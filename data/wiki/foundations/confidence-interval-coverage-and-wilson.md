---
title: Confidence Interval Coverage and Wilson
tags: [foundations, concept]
summary: "A 95 percent interval is a claim about the procedure's long-run coverage, and the textbook Wald interval for a proportion fails badly for rare events at modest n where the Wilson interval holds up."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--04-estimation.md
---

# Confidence Interval Coverage and Wilson

## What the 95% means

It describes the **procedure**, not one interval: over repeated datasets, about 95% of intervals contain the true value (a simulation gave 0.948). Any single interval either contains it or does not. The statement "95% probability the truth is in this interval" needs a prior and belongs to a Bayesian credible interval.

## Wald versus Wilson for a proportion

Wald: p-hat +/- 1.96 sqrt(p-hat(1-p-hat)/n). It is centred on the estimate and assumes the SE from that same estimate is reliable. When successes are rare it is not.

- 0 conversions in 50: Wald gives [0, 0], claiming certainty from nothing. Wilson gives [0, 0.0714].
- True p = 0.02, n = 50: Wald coverage 0.633, Wilson 0.920.
- At n = 4,000 the two are indistinguishable.

Wilson inverts the test rather than plugging in the estimate, so it never collapses to a point and stays inside [0, 1]. Default to Wilson for proportions; the cost is nil at large n.

## Uses

- Ranking by the Wilson lower bound rewards evidence, not a lucky small sample ([[Small-N Trap and Shrinkage]]).
- Error bars on eval pass rates ([[Eval Error Bars and Sample Size]]).
- Checking an interval's coverage by simulation is the general test of any interval method ([[Data Generating Process Simulation Check]]).

## Failure modes

Coverage assumes independent rows ([[Pseudoreplication and Intraclass Correlation]]) and a representative sample ([[Data Defect Correlation]]); intervals from a skewed mean need large n ([[CLT on Heavy-Tailed Metrics]]).

## See Also
- [[Maximum Likelihood and Estimator Bias]] — prerequisite-for
- [[Bootstrap Resampling and Its Failures]] — alternative-to (an interval without a formula)
- [[Minimum Detectable Effect and Sample Size]] — related
- [[Eval Error Bars and Sample Size]] — related
