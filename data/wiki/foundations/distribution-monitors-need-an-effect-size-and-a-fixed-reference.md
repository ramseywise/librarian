---
title: "Distribution Monitors Need an Effect Size and a Fixed Reference"
tags: [foundations, pattern]
summary: "Only a distribution monitor sees a silent unit change; threshold on an effect size such as the KS statistic rather than a p-value, keep an approved fixed reference, and start with prediction drift when labels arrive late."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--05-quality-and-observability--notes--02-monitors-and-lineage.md
  - data/raw/repos/learn-ai-engineering/data-engineering--05-quality-and-observability--notes--01-quality-dimensions-and-tests.md
---

# Distribution Monitors Need an Effect Size and a Fixed Reference

A test judges a batch against a written rule; a monitor judges it against history, so it finds failures nobody wrote a rule for. In a synthetic feed distance switched from miles to kilometres on 24 March: row counts and nulls did not move, only the values.

## KS D as the signal

Compare a column with a reference window (February) using the two-sample Kolmogorov-Smirnov test; the statistic D is the largest gap between the two cumulative distributions. Before the change D was at most 0.029 with no day at p<0.05 (22 days); after it D was at least 0.182 with all 8 days under 0.05, detected on the first day (0.0178 on 23 March, 0.2100 on 24 March).

## Why not the p-value

P-values degrade as data grows. In a published validation study, 100 million normal draws with 10 thousand replaced by a wider normal (a 0.01% change nobody would care about) triggered a chi-squared alert at the 1% level in 7 of 10 trials. The remedy is a distance with a threshold a team can reason about: L-infinity distance for categorical values (largest change in any value's probability, which also names the culprit), KS D for numeric. With about 3,000 rows a day the p-value still behaved; at far larger sizes it would not.

## Reference choice

- A rolling baseline absorbs a permanent shift: once more than half the window is post-change it treats the bug as normal. Keep a fixed, approved reference, roll it forward deliberately, and investigate any step that never reverts. A 14-day rolling reference made D small by 7 April with every distance still wrong.
- For models the reference should be data the model handles acceptably, from the same pipeline, with predictions attached; raw training data flags differences the model already handles.
- Declare column types (numeric vs categorical): location IDs guessed as numeric are tested wrongly.

## Model-side signals

Prediction drift needs no ground truth, so it is the first alarm when labels arrive late. For the unit change, drift score on the prediction went from 0.022 to 0.679. Per-column flags are noisy (one column drifted on a clean day), so require more than one column and two consecutive breaches before alerting. A report describes (scores, distributions); a test suite asserts pass/fail and is what to gate a pipeline on, but its preset was strict at small daily samples, so see how often a normal day fails first. Before a drift alert triggers retraining, rule out invalid data, a schema change and one outlier; retraining on bad data bakes the fault in.

Drift taxonomy (covariate, target, concept) and the multivariate case (embeddings compared with maximum mean discrepancy) are in [[Drift Types and What Monitors Can See]]; the score-level distance measure is [[Population Stability Index]].

## See Also
- [[Drift Types and What Monitors Can See]] — related
- [[Population Stability Index]] — related
- [[Same-Weekday Median and MAD Volume Monitor]] — related
- [[Data Quality Dimensions and Tests as Failing-Row Queries]] — prerequisite-for
