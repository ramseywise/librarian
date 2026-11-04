---
title: Bayesian A/B Testing with Expected Loss
tags: [foundations, pattern]
summary: "Draw from each arm's Beta posterior to get P(B > A), the lift interval and expected loss; ship when expected loss is below the smallest difference you care about, and report the lift size, since P(B > A) alone says nothing about it."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--04-bayesian-analysis--notes--04-bayesian-ab-testing.md
  - data/raw/repos/learn-ai-engineering/data-analytics--04-bayesian-analysis--notes--05-loss-functions-and-decisions.md
---

# Bayesian A/B Testing with Expected Loss

The question changes from "how surprising is this data if the arms were equal?" to "given the data, what is P(B > A), and what do we lose if we are wrong?". Conversion data is Binomial and the Beta is conjugate ([[Beta-Binomial Updating and Credible Intervals]]), so each arm's posterior is exact and sampling both is fast enough for every dashboard refresh. Unequal arm sizes need no correction: a sampled model with B at half the traffic gave a wider posterior for B (sd 0.0078 against 0.0049).

## Worked numbers

1,000 visitors per arm, 120 against 140 conversions, uniform prior: P(B > A) 0.908 (an exact finite sum gives 0.9079); relative lift 95% interval [-0.07, 0.462]; loss if choosing B 0.00064, if choosing A 0.02058.

A full test with 2,079 of 42,141 on A and 2,335 of 41,859 on B: P(B > A) 0.99999; lift interval [+0.34, +0.95] points; loss if shipping B 0.000001 points, keeping A 0.645 points; P(lift > 0.5 points) 0.827; P(lift > 1.0 point) 0.011. The business case uses the last pair, which a p-value cannot state. The credible interval matches the frequentist confidence interval numerically at this size and flat prior; only the permitted reading differs.

One simulated draw reversed the truth (A truly better but B observed higher, P(A better) about 0.17). That is a correct report of the data and a wrong guess about the world, which is why sample-size planning still matters (see [[Minimum Detectable Effect and Sample Size]]).

## Expected loss as the rule

E[loss given B] = E[max(p_A - p_B, 0)]: the average rate given up by shipping B, counting only worlds where A was better.

| Rule | Ship B when |
|---|---|
| Probability | P(B > A) above 0.95 |
| Expected loss | E[loss given B] below epsilon, the smallest difference you care about |
| Interval | 95% lift interval excludes 0 |

The loss rule stops early when B is clearly better and also when the arms are so close that choosing wrong is cheap; it keeps running only while the choice matters. The cost of a wrong call in business units is worked in [[Cost-Based Decisions from a Posterior]]; stopping behaviour is in [[Peeking Under Bayesian Stopping Rules]].

## Priors for tests

Beta(1, 1) is fine after a few hundred visitors per arm; a weakly informative historical prior such as Beta(5, 95) stabilises early days; a strong one such as Beta(500, 9500) demands real evidence. Use the same prior on both arms: it encodes what you knew about rates, not which arm you hope wins. See [[Prior Choice and Prior Predictive Checks]].

## Failure modes

- Reading P(B > A) as the size of the win.
- Different priors per arm.
- Flat prior on day one: 1.77-point lift on 900 visitors per arm.
- Using the probability when the change costs money.
- Ignoring novelty effects and guardrail metrics: the posterior only answers what was measured.

## See Also
- [[P-Value Misreadings]] — alternative-to (frequentist reading of the same data)
- [[Peeking Under Bayesian Stopping Rules]] — extends
- [[Thompson Sampling and Bandit Regret]] — alternative-to (adaptive allocation)
- [[Ranking by Lower Credible Bound]] — related
