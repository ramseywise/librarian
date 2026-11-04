---
title: Regularisation as a Prior
tags: [foundations, concept]
summary: "Ridge is the MAP estimate under a Normal prior and lasso the MAP under a Laplace prior, with penalty strength equal to prior precision; lasso's exact zeros come from the MAP's geometry, not from a Bayesian belief in sparsity."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--04-bayesian-analysis--notes--03-priors-and-bandits.md
---

# Regularisation as a Prior

| Frequentist | Bayesian equivalent |
|---|---|
| Ordinary least squares | maximum likelihood, flat prior on each coefficient |
| Ridge (L2 penalty) | MAP with a Normal(0, tau) prior on each coefficient |
| Lasso (L1 penalty) | MAP with a Laplace prior on each coefficient |
| Penalty strength lambda | prior precision; tighter prior means larger lambda |

With unit noise, a Normal(0, tau) prior corresponds to a ridge penalty of 1/tau^2, so Normal(0, 1) against Normal(0, 10) differs by a factor of 100 in lambda. A Laplace prior of scale b matches a lasso penalty of 1/b (scikit-learn divides the loss by n, hence alpha = 1 / (n * scale)).

## Checking it

60 rows, 6 inputs, only 2 matter. With tau = 0.3 the MAP and ridge agree: [1.263, -0.979, -0.114, 0.115, -0.092, -0.088] against ridge with the last at -0.089. With Laplace scale 0.1, lasso and MAP both zero out the same coefficients (lasso [1.349, -0.987, 0, 0.006, 0, 0]). But the posterior mean under the same prior is not sparse (for example -0.053, 0.065, -0.047, -0.038 on the null coefficients), and none of 24,000 draws was exactly zero. If you want a Bayesian to say "this coefficient is zero", the Laplace prior is not doing it; use the MAP and say so.

## Why it matters

Shrinkage toward zero is shrinkage toward a prior mean, the same mechanism as in [[Small-N Trap and Shrinkage]] and, across many groups, [[Partial Pooling and Multilevel Models]]. A weakly informative prior stabilises estimates that maximum likelihood cannot (see [[Prior Choice and Prior Predictive Checks]]).

## Shrinking selected winners

Across 2,000 simulated experiments with true lifts Normal(0, 0.2) and standard error 0.3, 91 were significant and their mean observed lift was 0.759 against a true 0.246. Estimating the prior from the whole population (sd 0.192, shrink factor 0.290) and multiplying each estimate by that factor brought the winners' mean to 0.220. This is empirical Bayes in the safe form: the prior comes from a population in which one experiment is a tiny share, so its data is not meaningfully counted twice. It relies on known noise and a really Normal population (see [[Winner's Curse]]).

## See Also
- [[Prior Choice and Prior Predictive Checks]] — prerequisite-for
- [[Winner's Curse]] — related (the inflation shrinkage removes)
- [[Logistic Regression Separation]] — related
