---
title: "Error-Stream Detectors and Retraining Policy"
tags: [foundations, pattern]
summary: "When labels arrive, Page-Hinkley or CUSUM on the error stream trades detection delay against false alarms with no free setting; label delay decides whether this is possible, and scheduled retraining is the defensible default over triggers."
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--06-ml-platform--notes--04-drift.md
---

# Error-Stream Detectors and Retraining Policy

If labels arrive, the error stream is the best drift signal and can be tested online. Sequential analysis keeps a running statistic needing no stored window: CUSUM is `g_t = max(0, g_{t-1} + x_t - delta)` with an alarm when `g_t > lambda`; Page-Hinkley is a close variant. Statistical-process-control methods (DDM) warn at two standard deviations above the best error seen and act at three. Sequential and SPC methods use constant memory; two-window tests grow with the window.

## Delay against false alarms

Page-Hinkley on ride-level absolute error, change at ride 3000 (slope 3.2 to 4.5), 20 streams per threshold:

| Threshold | Fired before the change | Mean delay after | False alarms, stable |
|---|---|---|---|
| 15 | 20 of 20 | - | 20 of 20 |
| 50 | 14 of 20 | 21 | 20 of 20 |
| 100 | 1 of 20 | 43 | 1 of 20 |
| 200 | 0 of 20 | 86 | 0 of 20 |
| 400 | 0 of 20 | 179 | 0 of 20 |

No free setting: each doubling of the threshold roughly doubles the delay. Evaluate both delay of detection and false-alarm rate measured on drift-free data; pick the lowest threshold with none. Fed 12 monthly error aggregates, the detector has almost no evidence: use ride-level errors.

## Label delay decides what is possible

Predictions served before the first label at 450 an hour (an invented rate for scale): 225 for a 0.5 h label (taxi duration), 486,000 for a 45-day chargeback, 3,942,000 for a one-year loan default. Short delay: performance monitoring works. Long delay: it is retrospective, leaving input and prediction monitors (which can mislead both ways, see [[Drift Triage: Broken Feeds, Benign Shifts and Concept Drift]]) plus proxies and sampled labelling. Record the delay per model.

## Retraining policy

Blind adaptation retrains on a schedule; informed adaptation waits for a trigger. Compared on a model retrained with labels a month late, trigger = month's error 20% above the first quarter's:

| Change | Policy | Retrains | Mean MAE | Worst month |
|---|---|---|---|---|
| sudden (month 6) | never | 1 | 3.72 | 4.72 |
| sudden | monthly | 13 | 2.58 | 4.67 |
| sudden | triggered | 2 | 2.58 | 4.64 |
| gradual | never | 1 | 3.34 | 4.67 |
| gradual | monthly | 13 | 2.42 | 2.48 |
| gradual | triggered | 3 | 2.71 | 3.11 |

(Counts include the first fit.) A trigger matches monthly on sudden change with fewer trainings, but lags on gradual change since drift must accumulate to 20%. No policy avoids the first bad month after a sudden change, so fallback and rollback belong in the plan. Start blind: passive retraining first, active only when it fails, since active systems are more complex. Observed cadences run from hours to months, set without a scientific procedure; defend a schedule by experiment. Any retrain goes through [[Passive Retraining and the Promotion Gate]].

## See Also
- [[Drift Triage: Broken Feeds, Benign Shifts and Concept Drift]] — prerequisite-for
- [[Passive Retraining and the Promotion Gate]] — extends
- [[Peeking and Sequential Testing]] — related
- [[Concept-Drift Detector Families and Prequential Evaluation]] — extends (the full detector taxonomy)
