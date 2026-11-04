---
title: Sample Ratio Mismatch
tags: [foundations, pattern]
summary: "Compare arm counts with the designed split using a chi-square test before reading any outcome; a failure means users were lost or added non-randomly, the test is stopped rather than reweighted, and A/A tests validate the whole pipeline."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--03-experimentation-and-causality--notes--01-ab-testing.md
  - data/raw/repos/learn-ai-engineering/data-analytics--03-experimentation-and-causality--notes--03-experimentation-at-scale.md
---

# Sample Ratio Mismatch

A sample ratio mismatch (SRM) is a chi-square goodness-of-fit test of arm counts against the designed split. It runs before outcomes are read.

## Why a near-fair split can fail

- 50.4/49.6 on 2 million users gives p = 1.1e-29 (about 10^-29): with that many users, chance essentially never produces the gap, so something is removing or adding users to one arm.
- 42,400 vs 41,600 gives p = 0.0058; 10,000 vs 10,500 gives p about 0.0005.
- Platforms alert at a much stricter threshold than 0.05 (for example p < 0.001) because it runs on every test; set it from the number of tests and the cost of an investigation.

## The damage

In a simulation with no treatment effect, a logging bug that dropped 4% of one arm's users, all low value, produced a significant "win" (effect +0.036 on a mean of 1.00, p = 7.9e-03) and an SRM p of 9.8e-09. A team looking only at the outcome would ship it. The bias cannot be corrected by reweighting because you do not know who was lost: stop, find the cause, fix and rerun.

## Locating the cause

Slice counts by dimension until it localises (in one example only one browser was short). Follow the pipeline in order:

| Stage | Typical cause | Where to look |
|---|---|---|
| Assignment | hash correlated with another test, reused salt | counts by experiment overlap |
| Execution | redirect or new code loses users before logging | counts by browser and platform |
| Logging | bot filter or loss differs by arm | raw vs processed events |
| Analysis | filter that depends on treatment, wrong start date | counts by day, before and after each filter |

Dirty identifiers are a separate defect: some users appear in both arms or on the wrong page for their group. Cross-tabulate group by page first. Dropping them is reasonable, but if the off-diagonal is lopsided or duplicates differ by arm, the drop itself biases the result. An SRM can also arise per segment, so test counts within each segment (see [[Post-Treatment Segments and Simpson's Paradox]]).

## A/A tests

Run the whole pipeline with no change, continuously. About 5% of p-values should fall below 0.05 and they should be uniform (an A/A run gave a false-positive rate of 0.046 with about a tenth in each decile). A mismatch points to a broken variance estimate, usually an analysis unit that differs from the randomisation unit ([[A/B Test Lifecycle and Interval Decisions]]), or a poor assignment hash ([[Experiment Ramps and Overlapping Tests]]). An A/A's variance also sets sample size.

## See Also
- [[A/B Test Lifecycle and Interval Decisions]] — prerequisite-for
- [[Peeking and Sequential Testing]] — related
- [[Pseudoreplication and Intraclass Correlation]] — related
