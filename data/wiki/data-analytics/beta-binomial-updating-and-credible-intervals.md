---
title: Beta-Binomial Updating and Credible Intervals
tags: [data-analytics, bayesian-analysis, concept]
summary: "The Beta prior is conjugate to a Binomial rate, so Bayesian updating is addition of counts; the posterior gives a credible interval that says what people wish a confidence interval said, and separates MLE, MAP and posterior mean."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--04-bayesian-analysis--notes--01-bayesian-inference.md
  - data/raw/papers/2026-11-08-think-bayes-ch04-more-estimation.md
---

# Beta-Binomial Updating and Credible Intervals

The question a p-value cannot answer is "how likely is it that the new version is better?", because a p-value is a statement about data assuming a hypothesis. Bayesian inference reverses it: posterior is proportional to likelihood times prior (see [[Bayes Rule and the Base Rate Fallacy]]). Today's posterior is tomorrow's prior, so belief accumulates across experiments without extra machinery.

## The update

| Piece | Choice |
|---|---|
| Unknown | theta, a rate such as P(heads) or a conversion rate |
| Prior | theta ~ Beta(a, b); Beta(1, 1) is uniform |
| Likelihood | n successes in N trials ~ Binomial(N, theta) |
| Posterior | Beta(a + n, b + N - n) |

The Beta is **conjugate** to the Binomial, so the posterior is another Beta and no sampling is needed. Read a and b as pseudo-counts: Beta(a, b) behaves as if a - 1 successes and b - 1 failures were already seen. The same update underlies [[Bayesian A/B Testing with Expected Loss]] and the shrinkage in [[Small-N Trap and Shrinkage]].

Worked numbers: a uniform prior and a fair coin. At N = 1 with one head the posterior mean is 0.667 and the 95% interval [0.158, 0.987]; at N = 500 with 277 heads the mean is 0.554 and the interval [0.510, 0.597], narrow enough that it still excludes the true 0.5. A 95% interval misses about one time in twenty, Bayesian ones included. With a Beta(4, 4) prior and 32 heads in 50 flips the posterior is Beta(36, 22): mean 0.6207, sd 0.0632. MCMC on the same model gave mean 0.6190 and sd 0.0638, which is the point of checking a sampler against a closed form (see [[MCMC and Metropolis Sampling]]).

## Three point summaries

| Summary | What it is | Beta(4, 4) prior, 32 of 50 |
|---|---|---|
| MLE | ignores the prior | 0.640 |
| MAP | the posterior's peak | 0.625 |
| Posterior mean | averages over the posterior | 0.621 |

With a flat prior the MAP equals the MLE: a frequentist procedure is a Bayesian one with a particular prior (see [[Regularisation as a Prior]]). The summaries answer different questions; [[Bayes Action and Loss Functions]] says which loss each one is optimal for.

## Credible versus confidence interval

A credible interval holds 95% of the posterior probability, so "95% probability the value is inside, given model and data" is a legitimate reading. A confidence interval only says the procedure covers the truth 95% of the time over repeats (see [[Confidence Interval Coverage and Wilson]]). At large N with a flat prior the two are numerically almost identical (credible [0.05363, 0.05802] against confidence [0.05358, 0.05798] on 2,335 conversions in 41,859 visits). At small N they differ: for 1 conversion in 20 visits the credible interval is [0.012, 0.238] while the Wald interval is [-0.046, 0.146], which leaves the possible range. The posterior cannot leave [0, 1].

## The Euro coin as a worked case

Downey's *Think Bayes* (ch. 4) spins a Belgian one-euro coin 250 times and sees 140 heads and 110 tails. On a uniform prior over 101 grid hypotheses (x from 0 to 100 percent) the maximum-likelihood value is 56, the posterior mean 55.95 and median 56, and the 90% credible interval runs from 51 to 61, leaving out 50%. Exactly x=50 gets probability 0.021, but that figure shifts with how finely the range is cut up, so a single grid point's probability should not be read as a hypothesis probability. A triangular prior peaking at 50 gave identical medians and intervals, with means differing from the uniform case by under 0.5%, so the priors were swamped, illustrated on one pair of priors and one dataset. The conjugate update is Beta(alpha + h, beta + t); from Beta(1,1) the Euro posterior mean is 56%. Cromwell's rule: assign no hypothesis prior probability 0 if it has any real chance, because its posterior then stays 0 regardless of data. For the competing hypotheses fair versus biased, see [[Bayes Factors and Composite Hypotheses]].

## Failure modes

- Reading a confidence interval as a credible one because the numbers match.
- Choosing the prior after seeing the result: it can produce any conclusion. State it, justify it, show the result under a sceptic's prior (see [[Prior Choice and Prior Predictive Checks]]).
- Zero prior mass: a DiscreteUniform capped at 2000 can never conclude more than 2000, however strong the data.
- Reporting only the posterior mean, which discards the distribution.
- Large N agreement: with a prior that does not exclude the truth, the likelihood dominates and Bayesian and frequentist answers converge. Bayesian methods earn their machinery at small N, with real prior knowledge, or when the decision needs a probability.

## Limits

- The claim that the posteriors converge rests on a single pair of priors and a single dataset.

## See Also
- [[Generative Story Models]] — extends (building the model from a data-generating story)
- [[Posterior Predictive Checks]] — extends (checking the fitted model)
- [[Maximum Likelihood and Estimator Bias]] — related (the MLE the MAP is compared with)
- [[Confidence Interval Coverage and Wilson]] — alternative-to (frequentist interval)
- [[Grid Posteriors Over Several Parameters]] — extends
- [[Predicting from a Posterior as a Mixture]] — extends
- [[Locomotive Problem: Estimators and Losses]] — related (credible interval from a grid posterior)
- [[Grid and Quadratic Approximation and Posterior Samples]] — extends
