---
title: James-Stein Estimator and Shrinkage
tags: [data-analytics, probability-and-statistics, concept]
summary: With four or more normal means estimated at once, pulling each estimate toward the grand mean beats the separate maximum likelihood estimates on total squared error, at the cost of some individual cases getting worse.
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch07-james-stein-estimation-ridge-regression.md
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch05-parametric-models-exponential-families.md
---

# James-Stein Estimator and Shrinkage

Efron and Hastie (*Computer Age Statistical Inference*, ch. 7) ask why bias added on purpose can outperform maximum likelihood once many parameters are estimated together, and how the idea reappears in ridge regression.

## The estimator

Take N independent observations x_i ~ N(theta_i, 1). Under a Bayes model theta_i ~ N(M, A), the Bayes estimate pulls each x_i toward M. With A equal to the noise variance (B = A/(A+1) = 1/2), the posterior mean moves halfway from x to M and the posterior variance is half that of the maximum likelihood estimate.

The James-Stein estimate plugs the data in for the prior's unknowns: each estimate is the grand mean M-hat plus B-hat times the distance of x_i from it, where B-hat is one minus (N-3)/S and S is the sum of squared deviations from the grand mean. It is the Bayes rule with its constants estimated from all the observations; the chapter describes this as empirical Bayes.

The James-Stein theorem needs no prior: for N of 4 or more independent N(theta_i, 1) observations under squared error, the James-Stein total risk stays under N whatever theta is, which makes the maximum likelihood estimate inadmissible.

Setup for the risk figures: theta_i ~ N(M, A), N = 20, A = 1. The risks are 20 for the maximum likelihood estimate, 11.5 for James-Stein (N*B + 3(1-B)) and 10 for the exact Bayes rule (N*B).

## Baseball example

Setup: 18 players, batting averages from the 1970 Major League season (partly artificial data). The maximum likelihood estimate is the average over the first 90 at bats and the truth is the average over the rest of the season (370 more at bats on average); James-Stein used an arcsin-transformed estimate. The grand mean was 0.254 and B-hat was 0.34, so each player's estimate moves most of the way to it.

| Rule | Sum of squared error against the truth |
|---|---|
| Maximum likelihood | 0.0425 |
| Shrink all the way to the grand mean | 0.0266 |
| James-Stein | 0.0218 |

In 1000 simulations (each player's first-90 average drawn as Bi(90, truth)/90) the total mean square error was 0.0384 for maximum likelihood and 0.0235 for James-Stein. James-Stein beat maximum likelihood for 14 of 18 players; it lost for four, the two with the highest truths and the two with the lowest. For Clemente (truth 0.346) its root-mean-square error was 0.077 against 0.049, and every one of the 1000 estimates fell below the truth. A limited-translation version caps how far an estimate can move from the maximum likelihood value, at one standard deviation of that estimate, and gave him 0.056.

## Ridge regression

Ridge replaces the least-squares coefficients by (S + lambda I) inverse times X'y, which also minimises the squared residual norm plus lambda times the squared coefficient norm. Lambda = 0 is least squares and large lambda drives the coefficients to zero. Setup: diabetes data, n = 442, ten standardised predictors, centred response, lambda = 0.1, noise standard deviation 54.1 estimated from least squares. The standard error of the tc coefficient fell from 416.2 to 43.6; ldl went from +476.7 to -70.8, and tc itself from -792.2 to -83.5. The chapter's Cp calculation suggests variance reduction and added squared bias nearly offset, so accuracy of the fitted values is not clearly better even though coefficient variability falls sharply.

## Practice

Efron and Hastie advise standardising predictors before ridge, leaving the intercept unpenalised, and asking which other cases belong in the pool: an outstanding case should not be pooled with ordinary ones.

## Limits

- The chapter says no optimality theory for shrinkage exists yet, and there is no foolproof way to choose lambda.
- Part of the baseball data is artificial: each player's original 45 at bats had 45 simulated binomial draws added, which, by the authors' account, makes James-Stein look less impressive.
- The gain is in total error, not for every player, and depends on the cases being exchangeable.
- The theorem assumes the variance is known; estimating it erodes some of the improvement.
- Ridge is not scale-equivariant, hence the standardisation.

## See Also
- [[Small-N Trap and Shrinkage]] — prerequisite-for
- [[Regularisation as a Prior]] — prerequisite-for
- [[Robbins Empirical Bayes Formula]] — related (the other empirical Bayes estimator in the same book)
- [[Partial Pooling and Multilevel Models]] — related
- [[Penalised Linear Models: Ridge, Lasso and Elastic Net]] — related
- [[Empirical Bayes: Tweedie's Formula and g-Modeling]] — extends
