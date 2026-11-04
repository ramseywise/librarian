---
title: A/B Test Lifecycle and Interval Decisions
tags: [foundations, pattern]
summary: "A sound A/B test fixes the metric, the minimum detectable effect and the sample before launch, randomises and analyses at the same unit, checks the split, tests once, and decides by comparing the confidence interval with the effect worth shipping rather than reading the p-value."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--03-experimentation-and-causality--notes--01-ab-testing.md
  - data/raw/repos/learn-ai-engineering/data-analytics--03-experimentation-and-causality--notes--03-experimentation-at-scale.md
---

# A/B Test Lifecycle and Interval Decisions

Randomisation is what separates an experiment from observational data: a coin decides the arm, so no user trait, measured or not, can cause both arm and outcome. The two-sample test is then the easy part; most failures come before and after it.

## The pipeline

1. One primary metric (plus guardrails, see [[OEC, Guardrails and North Star Metrics]]), agreed before the test.
2. The minimum detectable effect (MDE): the smallest lift worth shipping, a business number. Sizing is in [[Minimum Detectable Effect and Sample Size]].
3. Sample size and duration; run whole weeks because weekday and weekend users differ.
4. Randomise by user, with a stable salted hash ([[Experiment Ramps and Overlapping Tests]]).
5. Check the split before reading outcomes ([[Sample Ratio Mismatch]]).
6. Test once at the planned N, or use a sequential design ([[Peeking and Sequential Testing]]).
7. Report lift, interval and p-value.

## What moves N (two-proportion test, 5.0% to 5.5%, 80% power, alpha 0.05: 31,231 per arm)

- Halving the MDE gives about 4 times the users (x3.91 for 5.0 to 5.25); doubling it gives x0.26.
- Power 0.9 gives x1.34; alpha 0.01 gives x1.49.
- A 20% baseline with the same absolute lift gives x3.25, because variance p(1-p) peaks at 0.5.
- Arm split matters: the variance multiplier is 1/(4p(1-p)), so 10% treatment costs 2.8 times and 1% costs 25.3 times the 50/50 design.
- The rule of thumb 16 sigma^2 / delta^2 per arm gave 30,400 here, within a few percent of the exact formula; use it as a cross-check. One practice formula computed the one-sample version and halved the answer (4,080 against 8,155 per arm), which the rule of thumb catches.
- Underpowered tests that do reach significance inflate the estimate ([[Winner's Curse]]).

## Unit of analysis

Analyse at the unit randomised. In an A/A simulation (users with 1 to 10 pageviews), analysing by pageview gave 10.8% false positives against 4.6% by user: rows from one person are correlated ([[Pseudoreplication and Intraclass Correlation]]).

## Reporting from the interval

Lift with its 95% interval comes first. The conversion tests (z, chi-square, Welch, Fisher) agree at large N; z squared equals chi-square for a 2x2 table, and they are not independent evidence. A relative lift needs a ratio interval, not the absolute interval divided by the control mean; a log-ratio interval works.

Compare the interval with zero and the MDE:

| Interval vs MDE | Reading |
|---|---|
| lower bound above MDE | ship |
| above zero, may be below MDE | real but weigh the cost |
| above zero, upper bound below MDE | flat, nothing worth shipping |
| spans zero and the MDE | inconclusive: cannot rule out a worthwhile effect |
| entirely below zero | harmful, stop |

"Not significant" in the fourth row is regularly misreported as "no effect" ([[P-Value Misreadings]]). Launches meant to "not hurt" can hide a negative, underpowered effect.

## Novelty and primacy

The first week's lift is not the steady state. In a simulation with a decaying daily effect and a steady-state lift of 0.20 points, weekly lift was 0.83, 0.33, 0.27, 0.28; stopping at week one claims four times the lasting effect. Plot lift by days since first exposure and compute it for new users, who cannot have novelty or primacy about a change they never saw before. A click-through bump on a new prompt can vanish after the first visit.

## Limits

A test says which version won, not why, so log diagnostics; it measures only the test window; it tests only what you can build.

## See Also
- [[Sample Ratio Mismatch]] — prerequisite-for
- [[Peeking and Sequential Testing]] — extends
- [[CUPED Variance Reduction]] — extends
- [[OEC, Guardrails and North Star Metrics]] — prerequisite-for
- [[Multiple Comparisons Corrections]] — related
