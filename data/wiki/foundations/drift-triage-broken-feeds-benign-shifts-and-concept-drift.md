---
title: "Drift Triage: Broken Feeds, Benign Shifts and Concept Drift"
tags: [foundations, decision]
summary: "Input drift can scream while error is flat, and concept drift can double the error while inputs and predictions look identical; triage an alert by checking the pipeline first, then measuring error on labels, and retrain only for real harm."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--06-ml-platform--notes--04-drift.md
---

# Drift Triage: Broken Feeds, Benign Shifts and Concept Drift

A stale model keeps returning numbers in the same format at the same speed; its dashboards stay green while answers worsen. Drift is a change in the joint distribution p(X, y). **Real concept drift** changes p(y|X) (same inputs mean something else); **virtual drift** changes p(X) only. Only changes that affect the decision need adaptation. Patterns: sudden, incremental, gradual, reoccurring; a single outlier is not drift.

| Drift | What moved | Seen without labels? |
|---|---|---|
| Feature | an input's distribution | yes |
| Label | the target's distribution | no |
| Concept | input-to-target relationship | no |
| Prediction | the model's output distribution | yes |
| Reality | sudden world change | partly |
| Feedback | the model's output changes its own future data | partly |

A **broken feed** (a unit switch such as Fahrenheit to Celsius, miles to kilometres) is not drift. In an interview study, feedback delays were the most frequent failure, then "unnatural" drift (missing or corrupt data), then natural drift, which engineers who retrain often worried about least. Fix the pipeline before buying a detector. For credit-model simulations of these cases see [[Drift Types and What Monitors Can See]].

## Two experiments that break input-only monitoring

Setup: linear model on distance, 5,000 rows.

- **Concept drift, inputs still:** a mile takes longer (slope 4.5). KS on distance p=0.315, KS on predictions p=0.315 (identical, since predictions are a monotonic function of the one input), mean absolute error 2.35 to 4.71 minutes. Invisible without performance feedback.
- **Benign input drift:** distance scale 2.4. KS p=2.7e-113, error 2.35 to 2.36. The relationship holds and the model is linear.

Trees bucket out-of-range values while linear models extrapolate, so benign drift for one model is not benign for all: a depth-5 tree's error rose from 2.32 to 2.44 where the linear model stayed flat. In the image comparison cited in [[Drift Tests: Significance, Magnitude and False Alarms]], detected shifts (a shift in sixes at p=2.7e-10 against a Bonferroni threshold of 6.3e-5; rotation) were harmless. The authors split the job into detect, characterise and judge malignancy, the last estimated by labelling a few of the rows the domain classifier is surest about, needing two to three orders of magnitude fewer labels than labelling everything.

## Alert flow

1. Pipeline fault (units, nulls, a bad join)? Data incident: fix the feed, do not retrain; retraining on a broken feed teaches the model the bug.
2. Labels available? If not yet, label a sample of the most shifted rows or wait.
3. Error up beyond calibrated noise? Retrain, gate, roll out ([[Passive Retraining and the Promotion Gate]]). Otherwise benign: log it and adjust the monitor.

## Pitfalls

- Monitoring only inputs; concept drift leaves them alone.
- A frozen reference window: after a retrain it must move with the training set; anything fitted (histogram buckets, vocabularies) needs refitting too.
- Ignoring seasonality: compare with a matching window; a reoccurring concept is not a new one.
- Replaying history under feedback cannot compare adaptation methods properly.

## See Also
- [[Drift Tests: Significance, Magnitude and False Alarms]] — prerequisite-for
- [[Error-Stream Detectors and Retraining Policy]] — extends
- [[Drift Types and What Monitors Can See]] — related
- [[Model Rollout: Shadow, Canary and A/B]] — related
