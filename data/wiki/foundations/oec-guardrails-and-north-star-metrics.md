---
title: OEC, Guardrails and North Star Metrics
tags: [foundations, concept]
summary: "Experiment metrics split into data-quality checks, one pre-agreed overall evaluation criterion, guardrails tested for non-inferiority against a margin, and diagnostics; a correct test on the wrong metric gives a confident wrong answer, and not significant is not a guardrail pass."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--03-experimentation-and-causality--notes--02-metrics-and-kpi-design.md
  - data/raw/repos/learn-ai-engineering/data-analytics--03-experimentation-and-causality--notes--03-experimentation-at-scale.md
---

# OEC, Guardrails and North Star Metrics

The gap behind all metric design: what you want (long-run health) is slow, noisy and hard to attribute; what you can measure in a test window is quick, sensitive and only a proxy.

## Four kinds

| Kind | Question | Read as |
|---|---|---|
| Data quality | can I trust this test? | any failure invalidates the rest ([[Sample Ratio Mismatch]]) |
| Overall evaluation criterion (OEC) | did the change succeed? | one number or weighted combination, fixed in advance, decides launch |
| Guardrail | did it break a promise? | must not worsen beyond a margin |
| Local or diagnostic | why? | explains, does not decide |

A north star is the company-level number steered across quarters; few experiments can move it detectably, so the OEC is the experiment-sized stand-in. It should be sensitive, directional (time on site fails: up is ambiguous), attributable, hard to game (Goodhart's law), leading (moves in the window) and predictive of long-term value, which is an empirical claim to check against past experiments. A metric tree connects north star to OEC to funnel steps and shows where a proxy might drift.

## Variance and sensitivity

Needed users scale with metric variance over mean squared. On one dataset, for a 5% change: revenue per user 290,154 per arm, capped at the 99.9th percentile 247,386, conversion 125,290. Forty users above the cap held 12.9% of revenue; capping cut the sample by about 15%. Count how many values each cap or bot filter changes and track it as data quality; a cap can hide an effect that only helps big spenders. Filtering to users who could be affected also shrinks variance but can shift who reaches the filter, so report conditional and unconditional rates. See [[Robust Summaries for Skewed Metrics]] and [[CUPED Variance Reduction]].

## Guardrails need non-inferiority

Fix a margin and require the one-sided upper bound of the change to fall below it. With a 50 ms load-time margin and sd 900 ms: 8 ms extra on 400 users per arm cannot pass (upper bound 112.7); the same 8 ms on 20,000 users per arm passes; +45 ms on 20,000 cannot pass (upper 59.8). A naive check "not significant" would pass the first. Guardrail power is part of the design. An underpowered metric measured at +0.5% with an interval of about plus or minus 5% could detect only changes of at least 7.8%, so an apparent pass means little. Slowing search results by one second cut queries per user by 1% and ad clicks by 1.5%, which is why latency earns guardrail status.

## Many metrics, one decision

With 60 metrics and 4 real movers, raw testing flagged 7 (3 false); Benjamini-Hochberg flagged 3 (0 false). Use one OEC at the normal threshold, guardrails with margins, diagnostics under FDR control ([[Multiple Comparisons Corrections]]). For conflicts, state weights before the test (a weighted OEC), ideally estimated by regressing long-term value on short-term metrics and revisited as it drifts.

## Writing a metric down

A metric needs name, owner, kind, unit (the randomisation unit), numerator, denominator (including users with no order), direction, filters, variance method, window (whole weeks) and guardrails. Pick the metric before the result; the argument about it tends to follow whichever result people wanted.

## Twyman's law and the dozen

A figure that looks interesting or different is usually wrong. A button change showed +28% clicks and +27% on the neighbouring button with no retention change. The catalogued pitfalls (ratio metrics, telemetry loss, underpowered metrics, borderline p-values, early stopping, non-uniform effects, segment misreads, outliers, novelty, incomplete funnels) each map to an automatable check: [[Ratio Metrics and the Denominator Trap]], [[Peeking and Sequential Testing]], [[Post-Treatment Segments and Simpson's Paradox]].

## See Also
- [[A/B Test Lifecycle and Interval Decisions]] — prerequisite-for
- [[Ratio Metrics and the Denominator Trap]] — extends
- [[Distribution Selection for Metrics]] — related
