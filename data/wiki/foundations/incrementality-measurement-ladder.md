---
title: Incrementality Measurement Ladder
tags: [foundations, pattern]
summary: "Rank marketing evidence by what it can claim: attribution shares credit, a geo test measures the average return over a tested spend change, and a media mix model with adstock and saturation estimates marginal returns, which budgets move on."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--06-applied-analyses--notes--09-marketing-measurement.md
---

# Incrementality Measurement Ladder

Incrementality is the difference a channel makes compared with the same world without it. Three rungs, in order of what each can claim.

1. **Attribution** ([[Attribution Credit vs Causal Share]]): accounting; no counterfactual.
2. **Geo test**: switch the channel off in randomly chosen areas (20 areas in 10 pairs, 8 weeks). For each pair, grow the holdout's earlier revenue by its control's growth to get the revenue it would have earned; incremental ROAS = revenue lost / spend saved. Estimate 1.491 (pair bootstrap 95% 1.43 to 1.57) against true 1.524; over 12 seeds mean error 0.002, sd 0.044. It is clean and causal but narrow: it covers the first 2,510 of weekly spend, while spend had risen to about 7,300.
3. **Media mix model (MMM)**: regress revenue on transformed spend plus trend and seasonality; correlational.

## Adstock and saturation
Adstock is carryover (geometric decay, rate alpha: with 0.30 a 1,000 spend week gives 700, 210, 63 ... ; with 0.60 it gives 407, 244, 146 ...). Saturation is diminishing returns, a Hill curve (ceiling beta, half-ceiling spend K, slope). Average ROAS is revenue per unit spend; marginal ROAS is the return on the next unit, and budgets move on the marginal. At 7,300 a week paid social had average ROAS 1.31 but marginal 0.71 (at 13,000: 0.93 and 0.27).

## Why MMMs are hard
Few data points (157 weeks, about 31 parameters, about five per parameter against a suggested 7 to 10); correlated inputs (paid social and email spend correlated -0.72); and average ROAS needs extrapolation to zero spend, where there is no data, so a model can give a fair marginal and a poor average. Plain regression called email worth 0.46 against a true 2.89. With default priors the average ROAS for paid social was 2.71 (true 1.29) and email 20.36 (true 4.0) while paid social's marginal was about right (0.80 vs 0.71). Priors largely decide the posterior with small samples; in published simulations response curves were biased by up to about 40% with two years of weekly data and about 10% with sixty. High R^2 is not evidence: five models with R^2 of 0.98 to 0.99 disagreed by up to 50%. Use posterior samples, not posterior means, in nonlinear formulas, and read R-hat and divergences (a default sampler gave R-hat up to 1.6; tuned settings about 1.04).

## Adding the geo test
A lift-test measurement adds a likelihood term pinning the curve's average return over the tested change. Paid social's average ROAS tightened to 1.37 (1.23 to 1.51) against a true 1.29, but its marginal stayed as wide (0.86, 0.62 to 1.08 vs 0.71) and untested channels barely moved. The test fixes the average over its range and leaves the slope above it to the curve.

## Moving the budget
Moving a weekly 500 to 1,000 from paid social to email gave a true gain of 905 to 1,232 a week and the model's probability of gain was 0.98 or higher; at 2,000 the truth was +1,049 but the model +205 (66% chance); at 4,000 both lost money. The truth's best split of the same total moved about 1,100 out of paid social and 1,300 into email for about 1,280 more revenue a week, a ceiling.

Larger question: gross margin was 61%, so a unit of spend pays for itself at revenue ROAS 1.63; paid social's marginal (0.71) and even the geo test's 1.49 sit below it, so whether total spend should fall matters more than reallocation, unless the revenue series omits later orders.

## Recommendations
Test at today's spend with partial cuts (for example from about 7,300 to about 5,000), test the least-known channel, and defer total-spend decisions until then.

## See Also
- [[Attribution Credit vs Causal Share]] — prerequisite-for
- [[BG/NBD Customer Lifetime Value]] — related
- [[Campaign Breakeven and Uplift Holdout]] — related
- [[Bootstrap Resampling and Its Failures]] — related
