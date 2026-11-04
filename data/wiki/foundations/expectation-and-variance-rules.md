---
title: Expectation and Variance Rules
tags: [foundations, reference]
summary: "Expectations always add, even for dependent variables, while variances add only for uncorrelated ones; indicator variables turn counts into sums, and the law of total variance explains why knowing a group removes noise."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--02-probability-foundations.md
---

# Expectation and Variance Rules

## Linearity of expectation needs no independence

E[X + Y] = E[X] + E[Y] always. This lets you take hard problems apart. Shuffle a deck of 52 and count cards left in their original position: the positions are dependent, yet each matches with probability 1/52, so the expected count is exactly 1 (simulated mean 0.999; P(no match) is about 1/e, a separate fact that does need harder calculation).

The tool is the **indicator variable**, 1 if an event happens and 0 otherwise. Its expectation is the event's probability, so P(A) = E[1_A], which is why `np.mean(samples > 0)` estimates a probability. A count of events is a sum of indicators and its expectation is the sum of probabilities however tangled they are.

## Variance needs care

Var(X + Y) = Var(X) + Var(Y) + 2 Cov(X, Y). Views and clicks are positively related: the simulated variance of their sum was 6.61, against 5.61 for the sum of variances. The covariance term vanishes only for uncorrelated variables. That condition produces the standard error: n independent values with standard deviation s have a sum of variance n s^2, so the mean has standard deviation s / sqrt(n) (simulated 3.05, 0.74 and 0.19 against formula 3.00, 0.75 and 0.19 for n = 100, 1,600 and 25,600 with s = 30). When rows are correlated the formula is too optimistic: see [[Pseudoreplication and Intraclass Correlation]].

## Law of total variance

For a hidden group variable B:

```text
E[X]   = E[ E[X | B] ]
Var[X] = E[ Var[X | B] ] + Var[ E[X | B] ]
```

Total variance is the average within-group spread plus the spread between group means. For revenue per user with B = "buys or not", E[revenue] = P(buy) times E[order | buy], and in the simulation 29% of revenue variance came from whether a user buys at all, which is why conversion is easier to move than revenue.

The second identity is why stratification and covariate adjustment ([[Regression Covariate Adjustment]]) reduce noise: if you already know a user's group or prior spend, that part of the variance was never about the treatment. A simple comparison stays unbiased only if the mix is balanced across arms.

## Failure modes

- Adding variances without checking covariance.
- Assuming independence because it is convenient: sessions within a user, users within a household and days within a week are correlated.

## See Also
- [[Pseudoreplication and Intraclass Correlation]] — extends (what correlation does to the variance of a mean)
- [[Regression Covariate Adjustment]] — related (applies the between-group term)
- [[Independence Pitfalls]] — related
- [[CLT on Heavy-Tailed Metrics]] — prerequisite-for (the s/sqrt(n) rule)
