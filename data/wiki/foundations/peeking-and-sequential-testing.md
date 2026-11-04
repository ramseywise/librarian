---
title: Peeking and Sequential Testing
tags: [foundations, pattern]
summary: "Checking a fixed-horizon p-value repeatedly inflates false positives to 25% at 20 looks, so if people will look use group-sequential boundaries (O'Brien-Fleming, Pocock) or always-valid mSPRT p-values, which pay for looks with a stricter threshold."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--03-experimentation-and-causality--notes--01-ab-testing.md
  - data/raw/repos/learn-ai-engineering/data-analytics--03-experimentation-and-causality--notes--03-experimentation-at-scale.md
---

# Peeking and Sequential Testing

A p-value is valid only at the sample size planned. Stopping the first time it dips below 0.05 inflates the false-positive rate ([[P-Value Misreadings]]).

## How bad

With both arms at 10%, testing once gave 0.055; stopping at the first of 20 looks gave 0.250. Under the null with n_max 10,000, the false-positive rate by number of looks: 1 look 0.048, 2 looks 0.085, 5 looks 0.141, 10 looks 0.196, 20 looks 0.245, 100 looks 0.390, 1000 looks 0.524.

Banning peeking does not work as policy: dashboards exist and a bad launch must be stoppable. Two honest alternatives both pay for looks.

## Group-sequential boundaries

Fix the number of looks in advance and set a threshold per look. Calibrated to 5% overall over five looks:

- Pocock: constant z boundary 2.42 at every look. Stops moderate effects earlier, costs power at the end.
- O'Brien-Fleming: 4.53, 3.2, 2.61, 2.26, 2.03. Stops early only on enormous effects and ends near the fixed value 1.96; the usual choice.

A boundary that is 1.96 divided by the square root of the information fraction, uncalibrated, gave about 0.058, slightly above 5%. Published designs use tables or alpha-spending functions, which allow looks on unplanned dates.

## Always-valid p-values (mSPRT)

The mixture sequential probability ratio test compares the likelihood under "some effect drawn from a normal with variance tau squared" to the likelihood under no effect. Under the null the ratio is a martingale with mean 1, so the chance it ever reaches 1/alpha is at most alpha; p = min(1/ratio) is valid at any stopping time. In simulation, checking after every pair of users gave a false-positive rate of 0.041. With a true effect of 0.05 sd, 98.2% of runs detected it within 20,000 pairs; median stop 5,897 pairs, 90th percentile 12,932, against 6,272 pairs for a fixed test with 80% power. So half the runs stop sooner, but the tail is long. Tau squared sets where the method is sharpest; choose it from effect sizes seen in past experiments.

## Choosing

- Test planned for weeks and reviewed weekly: group-sequential.
- Self-serve platform where people look whenever: always-valid.
- Either way keep whole weeks, and allow early stops for guardrail failure.
- A Bayesian posterior does not make peeking free either.

## See Also
- [[A/B Test Lifecycle and Interval Decisions]] — prerequisite-for
- [[Multiple Comparisons Corrections]] — related (repeated looks are multiple tests)
- [[Minimum Detectable Effect and Sample Size]] — prerequisite-for
- [[Experiment Ramps and Overlapping Tests]] — related
