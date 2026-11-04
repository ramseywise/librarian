---
title: Weekly Seasonality Forecasting Methods
tags: [foundations, comparison]
summary: Weekly data has a non-integer yearly period (about 52.18 weeks) and moving holidays; STL+ETS, dynamic harmonic regression and Prophet handle it differently, and most of their edge comes from knowing the calendar.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--06-applied-analyses--notes--01-forecasting.md
---

# Weekly Seasonality Forecasting Methods

A year is about 52.18 weeks: a long, non-integer seasonal period rules out classic seasonal methods that want a short integer period. Two standard answers are STL decomposition with a non-seasonal model on the remainder, and dynamic harmonic regression. Prophet is a third framing.

## The three models

- **STL + ETS.** STL splits trend, season and remainder by repeated local regressions; ETS forecasts the seasonally adjusted part and the season is added back. Cheap and robust, but it treats the season as a fixed 52-week pattern, so a moving event is learned only as a smear over neighbouring weeks.
- **Dynamic harmonic regression.** Season as sines and cosines at the true period of 52.18 weeks, plus a trend, an event flag and AR(1) errors. The number of sine/cosine pairs K controls wiggliness and is chosen by minimising AICc (K = 6 in the example), inside each backtest fold.
- **Prophet.** Curve fitting: a decomposable model of piecewise trend, Fourier yearly seasonality and holiday effects, with multiplicative seasonality when the peak grows with the level. Close to harmonic regression with an automatic trend and no explicit error autocorrelation. Its intervals come from simulating future trend changes assuming they resemble past ones, so treat them as an estimate.

Fit on the log scale where errors scale with the level; it also keeps forecasts positive.

## Moving events

Black Friday is the day after the fourth Thursday of November, so its week is not a fixed distance from last year's. Encode the rule as an event flag. A weekly series stamped on Mondays must put the event on the Monday of that week.

## What the backtest showed (eleven origins, 13 weeks ahead)

| Model | MASE |
|---|---|
| Seasonal naive | 1.21 |
| STL + ETS | 1.02 |
| Harmonic regression | 0.70 |
| Prophet | 0.63 |

Harmonic regression and Prophet were too close to bet on. Removing the Black Friday term from harmonic regression raised MASE from 0.70 to 0.98: most of the lead over STL+ETS came from knowing the calendar, not from the model form. These results describe the synthetic generator, which really did build the series that way.

## Outage weeks

Masking a one-week outage before fitting Prophet moved MASE only from 0.63 to 0.62, because a smooth fitted season barely moves for one low week; the seasonal naive is the method that copies the hole.

## See Also
- [[Forecast Baselines and Rolling-Origin Backtest]] — prerequisite-for
- [[Newsvendor Critical Ratio]] — extends
