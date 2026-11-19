---
title: Regression Splines, Smoothing Splines and GAMs
tags: [data-analytics, probability-and-statistics, concept]
summary: "Polynomials, step functions, regression splines, smoothing splines, local regression and additive models all fit a non-linear curve while staying a linear or additive model; each has one knob (degree, knots, lambda, span) that cross-validation or an F-test sets."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-islp-ch07-moving-beyond-linearity.md
  - data/raw/papers/2026-11-08-islp-ch03-linear-regression.md
---

# Regression Splines, Smoothing Splines and GAMs

ISLP's Chapter 7 extends the linear model to non-linear relationships while keeping most of its interpretability. The worked data is the ISLP Wage set (n = 3,000, males in the central Atlantic US), with age as the main predictor and wage in thousands of dollars.

## Basis functions and polynomials

A **basis function** model fits y = b0 + b1 b1(x) + ... + bK bK(x) by least squares, where the transformations b1..bK are fixed in advance. Polynomial regression is the case b_k(x) = x^k. ISLP advises a degree of no more than 3 or 4, since a high degree is wild near the boundary. In the Chapter 3 Auto data (mpg on horsepower), adding horsepower squared raised R-squared from 0.606 to 0.688 with a t-statistic of 10.1, and degree 5 looked unnecessarily wiggly. In the lab, sequential F-tests on nested polynomials of age gave p near 0 for linear against quadratic, 0.0017 for quadratic against cubic, about 5% for cubic against quartic and 0.37 for the quintic, so cubic or quartic suffice. A step function cuts the range at breakpoints and fits a constant per bin; the authors advise it only where the breaks are natural.

## Regression splines

A **knot** marks where a piecewise polynomial switches to new coefficients. A **cubic spline** stitches cubic pieces so the function and its first two derivatives stay continuous across every knot, built from the cubic basis x, x^2, x^3 plus one **truncated power** term h(x, xi) = (x - xi)^3 for x above xi and 0 otherwise per knot, so K knots cost K + 4 degrees of freedom. Without constraints, a one-knot piecewise cubic spends eight degrees of freedom; requiring continuity of value, slope and curvature removes three, leaving five. A **natural spline** is also forced to be linear beyond the boundary knots, which tames the variance at the edges: at 15 df the natural cubic spline stays well behaved at the tails, whereas a degree-15 polynomial swings wildly there.

Knots can be requested through a df value instead of placed by hand: a natural cubic spline with df = 4 puts three interior knots at the quartiles of age (about 33.8, 42 and 51). Ten-fold CV on Wage found about 3 df enough for a natural cubic spline and about 4 for a cubic spline, with one df (linear) inadequate. ISLP advises preferring splines to a high-degree polynomial: add knots and keep the degree fixed.

## Smoothing splines and local regression

A **smoothing spline** is the function g that minimises the sum of squared errors plus lambda times the integral of g''(t)^2 dt. Its **effective degrees of freedom**, the trace of the smoother matrix, shrink from n towards 2 as lambda rises from 0 without bound. On Wage, lambda chosen by LOOCV gave 6.8 effective df; a pre-specified 16 df fit was slightly wigglier and the authors preferred the simpler one when the fits are similar. **Local regression** fits a weighted regression around each point using the share of data set by the **span**: local linear regression on Wage used 5.3 df at span 0.7 and 16.4 df at span 0.2. It tends to struggle once there are many more than three or four predictors.

## Generalised additive models

A **generalised additive model** (GAM) is y = b0 + f1(x1) + ... + fp(xp) + e, with a separate smooth function per variable and no interactions unless added by hand. The authors fit it by **backfitting**, which updates each function in turn on its **partial residual**, the response minus the other fitted functions, holding the others fixed. Their Wage GAM gave year a natural spline with 4 df, age one with 5 df, and education a step function. In the lab, a GAM ANOVA preferred a linear function of year to none (p = 0.002) and found no need for a spline in year (p = 0.435). In the logistic GAM for wage above 250, nobody with education below high school earned above $250k, so that level had huge standard errors and was refit without them; check for empty cells before trusting such fits. The same polynomial logistic fit had wide intervals because only 79 of the 3,000 workers were high earners.

## Limits

- All Chapter 7 numbers come from the single Wage data set (n = 3,000) and illustrate rather than benchmark.
- GAMs are additive, so any interaction has to be supplied manually or through a two-dimensional smoother; local regression weakens past roughly three or four predictors.
- The lab used pygam, which has no local-regression terms and needs category codes shifted by one; the extraction could recover the lab tables only in part.
- The Chapter 3 R-squared figures are training-set values.

## See Also
- [[Functional Form Misspecification]] — prerequisite-for
- [[Model Selection Criteria]] — prerequisite-for
- [[Generalised Linear Models and Deviance]] — related
- [[Cross-Validation Variants and Nested Search]] — related
