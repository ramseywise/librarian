---
title: Forecast Grader Thresholds
tags: [eval, reference]
summary: The pass/fail contract for time-series forecast evaluation — MASE against a naïve baseline, SMAPE, directional accuracy, and prediction-interval coverage — with the diagnostic each failure points to and the drift ratio that triggers retraining.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/atlas/skills/ml-experiment/SKILL.md
  - data/raw/claude-docs/atlas/skills/eval-report/SKILL.md
---

# Forecast Grader Thresholds

Forecast evaluation differs from LLM evaluation in one structural way: the graders are
deterministic numeric functions, so there is no judge to calibrate (contrast
[[LLM Grader Calibration Insights]]). What must be chosen instead is the *baseline* and the
*threshold* — and the baseline is what makes MASE meaningful.

## The grader suite

```python
from evals.graders.graders import EvalHarness, MASEGrader, SMAPEGrader, DirectionalGrader

harness = EvalHarness(graders=[MASEGrader(), SMAPEGrader(), DirectionalGrader()])
result = harness.evaluate(actuals, predictions, baseline_predictions)
```

Note `baseline_predictions` is a required argument, not optional — MASE is *defined* relative
to a naïve forecast, so the harness cannot score without one.

## Thresholds and what a failure means

| Grader | Metric | Pass | Failure means |
|--------|--------|------|---------------|
| MASE | vs naïve lag-7 | < 1.0 | Worse than naïve — diagnose feature set, check preprocessing |
| SMAPE | symmetric % error | < 15% | Large percentage errors — check outliers, try log transform |
| Directional | % correct direction | > 55% | Not better than random — model isn't capturing trend |
| Coverage | % of actuals inside 80% PI | ≥ 75% | PI too narrow — increase uncertainty estimation |

**MASE ≥ 1.0 is the load-bearing failure.** It means the model loses to lag-7 — repeating
what happened a week ago. A model can have respectable SMAPE and still fail here, which is
exactly the case worth catching: absolute error looks acceptable while the model adds nothing
over a one-line heuristic.

Directional accuracy is scored against 50% (a coin flip), not 0 — hence a 55% pass bar. The
gap between 50% and 55% is deliberately narrow because directional accuracy on noisy series
is hard-won.

## Drift as an advisory signal

| Signal | Interpretation | Action |
|--------|---------------|--------|
| Drift ratio > 1.4 | Model degrading over time | LoRA fine-tune trigger |
| DriftGrader warning | Advisory only | Monitor — not a hard gate |

The split matters: `drift_ratio > 1.4` is a *numeric trigger* wired to retraining, while the
DriftGrader's own warning is explicitly advisory and does not gate. Drift is measured across
eval cycles from `drift_log.jsonl`, so it is a property of the eval *history*, not of any
single run — a distinction that makes it unsuitable as a per-run gate.

## The at-risk band

Any grader within 10% of its threshold is flagged **at risk** even when currently passing.
This converts a binary gate into a leading indicator: a MASE of 0.95 passes but is one bad
week from failing, and surfacing that before it breaks is the point.

## See Also
- [[Atlas Project]] — instance-of
- [[Eval vs Test Distinction]] — prerequisite-for
- [[Golden Set Mechanics]] — alternative-to
