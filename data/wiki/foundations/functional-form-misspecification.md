---
title: Functional Form Misspecification
tags: [foundations, pattern]
summary: "A linear control for a hump-shaped confounder biases the treatment effect threefold with zero coverage, flexible forms fix it, and a quadratic whose peak looks significant can be an artifact of a curve that never turns."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--07-data-generating-process.md
---

# Functional Form Misspecification

## Bias from the control

A hump-shaped confounder controlled linearly gave a treatment estimate of 0.663 against a truth of 0.20 with 0% coverage. A quadratic or spline control gave 0.195 to 0.200 with 94% coverage. Controlling for a variable is only as good as the shape you give it.

## Practical advice

- Take logs when you believe causes multiply, so effects are proportional.
- A spline bends locally without the global behaviour of a polynomial, which swings at the edges.
- Flexible forms barely moved the coefficient of interest (0.179 to 0.200), whereas staying with a bad form moved it a lot ([[Model Selection Criteria]]).

## Quadratic turning-point artifact

A fitted squared term can have p of about 1e-19 and a peak with a tidy interval [46.3, 55.4] on data whose true curve rises and flattens and never falls. The parabola must turn; the test only says the line is wrong, not that a turn exists. A turning point deserves a story only when theory predicts it, there is data past the turn, and a spline agrees.

## Detect

Plot residuals against each regressor, run the placebo ([[Data Generating Process Simulation Check]]), and compare with a spline.

## See Also
- [[Regression Covariate Adjustment]] — related
- [[Robust Standard Errors]] — related
- [[Explain vs Predict Modelling]] — related
