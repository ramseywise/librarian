---
title: Ranking by Lower Credible Bound
tags: [foundations, pattern]
summary: "Sort items with few observations by a low percentile of each item's Beta posterior instead of the raw ratio, so 1 upvote with 0 downvotes cannot outrank 999 and 1; the same fix applies to star ratings and to LLM prompts compared on eval pass rate."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--04-bayesian-analysis--notes--04-bayesian-ab-testing.md
---

# Ranking by Lower Credible Bound

Sorting by raw ratio puts 1 upvote and 0 downvotes (100%) above 999 and 1 (99.9%): the small-N trap from [[Small-N Trap and Shrinkage]]. Give each item a Beta(1 + successes, 1 + failures) posterior and sort by its 5th percentile, the 95% least plausible value. An item ranks high only if we are confident its ratio is high.

## Computing it

A Normal approximation, a/(a + b) - 1.65 * sqrt(ab / ((a + b)^2 (a + b + 1))) with a = 1 + up, b = 1 + down, is close to the exact percentile except at the smallest counts:

| Up / down | Raw | Normal bound | Exact 5th pct |
|---|---|---|---|
| 999 / 1 | 0.999 | 0.996 | 0.995 |
| 60 / 40 | 0.600 | 0.518 | 0.517 |
| 6 / 4 | 0.600 | 0.358 | 0.350 |
| 1 / 0 | 1.000 | 0.278 | 0.224 |

At 1 / 0 the posterior is very skewed, so prefer the exact beta percentile. A sampler is only needed if the model is not conjugate (NUTS gave 0.357 for 6 / 4). Star ratings: map n stars of N to n/N, sum scores into S, use a = 1 + S, b = 1 + (count - S): seven ratings with S = 6.20 have a lower bound of 0.591.

## Where else

Products by rating, sellers by on-time delivery, ads by click-through, and LLM prompts or models by eval pass rate. Prompt A passes 19 of 20 (raw 0.950, lower bound 0.810); prompt B 170 of 200 (raw 0.850, lower bound 0.805). A 95% on a small suite does not yet beat 85% on a large one; better, run the same suite on both.

## Limitation

The lower bound favours old items with many votes. Ranking by a posterior sample gives new items a chance (see [[Thompson Sampling and Bandit Regret]]). Across many segments or markets the small ones hold the extreme numbers; estimate them together with [[Partial Pooling for Segment Winners]].

## See Also
- [[Confidence Interval Coverage and Wilson]] — alternative-to (the frequentist lower bound)
- [[Bayesian A/B Testing with Expected Loss]] — related
- [[Beta-Binomial Updating and Credible Intervals]] — prerequisite-for
