---
title: Posterior Predictive Checks
tags: [foundations, pattern]
summary: "A precise posterior can still be wrong; simulate new datasets from the fitted model and compare them with the real data on a quantity the model was not tuned to match, ideally also reporting the whole probability band rather than a line."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--04-bayesian-analysis--notes--01-bayesian-inference.md
  - data/raw/repos/learn-ai-engineering/data-analytics--04-bayesian-analysis--notes--03-priors-and-bandits.md
---

# Posterior Predictive Checks

Convergence diagnostics say the sampler worked, not that the model describes the world. A **posterior predictive check** draws new datasets from the fitted posterior and asks whether they look like the observed one. Its pre-fit twin is the prior predictive check in [[Prior Choice and Prior Predictive Checks]], which asks the same question before seeing outcomes.

## Example: a logistic model of launch damage

Twenty-three launches with a temperature and a damage flag (7 failures, mean temperature 69.6) were fitted with a logistic regression on standardised temperature, normal priors with sd 5, 1,000 NUTS draws per chain after 1,000 of tuning. P(slope < 0) was 0.9985.

The failure probability is a band, not a line:

| Temperature (F) | Mean | 95% interval |
|---|---|---|
| 31 | 0.989 | [0.900, 1.000] |
| 65 | 0.515 | [0.226, 0.821] |
| 80 | 0.036 | [0.000, 0.174] |

Reading 65 F as "about 50%" hides that the data allow anything from about one in four to four in five. Because 31 F is 22 F below the coldest launch, the narrow band there is conditional on the logistic form continuing; nothing tested it.

## The check

Simulated total failures averaged 7.04 (95% interval 3 to 12) against 7 observed, but the fit is built to match totals, so that is a weak test. The check to trust splits on something not tuned: below 65 F the model expected a mean of 3.25 failures against 4 of 4 observed; at 65 F and above it expected 3.80 against 3 of 19. That is close given the sample. A rough **separation plot** sorts launches by predicted probability with 1 marking a real failure; a good model piles the 1s on the right. Here most do, but three sit among warm launches where few were expected: the model is useful, not sharp.

## When to use it

Every fitted model, on a statistic that is not the fitting objective. Report the band at the decision point, mark the observed range of the data, and do not extrapolate with a confident interval.

## See Also
- [[Beta-Binomial Updating and Credible Intervals]] — prerequisite-for (the posterior being checked)
- [[Prior Choice and Prior Predictive Checks]] — related (the same check before fitting)
- [[Model Selection Criteria]] — related
- [[Data Generating Process Simulation Check]] — related
