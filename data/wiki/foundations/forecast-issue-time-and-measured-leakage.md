---
title: "Forecast Issue Time and Measured Leakage"
tags: [foundations, pattern]
summary: "Fix the issue time, horizon, information set and loss before fitting; every feature lag must be at least the horizon, and three common leaks were measured on one hourly series."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--05-time-series-and-recommenders--notes--01-time-series-ml.md
---

# Forecast Issue Time and Measured Leakage

A forecast is a promise about data you cannot see, so shuffling rows and holding some out reports an accuracy that production will not deliver. Four things are fixed before any model is fitted:

- **Issue time**: when the forecast is made (midnight in the worked example).
- **Horizon**: how far ahead (1 to 24 hours).
- **Information set**: what is known at issue time. Calendar and all past values, but only a *forecast* of tomorrow's weather, never the actual weather.
- **Loss**: what an error costs (absolute error, since a van load is roughly linear in missed demand).

These decide which features are legal and how to validate. The baselines and the rolling-origin backtest are in [[Forecast Baselines and Rolling-Origin Backtest]]; the shift mechanics are in [[Time-Series Leakage: Shift and Rolling Windows]].

## Lags follow from the issue time

At midnight, the target at 23:00 can see 24 hours back at the earliest, so every lag is at least 24. One **direct** model then covers all 24 horizons with `hour` as a feature. The alternative, the **recursive** strategy, predicts one step and feeds it back in, which is compact but compounds errors. Stretching the horizon to a week forces every lag and the level to be at least 168 hours old: MASE rose from 0.786 to 0.880 (MAE 48.2 to 54.1 bikes), and same-hour-yesterday stops being a legal baseline while same-hour-last-week stays legal.

Reindex onto a complete calendar grid first. The raw file had 17,379 rows against 17,544 hours, so `shift(24)` on the raw rows would mean "24 rows ago", not yesterday.

## Three leaks, measured

All run against the same relative-to-level boosted model (honest MASE 0.786) over the same six monthly folds:

| Variant | MAE | MASE |
|---|---:|---:|
| Honest features | 48.172 | 0.786 |
| Lag of 1 hour (inside the horizon) | 25.597 | 0.419 |
| Actual weather instead of a forecast | 37.653 | 0.615 |
| Shuffled 5-fold on honest features | 43.4 | 0.747 |

- The 1-hour lag cuts error almost in half using a value nobody has at planning time.
- Actual weather is an upper bound on what a weather feed adds; in production only the forecast exists, with errors the model never trained on. Measuring it properly needs weather forecasts archived as issued.
- Shuffled folds flatter least here because every feature is at least a day old, but a 5% optimistic bias still changes a decision between close candidates.

## When K-fold is acceptable

Standard K-fold is valid for purely autoregressive models whose residuals are uncorrelated (checkable with a Ljung-Box test) and fails for underfit models with correlated errors. That does not rescue shuffled validation for a series with a drifting level, position-encoding calendar features and a decision made at a specific moment, so backtest forward.

## Pitfalls

- A rolling mean that ends at the target: `rolling(24).mean()` includes the current value; shift first by at least the horizon.
- Scaling or target-encoding on the full series leaks the future level; fit on the training fold only.
- Tuning on the final fold's noise turns the backtest into a training set.
- Report per-fold results: October was the only month above MASE 1 (1.091), invisible in the average. A storm in that month (22 rentals one day against more than 7,000 a day the week before) shows a calendar and lags cannot foresee an event, so a live model needs an input for it and an operational override.

## See Also
- [[Forecast Baselines and Rolling-Origin Backtest]] — prerequisite-for
- [[Time-Series Leakage: Shift and Rolling Windows]] — related
- [[Tabular ML Leakage Taxonomy]] — related (the non-time-series leak families)
- [[Gradient-Boosted Forecasting Relative to a Known Level]] — extends
