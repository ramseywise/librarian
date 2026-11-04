---
title: Standardised Survival and Pricing an Intervention
tags: [foundations, pattern]
summary: Turn a fitted hazard model into two survival curves (everyone treated, nobody treated) averaged over the real customer mix, so the gap becomes months gained and money; valid only if the observed covariates explain who got treated.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--06-applied-analyses--notes--07-survival-and-event-history.md
---

# Standardised Survival and Pricing an Intervention

A hazard ratio is hard to price, and a time-specific ratio compares survivors, who are different people in each arm. Standardisation (the parametric g-formula) avoids both.

## Method
1. Fit the discrete-time logit ([[Survival Analysis for Customer Lifetimes]]).
2. Predict every customer's monthly hazards under "all treated" and "none treated", holding other terms (e.g. the price rise switched off to isolate the treatment).
3. Multiply through to survival and average over the customers actually observed, keeping the real channel and plan mix in both arms.
4. Survival summed over months is months subscribed, so the gap between curves is months gained.
5. Resample customers, not rows, for the interval: one person's months belong together.

## Result (simulated subscriptions)
- Crude 360-day survival gap, no adjustment: 13.1 points. Adjusted gain at month 12: 5.9 (interval 3.3 to 8.3; truth 5.3); month 24: 3.3 (0.7 to 5.6; truth 2.9). More than half of the crude gap was who got treated.
- Gain 11.4 points at month 3, 2.1 at month 36: the hazards become equal after day 90, but people kept through those ninety days keep subscribing, worth 1.48 box-months in 24 months (0.91 to 1.95; truth 1.30).

## Pricing
Gain per customer = months gained x price x margin. With an assumed 35% margin and a 10.03 margin per month, the gain was 14.85 per call against an assumed 4.00 cost; the interval ends were 9.09 and 19.52. Margin and cost are assumptions: replace them. The call stops paying below about 0.4 months gained at that cost.

A price rise (hazard ratio about 1.5) can still pay. Stated cancel reasons give a check: price was cited by 21.4% of cancels before and 44.8% after, implying 1.42 against 1.49 from the model. Among 1,582 customers on the books on the day of the rise, extra margin per customer was 16.95 over 6 months, 23.56 over 12 and 24.14 over 24; the gain flattens because the higher price is offset by lost customers. It excludes new joiners and goodwill.

## Limits
Causal only if the covariates account for everything that decides who gets treated; true here by construction. In real data those who answer may simply be keener, so randomise a holdout and judge on 12-month survival and months gained, not a hazard ratio. See [[Sensitivity Analysis for Unmeasured Confounding]].

## See Also
- [[Matching and Weighting Estimators]] — prerequisite-for
- [[Campaign Breakeven and Uplift Holdout]] — related
- [[Bootstrap Resampling and Its Failures]] — related
- [[Sensitivity Analysis for Unmeasured Confounding]] — related
