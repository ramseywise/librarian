---
title: RFM Segmentation Validated on a Holdout
tags: [foundations, pattern]
summary: RFM segments are predictions and must be scored on a period after the snapshot; doing so shows that frequent buyers who went silent are mostly gone (iso-value curves bend backwards), that clustering adds little over R and F, and that value is concentrated but only partly predictable.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--06-applied-analyses--notes--05-segmentation-and-rfm.md
---

# RFM Segmentation Validated on a Holdout

A segmentation says these people will act differently, so test it like a model: build every feature from orders up to a snapshot date and keep a later period (here July-December) as holdout. Include customers who bought nothing after it.

## Features and scores

**Recency** = days since last order, **frequency** = order count, **monetary** = value **per order** (total spend largely repeats frequency, giving the same customers twice). Classic RFM cuts each into quintiles and names grid regions (Champions, At risk, New, Hibernating, Middle).

Most customers are not an active relationship: median customer last bought 287 days before the snapshot, ordered once, and bought nothing in the holdout. 60.2% had exactly one order.

**Tie-break bug.** Frequency cannot split into honest fifths when 60.2% are tied. Ranking with method "first" broke ties by row order, which follows customer id and so sign-up date: New held 315 customers instead of 3,061 and 4,217 of 4,309 recent one-order customers landed in Middle. Output gives no sign; break ties at random or use fixed bins, and always check what decides ties.

## What the holdout showed

| Segment | Buy again | Future value per head | Share of future value |
|---|---|---|---|
| Champions (18% of customers) | 45% | 55.57 | 68% |
| At risk (past value 168) | 3% | 1.72 | 1% |
| Hibernating | 2% | 1.19 | 1% |

The campaign target ("former big spenders gone quiet") is mostly gone.

## Backward-bending iso-value curves

On a round-number grid, five-plus-order customers silent over a year were worth about 1 and 3-4-order ones about 3; more orders did not help. A 23,560-customer analysis (Pareto/NBD for purchasing plus gamma-gamma for order value) plots iso-value curves that bend backwards in the low-value region. Resolution: a once-a-year buyer who is quiet may not be due yet; a weekly buyer quiet for the same time has probably left. High frequency makes a given silence more informative. That analysis found monetary value independent of purchase process (correlation 0.11 between average order value and orders among 946 repeat buyers; 0.09 Spearman in the simulated data), so M scales value but not who buys; look at R and F first. Also mind the "zero class" of customers with no purchases: small each, large in number.

## Does clustering beat the grid?

Log and standardise skewed features before k-means (one 67-order customer otherwise dominates). Silhouettes hovered around 0.3 for k = 2-7 (0.345 at k=2, 0.31 at k=4): a smooth continuum with no natural groups, so k-means returns whatever k is asked. Two clusters differing mainly by order value (77 vs 27) had nearly the same future value (5.40 vs 3.55): k-means weights monetary like the other axes, the outcome hardly cares. Score any segmentation on a holdout and prefer the explainable one when they do the same job. For mixed columns see [[Clustering Validation Against Named Baselines]].

## Value concentration and regression to the mean

Top decile by past value held 45.4% of past and 44.3% of future value, versus 91.9% if ranked by the future itself: the gap measures unpredictable buying. Rank correlation of past and future value was 0.244; among customers buying in both periods, order value's was 0.397. Extreme customers look less extreme next period without intervention, so a campaign on last year's top spenders appears to reduce spend whatever it does. Top-tenth future value share by recency alone 36.6%, frequency 43.5%, summed percentile ranks 53.5%.

## See Also
- [[Campaign Breakeven and Uplift Holdout]] — extends
- [[Clustering Control World Test]] — extends
- [[Shifted Beta Geometric Retention Model]] — related
- [[BG/NBD Customer Lifetime Value]] — related
- [[HDBSCAN with KMeans Fallback]] — related
