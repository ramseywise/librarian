---
title: Partial Pooling for Segment Winners
tags: [foundations, pattern]
summary: "When an experiment reports a lift per segment, the raw winner is overstated; pooling segment estimates removed most of the exaggeration in simulation (+2.93 to +0.09) but picked the best segment only modestly better, and it fails for outliers, wrong centres and when the prior on tau is wrong."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--04-bayesian-analysis--notes--07-multilevel-models-and-partial-pooling.md
---

# Partial Pooling for Segment Winners

The selection effect of [[Winner's Curse]] applied to segment lifts: the segment with the highest measured lift was selected for carrying positive noise. Pool the segments with [[Partial Pooling and Multilevel Models]] and the extremes shrink in proportion to their uncertainty.

## Setup and one dataset

24 segments, true lifts around +1.0 with tau 0.5 plus measurement noise. Given tau the normal model has a closed form, so integrating tau on a grid makes thousands of replications cheap; PyMC agreed with the grid to within 0.014 in any segment's mean. RMSE against truth: per segment 1.109, pooled 0.291. The raw winner (672 users an arm) measured +3.17, true +1.25, pooled +1.27; the pooled winner (8,102 an arm) measured +2.42, pooled +1.69, true +1.79, the truly best segment.

## 1,000 datasets

| | Per segment | Pooled |
|---|---|---|
| RMSE | 1.357 | 0.489 |
| Winner estimate minus true lift | +2.93 | +0.09 |
| True lift of the segment picked | 1.26 | 1.46 (truly best 1.98) |
| 90% interval coverage | 0.90 | 0.90 |

Pooling mostly fixes how much you claim and only partly which segment you pick. Classical corrections such as Bonferroni leave estimates and widen intervals; pooling moves estimates together, more for uncertain ones, reframing the problem as wrong-sign and wrong-magnitude errors. The price is claiming confidence in fewer comparisons (see [[Multiple Comparisons Corrections]]).

## Where it does not help

| Scenario | Pooled/raw RMSE ratio |
|---|---|
| Baseline, tau 0.5 | 0.36 |
| No real differences, tau 0 | 0.16 (coverage 1.00: intervals too wide) |
| Well measured (100x users), tau 0.5 / 2.0 | 0.93 / 0.99 |
| Only 4 segments, tau 0.5 | 0.55 |

- A real outlier: one small segment truly at +5.0 was pulled down by 3.74 on average (RMSE 3.01 to 3.76) while the other 23 improved from 1.249 to 0.490. Shrinkage works against finding the rare real winner; follow up large raw effects with a new test.
- Wrong centre: small segments truly at +3.0 and large at +0.5; one common mean gave mean error -1.10 (RMSE 1.29 against raw 1.73). Adding size as a group-level predictor removed the bias (RMSE 0.49). Known structure belongs in the model.
- Population-average questions need none of this.

## Few segments hand control to the prior

With 4 segments and tau really 0.5, pooled RMSE ratios were 0.49 (half-normal(0.25)), 0.55 (half-normal(2)) and 0.60 (half-Cauchy(5)). With tau really 2.0, half-normal(0.25) gave ratio 1.25 and 90% coverage of only 0.48, worse than raw, while half-normal(2) gave 0.85. The data barely informs tau from four segments, so report a range over priors ([[Prior Choice and Prior Predictive Checks]]).

## Caveat

Pooling analyses only the comparisons put in the model, so segments chosen after seeing the data still need counting. With few or highly structured comparisons inference can be sensitive to model assumptions; partial pooling is a better default than raw numbers or Bonferroni, not a licence to stop worrying.

## Conversion outcomes

A logit model with a random base rate and lift per market (30 markets, 156 to 6,637 users an arm) cut lift RMSE from 1.01 to 0.68 points and control-rate RMSE from 0.83 to 0.71. A market with zero control conversions got a nonzero pooled rate. In that single dataset both methods picked the same winner and understated it (+5.28 and +5.09 against a true +6.42), so it does not show the exaggeration; the replicated evidence is the 1,000 runs above. Lifts in points also grow with the base rate.

## See Also
- [[Winner's Curse]] — extends
- [[Partial Pooling and Multilevel Models]] — prerequisite-for
- [[Multiple Comparisons Corrections]] — alternative-to
- [[Ranking by Lower Credible Bound]] — related
