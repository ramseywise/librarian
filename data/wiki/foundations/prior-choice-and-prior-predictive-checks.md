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

## Flatness depends on the scale

Uniform on a rate becomes a bell-shaped logit (sd 1.81, 46% of mass within one unit of zero), and a very diffuse logit prior piles up at the extremes of the rate. Normal(0, 10) on the logit puts 65% of its mass below 1% or above 99%, which asserts near-determinism. Normal(0, 1.5) puts about none there, and Cauchy(0, 2.5) puts 32% by virtue of its heavy tails.

## Kinds of prior

| Kind | Note |
|---|---|
| Flat or objective | flat only on the scale chosen |
| Weakly informative | rules out absurd values; modern default, check on the outcome scale |
| Informative | encodes domain knowledge; defend it to a sceptic |
| Empirical Bayes | fitted from the data; double-counts if fitted on the same data, safe when fitted across a population of other units |
| Conjugate | convenience, not insight |
| Jeffreys | invariant under reparameterisation; Beta(1/2, 1/2) for a rate, piles mass at the edges |

Treat a Beta as a statement of how much evidence you hold. Beta(3, 97) says roughly 3% with a 95% interval of 0.006 to 0.071, while Beta(30, 970) keeps the mean yet asserts ten times the data (0.020 to 0.041). For standard deviations, prefer half-normal, half-Cauchy or exponential to Uniform(0, big).

## Prior predictive check

Draw outcomes from the prior alone and judge whether they look plausible (a single call in PyMC). On the 23-launch logistic model, the chance of 0 or 23 failures was 0.29 with Normal(0, 100) priors, 0.18 with Normal(0, 5) and 0.02 with Normal(0, 1.5). The "uninformative" prior thus expected all-or-nothing outcomes almost 30% of the time. Pair it with [[Posterior Predictive Checks]], and revise any prior that yields nonsense, since prior choice is part of model checking.

## A default for logistic regression

Rescale numeric inputs to mean 0 and sd 0.5, then place Cauchy(0, 2.5) priors, independent across coefficients, with Cauchy(0, 10) on the intercept. It remains stable under complete separation (see [[Logistic Regression Separation]]): on six separated points the flat fit's slope reached 100.3 with P(y = 1) of 1.000000 at the top x; Normal(0, 100) gave 39.1, Normal(0, 10) gave 9.6 and 0.991752, and Cauchy(0, 2.5) gave a slope of 3.6 and 0.859, roughly what six observations justify. Without the rescaling the default means little.

### Where the default comes from (Gelman et al., 2008)

The paper that proposed this default (published in 2008, posted to arXiv in 2009) argues that on standardised inputs, moving across two standard deviations seldom shifts the logit by over 5, and a logit shift of 5 moves a probability from about 1% to 50%. It observes that the likelihood given half a success and half a failure resembles a t distribution (7 degrees of freedom, scale 2.5), and chooses the heavier-tailed Cauchy as slightly more conservative. Because inputs are rescaled, interactions are shrunk harder: with plus or minus one half coding, a three-way interaction can change the logit by about 5/4 under the same prior.

Reported results (self-reported by the authors, using their bayesglm fit, which returns a posterior mode):

- A 45-dataset cross-validation (UCI sets with binary-discretised predictors, five folds) found the Cauchy scale with the best average score was 0.75, yet the authors still recommend 2.5 as a deliberately weaker, conservative choice. The best prior varied by dataset (for example a t with 4 degrees of freedom and scale 0.8 for one set, 2 degrees and scale 2.8 for another).
- Plain maximum likelihood and Jeffreys-prior fits did poorly in cross-validation; a finite-degrees-of-freedom t beat Gaussian and Laplace priors on average. The text gives no numeric margin.
- Bioassay (20 animals, four doses, deaths 0/1/3/5): the standardised-dose coefficient moved from 10.2 (standard error 6.4) to 5.4 (2.2).

Limits the authors state: standardising makes the prior depend on the data, which may be troublesome at very small sample sizes; the cross-validation scores point estimates, not full posteriors; and the corpus may not represent social-science use. The paper only discusses, without results, Poisson and other log-link models.

## The prior washes out

Data contribute more to the log-likelihood as N rises while the log-prior stays fixed. Comparing flat Beta(1, 1) with Beta(2, 10) at a true rate of 0.6, the posterior means differed by 0.333 at N = 0, 0.131 at N = 32 and 0.010 at N = 500. So priors count most at small N, where Bayesian methods are most needed. Posteriors converge to what the data say rather than to the truth, and a prior giving the truth zero mass never recovers.

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
