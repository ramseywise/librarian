---
title: Thompson Sampling and Bandit Regret
tags: [foundations, pattern]
summary: "Thompson sampling draws one sample from each arm's posterior and pulls the highest, so exploration is automatic and fades with evidence; regret measures the cost, and which rule wins depends on the gaps and horizon, so simulate your own."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--04-bayesian-analysis--notes--03-priors-and-bandits.md
  - data/raw/repos/learn-ai-engineering/data-analytics--04-bayesian-analysis--notes--04-bayesian-ab-testing.md
---

# Thompson Sampling and Bandit Regret

An A/B test is a bandit that explores uniformly until a fixed N and then exploits. A bandit reallocates traffic as it learns.

## Algorithm

Each round: draw X_b from each arm's Beta(1 + wins_b, 1 + losses_b); pull the arm with the largest draw; update that arm. Uncertain arms yield widely spread draws, so they still win sometimes; losers are chosen at a decreasing rate, never discarded. With true rates 0.85, 0.60, 0.75, 1,000 pulls gave [926, 26, 48] and posterior sds [0.011, 0.091, 0.061]: just enough learning about the losers to stop paying for more.

## Regret

Regret is the cumulative gap between the best arm's rate and the chosen arm's. Any good strategy's regret grows at least logarithmically in horizon, and Thompson sampling and Bayes-UCB (a rising posterior quantile) both achieve that for binary rewards. Simulated on rates 0.15, 0.20, 0.10 with 300 runs:

| Rule | Regret at 100 | at 500 | at 2000 |
|---|---|---|---|
| random | 5.0 | 24.9 | 100.0 |
| max posterior mean | 2.9 | 8.8 | 28.3 |
| 95% upper bound | 3.3 | 8.6 | 14.6 |
| Thompson | 3.8 | 12.4 | 22.8 |

Random pays at a constant rate. Here the plain 95% bound beat Thompson over this horizon. Do not read it as a ranking: the order depends on gaps and horizon, and 300 runs are noisy. Thompson's appeal is no quantile to choose and direct extension to the variants below.

## Extensions

- Minimise: take argmin of draws.
- Non-stationary arms: decay evidence with a rate below 1 (wins = rate * wins + result). Two arms swapping rates halfway through 4,000 pulls: reward per pull 0.162 with no forgetting, 0.179 with rate 0.99, about 10% more. Forgetting costs a little when the world is stationary.
- Comment ranking: each item an arm with Beta(1 + up, 1 + down); sample a score per item per page load and sort, so new items still get seen (see [[Ranking by Lower Credible Bound]]).

## Bandit or fixed test?

Use a bandit when showing a loser is costly, arms change or there are many. Use a fixed-horizon test when you must report an unbiased effect, make a one-off decision or read guardrail metrics: adaptive allocation starves the early-looking-bad arm, so its estimate stays noisy and tends to stay low. A week-long price test with weekend effects confounds timing with price; a fixed split over whole weeks is the honest answer.

## See Also
- [[Bayesian A/B Testing with Expected Loss]] — alternative-to (fixed allocation)
- [[Beta-Binomial Updating and Credible Intervals]] — prerequisite-for (the arm posterior)
- [[Gaussian Processes and Bayesian Optimisation]] — related (explore versus exploit with a surrogate)
