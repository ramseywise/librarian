---
title: Cost-Based Decisions from a Posterior
tags: [foundations, pattern]
summary: "Turn posterior draws and explicit costs into decisions: the newsvendor quantile short/(short+over) for stock, a cost-ratio probability threshold for blocking, and expected net value with regret risk across plausible costs for a ship decision."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--04-bayesian-analysis--notes--05-loss-functions-and-decisions.md
---

# Cost-Based Decisions from a Posterior

Once costs are explicit ([[Bayes Action and Loss Functions]]), three common decisions have simple Bayes actions. All numbers below are from hypothetical costs in worked examples, not measurements.

| Decision | Loss to write down | Bayes action |
|---|---|---|
| Ship B or keep A | max(pA - pB, 0) | ship if expected loss is under epsilon ([[Bayesian A/B Testing with Expected Loss]]) |
| Inventory or capacity | stock-outs cost more than surplus | an upper quantile of the predictive distribution, not the mean |
| Fraud or risk threshold | cost of a blocked customer against a missed fraud | the probability where expected costs balance |

## Newsvendor quantile

With shortage cost per unit and overage cost per unit, the best stock is the quantile short / (short + over) of the **predictive** distribution (draw a rate from the posterior, then a count from it: see [[Posterior Predictive Checks]] for why predictive draws matter). Example: 1,200 units sold over 30 days with a Gamma posterior on the daily rate, predictive mean 40.0 and sd 6.5, running out costing 5 times a surplus unit. The critical quantile is 0.833, which gives a best stock of 46. Cost at the mean was 15.26 against 9.92 at the Bayes action, about 54% more.

## Cost-ratio threshold

Block when the expected cost of blocking is below the expected cost of allowing: P(fraud) > cost_block / (cost_block + cost_miss). With a blocked good customer costing 2 and a missed fraud 80 (hypothetical), the threshold is 0.024. At P = 0.01 blocking costs 1.98 against 0.80 for allowing; at 0.03 it flips (1.94 against 2.40); at 0.2 it is 1.60 against 16.00. If blocking cost 20 the threshold would be 20 / (20 + 80) = 0.2. A 2.4% threshold looks absurd beside a default of 0.5, but it is what the costs imply, and it depends on the probability being well calibrated (see [[Calibrated Score, Deterministic Decision Rule]]).

## Ship decision in business units

Multiply posterior draws of the lift by business numbers to get a posterior over yearly gain, then subtract cost. With the A/B posteriors of [[Bayesian A/B Testing with Expected Loss]] and hypothetical figures (480,000 visitors a year, 30 per order, 25,000 a year to maintain the redesign), the yearly gain had mean 92,906 and 95% interval [49,559, 136,395].

| Yearly cost | Expected net of shipping | P(regret shipping) |
|---|---|---|
| 25,000 | 67,906 | 0.001 |
| 45,000 | 47,906 | 0.015 |
| 60,000 | 32,906 | 0.069 |
| 90,000 | 2,906 | 0.448 |

Expected net of keeping A is 0. The decision becomes a statement others can argue with: below a yearly cost of about 93,000 shipping has positive expected value. An engineer can check the run cost and finance the order value, and neither needs a p-value. Because costs have owners, report the table across a range, not a single figure.

## Failure modes

- Using accuracy, or a 0.5 threshold, when error costs are asymmetric.
- Applying a cost to the mean outcome instead of per draw.
- Understating risk by drawing only the mean's posterior, not outcomes.

## See Also
- [[Bayes Action and Loss Functions]] — prerequisite-for
- [[Peeking Under Bayesian Stopping Rules]] — related
- [[Minimum Detectable Effect and Sample Size]] — related
