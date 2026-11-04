---
title: "Counterfactual Evaluation with Inverse Propensity Scoring"
tags: [foundations, pattern]
summary: "Logs only record what the old system showed; inverse propensity scoring reweights logged events by one over the logging probability to estimate an unshipped policy's value, at the price of variance, so log propensities, keep some randomisation and report effective sample size."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--05-time-series-and-recommenders--notes--03-two-tower-and-evaluation.md
---

# Counterfactual Evaluation with Inverse Propensity Scoring

All offline numbers share a flaw: interaction logs record what people did with what the old system showed them. Offline experiments assume users would have behaved the same under a new algorithm, so an algorithm that recommends very different things gets little credit.

## IPS

If the logging system randomised and recorded its action probabilities, reweight each logged event in which the new policy agrees with the logged action by 1 / (logging probability). **Self-normalised IPS** divides by the sum of weights instead of the event count. A classic application replayed 33 million news-front-page events logged under uniform random choice and reported a 12.5% click lift over a context-free bandit.

## Simulated check (truth known)

200,000 events, 20 actions, 5 user segments, a logger favouring overall winners (uniform share 0.2), and a personalised policy never shipped:

| Estimate | CTR |
|---|---:|
| True value of new policy | 0.2162 |
| Logged CTR (old policy) | 0.0801 |
| Naive: CTR on matching events (14,908 events) | 0.2955 |
| IPS | 0.2190 |
| Self-normalised IPS | 0.2161 |

The naive estimate overstates by more than a third because matching events skew towards actions the logger favoured. The cost: largest weight 100, effective sample size about 3,237 of 200,000 (computed as sum(w)^2 / sum(w^2)). Cutting the logger's uniform share from 0.2 to 0.02 dropped ESS to 332, raised the largest weight to 1,000, and moved IPS to 0.2037 and SNIPS to 0.2055: both then miss by about 5% with nothing in the point estimate to warn you. Log the ESS and largest weight.

## Pitfalls

- Bandit logs without recorded propensities make IPS unavailable later; design for it early.
- A few tiny-propensity events can dominate: clip, self-normalise, report ESS.

## Where it sits: the evaluation ladder

Full-catalogue offline metrics (cheap, biased by logs), then counterfactual estimates, then a small live ramp (guardrails, latency, bugs), then an A/B test on the outcome, then a long-term holdout for slow effects. Only a controlled experiment makes the counterfactual real, and live results are not always correlated with offline ones. Sample size per arm is roughly 2(z_a + z_b)^2 p(1-p) / delta^2: with two-sided 5% and 80% power, 5% baseline and 5% relative lift takes 121,987 users per arm, a 1% lift on 5% takes 2,993,309, and a 1% lift on 30% takes 366,909. Pick outcomes beyond the click (retention, watch time) because clicks can be moved by clickbait, and watch for interference since treated and control users share one catalogue and training pipeline. See [[Minimum Detectable Effect and Sample Size]] and [[Peeking and Sequential Testing]].

## See Also
- [[Sampled Ranking Metrics and MRR]] — prerequisite-for
- [[Minimum Detectable Effect and Sample Size]] — related
- [[Peeking and Sequential Testing]] — related
- [[Thompson Sampling and Bandit Regret]] — related
