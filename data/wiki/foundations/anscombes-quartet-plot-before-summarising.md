---
title: "Anscombe's Quartet: Plot Before Summarising"
tags: [foundations, concept]
summary: Four datasets with identical means, variance, correlation and fitted line look completely different, so summary statistics alone cannot replace a plot.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--05-visualisation-and-storytelling--notes--01-grammar-and-chart-choice.md
---

# Anscombe's Quartet: Plot Before Summarising

Four small datasets (11 points each) were built to rebut the belief that calculations are exact and graphs rough. To two decimals they share every headline number:

| Statistic | Value in all four sets |
|---|---|
| mean of x | 9.0 |
| mean of y | 7.5 |
| variance of y | 4.12 to 4.13 |
| correlation | 0.82 |
| fitted slope / intercept | 0.5 / 3.0 |

Drawn, they differ:

- **Set I**: the picture the summary implies, a noisy line.
- **Set II**: a clean curve that a line should never have been fitted to.
- **Set III**: a tight line with one outlier dragging the fit.
- **Set IV**: no relationship except one point that manufactures the whole slope (x is constant except for that point).

Each needs a different next step (a nonlinear model, outlier handling, more data across x), and the table cannot say which.

## Consequences

- Plot before you report. Summaries can hide curvature, outliers and leverage; see [[OLS Influence and Collinearity Diagnostics]] for the leverage side.
- There are two jobs for charts. **Exploratory** charts are the many you make to find out what is true; **explanatory** charts are the few you make to tell someone else one thing; see [[Explanatory Data Story and the Big Idea]].
- For a systematic pass over a new dataset see [[EDA Audit Loop]].

## See Also
- [[EDA Audit Loop]] — related
- [[OLS Influence and Collinearity Diagnostics]] — related
- [[Visual Encoding Accuracy Ranking]] — related
