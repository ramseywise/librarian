---
title: Winner's Curse
tags: [foundations, concept]
summary: "When a test is underpowered, the estimates that reach significance are exaggerated: a true 1 percent lift with a 1 percent standard error had power 0.17, significant estimates averaged 2.5 times the truth, and some had the wrong sign."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--05-hypothesis-testing.md
---

# Winner's Curse

Select on significance and you select on luck. Estimates are truth plus noise; those that clear the threshold are disproportionately the ones where noise pushed upward.

## Numbers

True lift 1%, standard error 1%:
- power is only 0.17;
- among significant results the mean estimate was 0.0245, about 2.5x the true effect;
- 0.9% of significant results had the wrong sign.

The smaller the power, the worse the inflation: a win from a small test is likely an overestimate, and shipping on it then sees the lift shrink in the next measurement.

## Mitigation

- Power tests properly ([[Minimum Detectable Effect and Sample Size]]).
- Report the interval, not the headline estimate ([[P-Value Misreadings]]).
- Pick the best of many variants and expect regression toward the mean ([[Multiple Comparisons Corrections]]); shrink estimates toward the overall mean ([[Small-N Trap and Shrinkage]]).

## See Also
- [[Eval Error Bars and Sample Size]] — related
- [[Confidence Interval Coverage and Wilson]] — related
- [[Experiment Ramps and Overlapping Tests]] — related (portfolio-level inflation of shipped lifts)
- [[Partial Pooling for Segment Winners]] — extends
