---
title: Logistic Regression Separation
tags: [foundations, pattern]
summary: "When a feature perfectly predicts the outcome, maximum likelihood diverges, giving a huge coefficient and an absurd standard error; a penalty or weakly informative prior stabilises it."
updated: 2026-11-04
sources:
  - data/raw/papers/2026-11-06-gelman-2009-weakly-informative-default-prior-distribution.md
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--06-regression-and-glms.md
---

# Logistic Regression Separation

If some value of a regressor always occurs with one outcome, the likelihood keeps improving as the coefficient grows, so the fit has no finite maximum. Symptoms: coefficient 28.52 with SE 171,433 in the example, a warning from the optimiser, and a meaningless p-value.

## Fixes

- A **ridge penalty**: coefficient 4.92 in the example, finite and usable.
- A weakly informative prior does the same job from a Bayesian side. Gelman and colleagues (2008) report two cases (self-reported): in a US vote-choice regression fitted separately for each election from 1952 to 2000, every Black respondent in 1964 voted Democrat, so the flat fit diverged while Cauchy, t7 and normal priors of scale 2.5 stabilised 1964 and left other years essentially unchanged; and in an HIV viral-load imputation model one coefficient was -20.99 with standard error 888.74 under classical glm and -6.74 (1.22) under their Cauchy-prior fit. They argue that dropping the offending predictor discards the strongest one, and that always getting a finite answer could mask non-identifiability, so they suggest also fitting by maximum likelihood.
- Collapse or drop the categories involved (and ask whether the perfect prediction is a leak).

Never read the unpenalised coefficient: the optimiser has stopped, not found an answer. The likelihood basis is in [[Maximum Likelihood and Estimator Bias]]; the odds-ratio reading in [[Logistic Regression Odds Ratios vs Marginal Effects]].

## See Also
- [[Generalised Linear Models and Deviance]] — related
- [[Small-N Trap and Shrinkage]] — related (shrinkage as a stabiliser)
- [[Prior Choice and Prior Predictive Checks]] — related (a weak prior stabilises separated fits)
