---
title: "Gradient-Boosted Forecasting Relative to a Known Level"
tags: [foundations, pattern]
summary: "A regression tree cannot predict above anything it has seen, so divide target and lags by a level known at issue time; on a short single series this beat LSTM, TCN and DLinear, and quantile models give intervals whose coverage must be checked per fold."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--05-time-series-and-recommenders--notes--01-time-series-ml.md
---

# Gradient-Boosted Forecasting Relative to a Known Level

The feature-table approach: each row is a target hour, the columns are calendar fields plus lagged values legal at the issue time ([[Forecast Issue Time and Measured Leakage]]), and a gradient-boosted tree learns the mapping.

## The level problem

A tree predicts by averaging training targets in a leaf, so it is structurally capped by its training range. Mean demand on the worked series rose about 64% from the first year to the second, so every test hour sat above the training level. The fix is one line: divide the target and the lags by a recent level known at issue time (the mean of the previous week), let the tree learn the shape of a day relative to that scale, then multiply back. A Poisson loss suits a non-negative count. When the series crosses zero (net cash), use a trailing mean of absolute values as the level.

Six monthly folds, MASE: same hour yesterday 1.317, same hour last week 1.074, boosted on absolute values 0.906, boosted on values relative to level 0.786. The gain from the level division was larger than most tuning would give.

Extra feature ideas gave little on this short series: adding a four-week same-hour mean moved MASE only to 0.778, because it overlaps the weekly lags the trees already have. Trailing 365 days of training gave 0.789 and trailing 180 days 0.809, so dividing by level already removed most drift.

## Why trees, and global models

On a large public competition (42,840 hierarchical series, 28-day horizon) the top methods were pure machine learning, the winner an equal-weighted mean of six LightGBM models that improved on the best benchmark by 22.4%. Yet only 7.5% of teams beat that benchmark and 35.8% beat the seasonal naive. Essentially all of the top 50 trained one **global** model across many series (cross-learning), borrowing patterns between related series. See [[Global vs Per-Segment Forecast Models]].

## Sequence models, same backtest

Each takes 168 hours in and gives 24 out, with every window scaled by its own level (after log1p).

| Model | MAE | MASE | Train time |
|---|---:|---:|---:|
| DLinear | 64.710 | 1.056 | 2 s |
| LSTM | 63.632 | 1.039 | 56 s |
| TCN | 60.188 | 0.981 | 123 s |
| Boosted, relative | 48.172 | 0.786 | |

- **DLinear** splits the window into a moving-average trend and a remainder and fits one linear map on each; a single linear layer of this kind beat Transformer forecasters on nine long-horizon datasets, often by 20% to 50%, on the argument that attention loses temporal order.
- **TCN** stacks causal dilated convolutions so the receptive field grows exponentially ([[Dilated Causal Convolutions]]); left-pad only to stay causal.
- **DeepAR-style** recurrent models are designed for global training across many series and predict a distribution.

All three beat the naive rows but none beat trees given holiday flags and a calendar. The setup was one series, roughly 540 to 690 midnight windows, no tuning. The narrow lesson that holds: on a small tabular-style problem start with features and trees and require any deep model to beat that number in the same backtest.

## Intervals by quantile regression

Train one model per quantile with the pinball loss, then check coverage on the future. The nominal 80% interval (10% and 90% quantiles) covered 78.9% overall with mean width 158 bikes, but by month it ranged from 74.7% to 89.1%: a calibrated average can hide folds that are too narrow and others too wide. Separate quantile models can cross on a hard hour; sort them if a valid interval is required. Coverage as a testable claim: [[Confidence Interval Coverage and Wilson]].

## See Also
- [[Forecast Issue Time and Measured Leakage]] — prerequisite-for
- [[Forecast Baselines and Rolling-Origin Backtest]] — prerequisite-for
- [[Global vs Per-Segment Forecast Models]] — extends
- [[Weekly Seasonality Forecasting Methods]] — alternative-to (statistical methods for the same seasonal series)
- [[Dilated Causal Convolutions]] — related
