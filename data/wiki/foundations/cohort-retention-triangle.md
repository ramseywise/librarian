---
title: Cohort Retention Triangle
tags: [foundations, pattern]
summary: Cohorts hold customer age fixed so retention changes can be read as a cohort effect (who arrived) or a period effect (something hit everyone), with incomplete ages masked and channel value judged over 24 months, not at the first order.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--06-applied-analyses--notes--03-cohort-and-retention.md
---

# Cohort Retention Triangle

A cohort is a group of customers who started in the same period; **age** is months since then. Two columns on each order (cohort, age) are all a cohort analysis needs.

## Why not one blended retention rate

A blended rate averages customers of every age. A young base has a high monthly rate because new customers buy again soon, so growth flatters it and slowdown hurts it with no behaviour change. Holding age fixed removes this.

## Reading the triangle

- **Across a row:** one cohort ageing (declines then flattens).
- **Down a column:** cohorts compared at one age, where a cohort effect (who arrived) shows. In the example age-1 retention ran about 15% through 2024Q4, then about 8.4%.
- **Along a diagonal:** one calendar month across cohorts of different ages, where a period effect shows. A shock in early 2025 appeared as drops at age 12 for 2024Q1, age 6 for 2024Q3, age 2-3 for 2024Q4.

Limit: age = period - cohort, so the three cannot be separated by regression without an extra assumption. Treat the triangle as evidence for a hypothesis and use an outside fact (the known date of a budget cut) to interpret the diagonal.

## Mask incomplete cells

Report an age for a cohort only once its youngest member has reached it. An unreached cell does not exist yet; filling it with a partial figure or zero reports a collapse every month. For a 90-day repeat rate, use only customers acquired early enough to have had 90 days.

## Rate versus mix

To tell "every customer got worse" from "we bought different customers", use [[Rate and Mix Decomposition]]. In the example the 90-day repeat rate fell from 31.6% to 20.2%: 6.2 points from rates (every channel worse by 5-9 points), 5.2 from mix shifting to a low-repeat channel (from about 27.5% to 53.8% of new customers).

## Value by channel

First-order value (about 56-62 pounds in all four channels) or a 30-day return makes every channel look alike; cumulative revenue lines separate later, so a day-30 decision can be badly wrong at month 24. Margin per customer over 24 months divided by acquisition cost (CAC) gives an LTV-to-CAC ratio, and both margin and CAC are assumptions to state with sensitivity. With an assumed 35% margin and assumed CAC of 32 for paid social, its ratio was 1.02 against 4.39-10.95 for other channels. If its CAC were 15 the ratio would be about 2.2. A 3x hurdle is a planning rule, not a law.

A before-and-after around a budget cut cannot prove the cut caused the fall; reinstating it needs a holdout.

## Pitfalls
- Comparing incomplete cohorts; reading a period effect as a cohort effect; treating a lapsed customer as lost (non-contractual churn is silence, not observed).
- Fitting an arbitrary curve to extrapolate: see [[Shifted Beta Geometric Retention Model]].

## See Also
- [[Rate and Mix Decomposition]] — extends
- [[Shifted Beta Geometric Retention Model]] — extends
- [[Survival Analysis for Customer Lifetimes]] — related
- [[Minimum Detectable Effect and Sample Size]] — related (sizing the reinstatement holdout)
