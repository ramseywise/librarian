---
title: Forecast Baselines and Rolling-Origin Backtest
tags: [foundations, pattern]
summary: A forecasting model earns trust only by beating free baselines (seasonal naive above all) across many rolling origins, scored with a scaled error plus bias, with the final origin held back as an untouched exam.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--06-applied-analyses--notes--01-forecasting.md
---

# Forecast Baselines and Rolling-Origin Backtest

The discipline that decides which forecasting model is allowed to feed a decision. A forecast is only good relative to what could be done with no effort, and one train/test split is one anecdote.

## Baselines first

Four zero-cost benchmarks: the **mean** of history, **naive** (last value), **seasonal naive** (value one season ago), and **drift** (line from first to last point, extended). For a seasonal series the seasonal naive is the one to beat: it knows the season, needs no fitting, and fits in a spreadsheet. A model that cannot beat it has added cost and no information.

Its two weaknesses: it ignores growth (runs low on a growing series) and it copies last year's anomalies, including outages. In the worked backtest its bias was about +185 units a week on a series growing 6-11% a year.

## Rolling-origin evaluation

Fit on everything up to a date, forecast the horizon (13 weeks in the example), step forward, repeat. Only train on the past: random k-fold lets the model see the future of the series it forecasts. Any tuning choice (such as the number of Fourier pairs K) is made inside each fold from that fold's own past.

- Twelve origins, 13 weeks apart: the first eleven choose the model, the twelfth is the **exam** and stays locked until model and buffer are chosen. Once the exam guides a choice it becomes a selection set and its score is flattering.
- One quarter cannot rank models: on the exam, STL+ETS beat harmonic regression 0.85 to 0.90 MASE, the reverse of the eleven-origin ranking.

## Which error measure

- MAE leads to forecasts of the median, RMSE to the mean, so they can legitimately disagree.
- Percentage errors (MAPE) are undefined near zero and penalise over- and under-forecasting unequally.
- **MASE** divides each error by the in-sample MAE of a naive method (seasonal naive for seasonal data): unit-free, defined at zero. It is a one-step in-sample scale, a harder target than a 13-week-ahead out-of-sample error, so the seasonal naive itself does not score exactly 1 (it scored 1.21 across eleven origins).
- Report **bias** (mean of actual minus forecast; positive means under-forecasting) separately. For staffing, a consistent shortfall means being understaffed every week, which scatter metrics hide.

## Interval coverage is testable

An 80% interval should contain about 80% of outcomes. Measured on the backtest: harmonic regression 93.0% (too wide), Prophet 74.8% (slightly narrow), STL+ETS 47.6% (it cannot see the moving event). Never quote an interval without measuring coverage on your own backtest.

## Tripwire

Keep the seasonal naive running beside the chosen model; if the model's rolling MASE rises above the benchmark for a few weeks, stop trusting it and investigate.

## Pitfalls

- Treating supply-capped periods (outage, stock-out) as demand: mark them missing or give them their own event.
- Reading MASE as relative to the benchmark's own forecast.
- Comparing models on data whose generator was built to suit one of them (handing a model the true moving-event rule is flattering in general).

## See Also
- [[Weekly Seasonality Forecasting Methods]] — extends (the three models that beat the baseline)
- [[Newsvendor Critical Ratio]] — extends (turns the backtest error distribution into a stocking or staffing quantile)
- [[Confidence Interval Coverage and Wilson]] — related (coverage as a testable claim)
- [[Label Horizon vs Sampling Window]] — related
