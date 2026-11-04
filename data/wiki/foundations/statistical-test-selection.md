---
title: Statistical Test Selection
tags: [foundations, reference]
summary: "Pick the test from the data type and design: Welch by default for two means, paired when rows pair, chi-square or Fisher for counts by expected cell size, rank tests for ordinal data but not for questions about totals."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--05-hypothesis-testing.md
---

# Statistical Test Selection

| Situation | Test |
|---|---|
| Two group means | Welch t-test (default; no equal-variance assumption) |
| Equal variances plausible | Student t-test |
| Same units measured twice | Paired t-test |
| Three or more groups | ANOVA, then Tukey for pairs |
| Two categorical variables | Chi-square; Fisher exact if any expected count is below 5 |
| Two distributions | Kolmogorov-Smirnov |
| Two proportions | Two-proportion z-test |
| Skewed or ordinal, two groups | Mann-Whitney |
| Skewed or ordinal, paired | Wilcoxon signed-rank |
| Skewed or ordinal, 3+ groups | Kruskal-Wallis |

ANOVA is regression: a one-way ANOVA is OLS on group dummies and gives the same F-test ([[Regression Covariate Adjustment]]).

## Rank tests and revenue

Rank tests ignore magnitude, which is sometimes the point and sometimes the problem. Adding one 60,000 whale to a revenue sample moved Welch's p from 0.165 to 0.506 while Mann-Whitney moved from 0.125 to 0.163. Mann-Whitney is steadier, but it answers whether one group tends to be higher, not whether total revenue differs, and the business question is usually the latter. A bootstrap of the median difference gave [-7.6, 16.6] ([[Bootstrap Resampling and Its Failures]]). Choose the test for the question, not for the p-value you want.

## Check the design first

Pair when rows pair ([[P-Value Misreadings]]), cluster when assignment clusters ([[Clustered Standard Errors]]), and correct when testing many things ([[Multiple Comparisons Corrections]]). The data's distribution sets the family ([[Distribution Selection for Metrics]]).

## See Also
- [[Permutation Test]] — related
- [[Minimum Detectable Effect and Sample Size]] — related
- [[Robust Summaries for Skewed Metrics]] — related
