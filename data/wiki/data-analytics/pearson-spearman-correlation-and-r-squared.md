---
title: "Pearson, Spearman Correlation and R-Squared"
tags: [data-analytics, probability-and-statistics, concept]
summary: "Pearson correlation is the mean product of standard scores and sees only straight-line association, Spearman applies it to ranks, and R-squared is the squared correlation read as the cut in squared prediction error; none of them shows causation."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-think-stats-ch09-correlation.md
---

# Pearson, Spearman Correlation and R-Squared

Downey's *Think Stats* chapter 9 covers the relationship between two variables, with one explanatory variable only; multivariate regression is explicitly left out.

## Pearson correlation

Pearson's rho is the mean product of standard scores, equivalently Cov divided by the product of the standard deviations, and is bounded between -1 and +1 (proved with Cauchy-Schwarz). It captures straight-line association only, so a dependence that is clearly nonlinear can still yield rho = 0. It is not robust to outliers; Anscombe's quartet is four data sets with the same correlation ([[Anscombe's Quartet: Plot Before Summarising]]). Downey advises looking at a scatterplot before computing a coefficient.

## Spearman rank correlation

For skewed data or data with outliers, Downey advises percentile ranks (Spearman), or transforming to near-normal first, for example the log of lognormal data, and then using Pearson. The simple solution gives tied values arbitrary ranks; averaged ranks are strictly correct.

## R-squared

For a simple least-squares line, R-squared equals the squared Pearson correlation. An R-squared of 0.64 means the model reduces the mean squared error of predictions by 64%. An exercise relates total SAT to WAIS scores through a correlation of 0.72 (cited from "one study", no reference; WAIS has mean 100 and standard deviation 15) and implies an expected MSE of 225 x (1 - 0.72^2), which the chapter leaves uncomputed. Downey asks whether squared residuals are the right loss, since a cost function may suit better.

## Plotting large and rounded data

BRFSS heights were rounded to whole inches, so each can be off by as much as 0.5 in (1.3 cm); random offsets drawn uniformly from -1.3 to 1.3 cm are added to the scatterplot to undo the banding. Downey restricts jitter to plotting and rules it out for analysis. Alpha transparency suits moderate data and hexbin large data, though hexbin hides outliers; the transparency example shows the first 1000 of 414,509 BRFSS records.

## Causation

Correlation does not establish cause. Downey names a randomised controlled trial as the most reliable demonstration, and lists time ordering, natural experiments, and controlling for a confounder by regression or stratification as other supports. His stratification example compares first and other babies within mother's-age groups.

## Limits

- The chapter stops at simple linear regression and offers no interval or p-value for rho, beta or R-squared.
- The printed formula for rho in terms of deviations is wrong as typeset; the correct form has the square root of the product of summed squares in the denominator.
- No numeric BRFSS correlation, slope or R-squared is printed; they are left as exercises.
- The book is dated: pyplot code from the Python 2 era and thinkstats.com links.

## See Also
- [[Robust Summaries for Skewed Metrics]] — related (a measured Pearson against Spearman comparison on a revenue column)
- [[Confounders, Mediators and Colliders]] — related (confounders behind a correlation)
- [[Regression Covariate Adjustment]] — related (controlling for a confounder by regression)
