---
title: Prior Choice and Prior Predictive Checks
tags: [foundations, pattern]
summary: "A wide prior is not uninformative once a model transforms it; simulate outcomes from the prior before seeing data, pick weakly informative priors on a standardised scale, and remember priors wash out with data but a zero-mass region never does."
updated: 2026-11-04
sources:
  - data/raw/papers/2026-11-06-gelman-2009-weakly-informative-default-prior-distribution.md
  - data/raw/repos/learn-ai-engineering/data-analytics--04-bayesian-analysis--notes--03-priors-and-bandits.md
  - data/raw/repos/learn-ai-engineering/data-analytics--04-bayesian-analysis--notes--04-bayesian-ab-testing.md
---

# Prior Choice and Prior Predictive Checks

## Flat is a choice

A flat prior on a rate is not flat on the log-odds, and a wide prior on log-odds is not wide on the rate. Uniform p has a logit with sd 1.81, with 46% of its mass within plus or minus 1. A Normal(0, 10) on the logit puts 65% of mass on rates below 1% or above 99%: a strong prior that the outcome is nearly deterministic. Normal(0, 1.5) puts about none there; Cauchy(0, 2.5) puts 32%, heavy tails by design.

## Kinds of prior

| Kind | Note |
|---|---|
| Flat or objective | flat only on the scale chosen |
| Weakly informative | rules out absurd values; modern default, check on the outcome scale |
| Informative | encodes domain knowledge; defend it to a sceptic |
| Empirical Bayes | fitted from the data; double-counts if fitted on the same data, safe when fitted across a population of other units |
| Conjugate | convenience, not insight |
| Jeffreys | invariant under reparameterisation; Beta(1/2, 1/2) for a rate, piles mass at the edges |

Read a Beta as evidence claimed: Beta(3, 97) is "around 3%, give or take" (95% in [0.006, 0.071]); Beta(30, 970) has the same mean and claims ten times the evidence ([0.020, 0.041]). Use half-normal, half-Cauchy or exponential for standard deviations rather than Uniform(0, big).

## Prior predictive check

Simulate outcomes from the prior and ask whether they are believable (one call in PyMC). On the 23-launch logistic model, the probability of 0 or 23 failures was 0.29 under Normal(0, 100) priors, 0.18 under Normal(0, 5) and 0.02 under Normal(0, 1.5). The "uninformative" prior expects total failure or none nearly 30% of the time. It pairs with [[Posterior Predictive Checks]]. Revise a prior that gives nonsense: choosing it is part of model checking.

## A default for logistic regression

Scale non-binary inputs to mean 0 and sd 0.5, put independent Cauchy(0, 2.5) on coefficients and Cauchy(0, 10) on the intercept. It stays stable under complete separation (see [[Logistic Regression Separation]]): on six separated points, the flat fit's slope ran to 100.3 with P(y = 1) 1.000000 at the largest x; Normal(0, 100) gave 39.1, Normal(0, 10) gave 9.6 and 0.991752, and Cauchy(0, 2.5) gave slope 3.6 and 0.859, about what six observations are worth. Unscaled inputs make the default meaningless.

### Where the default comes from (Gelman et al., 2008)

The paper that proposed this default (published in 2008, posted to arXiv in 2009) reasons that, on standardised inputs, a move from one standard deviation below the mean to one above rarely changes the logit by more than 5, and a shift of 5 takes a probability from 0.01 to 0.50. It notes that the likelihood from half a success and half a failure looks close to a t distribution with 7 degrees of freedom and scale 2.5, and picks the heavier-tailed Cauchy as slightly more conservative. Because inputs are rescaled, interactions are shrunk harder: with plus or minus one half coding, a three-way interaction can change the logit by about 5/4 under the same prior.

Reported results (self-reported by the authors, using their bayesglm fit, which returns a posterior mode):

- A 45-dataset cross-validation (UCI sets with binary-discretised predictors, five folds) found the Cauchy scale with the best average score was 0.75, yet the authors still recommend 2.5 as a deliberately weaker, conservative choice. The best prior varied by dataset (for example a t with 4 degrees of freedom and scale 0.8 for one set, 2 degrees and scale 2.8 for another).
- Plain maximum likelihood and Jeffreys-prior fits did poorly in cross-validation; a finite-degrees-of-freedom t beat Gaussian and Laplace priors on average. The text gives no numeric margin.
- Bioassay (20 animals, four doses, deaths 0/1/3/5): the standardised-dose coefficient moved from 10.2 (standard error 6.4) to 5.4 (2.2).

Limits the authors state: standardising makes the prior depend on the data, which may be troublesome at very small sample sizes; the cross-validation scores point estimates, not full posteriors; and the corpus may not represent social-science use. The paper only discusses, without results, Poisson and other log-link models.

## The prior washes out

The log-likelihood grows with N and the log-prior does not. Flat Beta(1, 1) versus Beta(2, 10) with true rate 0.6: the posterior-mean gap was 0.333 at N = 0, 0.131 at N = 32 and 0.010 at N = 500. Priors matter most exactly when Bayesian methods matter most, at small N. They wash out toward what the data says, not the truth, and a prior with zero mass at the truth never washes out.

## A/B example

On a first day of 42 against 58 conversions per 900 visitors, a flat prior reported a 1.77-point lift with P(B > A) 0.950; a Beta(500, 9500) prior reported 0.15 points and 0.689. On the full test all agreed on the decision. Use the same prior for both arms (see [[Bayesian A/B Testing with Expected Loss]]).

## Failure modes

- Fitting the prior on the same data.
- Zero mass where the truth could be.
- Calling a wide prior uninformative without simulating outcomes.

## See Also
- [[Beta-Binomial Updating and Credible Intervals]] — prerequisite-for
- [[Regularisation as a Prior]] — extends (penalties as priors)
- [[Small-N Trap and Shrinkage]] — related (an informative prior as shrinkage)
