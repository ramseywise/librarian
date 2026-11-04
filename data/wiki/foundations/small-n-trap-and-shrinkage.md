---
title: Small-N Trap and Shrinkage
tags: [foundations, pattern]
summary: "Averages from small groups are noisy, so the best and worst groups of any league table are the smallest ones even when no group differs; show N beside every rate, rank by a lower bound, or shrink toward the overall rate with pseudo-observations."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--01-descriptive-statistics-and-eda.md
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--03-distributions-and-sampling.md
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--README.md
---

# Small-N Trap and Shrinkage

The law of large numbers holds only for large N. For small N sample averages are noisy, and the most extreme averages come from the smallest groups.

## Demonstrations

- 200 arbitrary groups of about 100 users, assigned at random, had mean spend per user ranging from 0.00 to 15.46 around an overall 3.30, with no real difference between groups.
- 5,000 simulated counties of 100 to 1,500 people, all with the same height distribution: every one of the ten tallest and ten shortest counties had under 300 people although the median county had 808. Plotting average against population gives a funnel, wide at the small end.
- Real version: a funder backed small schools because the best-performing schools were small, but the worst were small too.

Small samples are high-variance, not high-quality.

## Shrinkage

If a raw rate is unreliable because N is small, add pseudo-observations at the overall rate:

```python
shrunk = (hits + prior_mean * prior_n) / (trials + prior_n)   # prior_mean 0.9, prior_n 40
```

This is the Beta-Binomial posterior mean. With prior mean 0.9 and 40 pseudo-trials, 2/2 shrinks from 1.000 to 0.905, 5/5 to 0.911, 92/100 to 0.914, while 905/1000 stays at 0.905: the estimate moves only when N is too small to speak for itself. The amount of shrinkage can itself be estimated from data (empirical Bayes).

An alternative ranking: the lower 95% Wilson bound ranks 95/100 (0.888) far above 2/2 (0.342) ([[Confidence Interval Coverage and Wilson]]).

## Where it bites

| Setting | Symptom | Fix |
|---|---|---|
| Ranking items by average rating | a 1-review 5-star item tops the list | rank by a lower bound |
| Comparing regions, stores, cohorts | best and worst segments are smallest | show N; shrink toward the overall mean |
| A/B test read early | huge lift on day one | fix the sample size in advance |
| Leaderboards on small eval sets | rank flips between runs | report an interval, not a point |

Sample sizes are never large: once N is large enough you start subdividing, and there is always a subgroup small enough to be noisy ([[Multiple Comparisons Corrections]] covers the testing side).

## See Also
- [[Small-N Reporting Floor]] — related (a reporting-side guard against the same trap)
- [[Eval Error Bars and Sample Size]] — related
- [[Confidence Interval Coverage and Wilson]] — related
- [[CLT on Heavy-Tailed Metrics]] — related
- [[EDA Audit Loop]] — related (group tables keep N)
