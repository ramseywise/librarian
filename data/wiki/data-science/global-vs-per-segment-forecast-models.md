---
title: "Global vs Per-Segment Forecast Models"
tags: [data-science, comparison]
summary: "Start with one global model plus the naive row, add the segment as a feature before splitting the data, and split only where later folds confirm it; one eight-fold table gave the wrong answer on synthetic cash-flow data."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-science--05-time-series-and-recommenders--notes--01-time-series-ml.md
  - data/raw/papers/2026-11-08-montero-manso-2021-locality-globality.md
  - data/raw/papers/2026-11-08-bandara-2020-forecasting-across-time-series.md
---

# Global vs Per-Segment Forecast Models

Question: with hundreds of series grouped into segments, does training one model per segment beat one **global** model across all of them? The evidence here is a synthetic study (400 businesses, 156 weeks of signed weekly cash, segments from clustering frozen at the first issue date, four-week horizon, eight walk-forward issue dates), so it shows a method, not how real customers behave. The model is the boosted setup of [[Gradient-Boosted Forecasting Relative to a Known Level]], scored by MASE against the same-week-last-year naive.

## Result on one world (segment-total MASE)

| Model | Planted | Control |
|---|---:|---:|
| Naive, same week last year | 1.234 | 1.413 |
| Local MSTL on each total | 1.136 | 1.355 |
| Global GBM | 0.945 | 1.070 |
| Global plus a segment feature | 0.930 | 1.093 |
| One GBM per segment | 0.961 | 1.082 |
| One GBM per random group | 0.936 | 1.035 |
| One GBM per true archetype | 0.897 | n/a |

The control world has no archetypes. The true-archetype row is a ceiling reachable only inside a generator. Read each score against the naive row: the naive itself exceeds 1 because test weeks are harder than the history that scales it.

## One world misled

On that single world per-segment (0.961) lost to global (0.945) and random groups (0.936) looked fine, suggesting segments do not help. Five fresh worlds reversed it. Averaged segment-total MASE on planted worlds: global 1.105, segment as feature 1.026, per segment 1.024, random groups 1.115. The feature beat global in all five worlds, per segment in four, random groups in one. On control worlds the gain vanished (0.999, 1.004, 1.014, 1.007 for the non-global variants). So segments help only where real structure exists, and a feature gets as much as a split while keeping one model to maintain. For single customers the gain nearly disappears (1.133 global against 1.126 and 1.137).

A separate model can still be worth keeping for one segment: on a 161-customer segment merging two behaviours, naive scored 1.816, global 1.123, global with feature 0.981, per segment 0.807, while in the other four groups per segment lost to global. Why was not tested.

## Literature fit

Two papers bear on the question.

**Montero-Manso and Hyndman** (self-reported) argue that global methods work without similar series. They lag-embed every series, stack them and fit one regression, forecasting one step ahead and scoring MASE on about 17 datasets. One global linear AR(25) over the 617 M1 Monthly series is reported to outperform the leading local methods, using 25 parameters where auto.arima uses about 1600. Splitting a set at random into 10 equal groups and fitting one global linear model per group still helped in most datasets where the global model was complexity-constrained, which they take as evidence that similar series are not the cause; they call it a showcase of theory, not a recommendation. On M4 one-step MASE (AR(12)) the three local methods scored 0.7618 (auto.arima), 0.7644 (ets) and 0.7745 (theta), all ahead of a plain global deep network at 0.8149; splitting M4 by periodicity into one deep network per cluster scored 0.7632, and the best row was a global deep network that took frequency and other features as inputs. The course note gives 0.7596 for that last row; the extraction names 0.7596 only in its Limits, without tying it to a Results row.

**Bandara, Bergmeir and Smyl** (self-reported) train one LSTM per cluster of series, grouped by 18 features and a Snob mixture model, against one LSTM over all series. On NN5 (rolling origin, 56-day horizon, 111 daily ATM series) mean MASE was 0.93 for the clustered LSTM and 0.95 for the single LSTM, while exponential smoothing (ES and ETS) scored 0.87; the clustered model beat the single LSTM significantly (paired Wilcoxon p = 7.22e-4) and never beat the smoothing benchmarks on any measure. On CIF2016 (72 monthly series, fixed origin) its mean sMAPE of 10.53 was the lowest among entrants (10.69 for the single LSTM), but the three LSTM variants were not significantly different (aligned Friedman p = 0.8010).

The two papers pull in different directions: Montero-Manso and Hyndman say similar series are not essential (and put a clustering analysis out of scope, while their own per-periodicity networks beat the plain global one), and Bandara and colleagues report a significant gain from clustering on NN5 but no significant difference on CIF2016.

The course note adds that boosted trees are not complexity-constrained the way a global linear model is, so in this page's setting random splits mostly cost data.

## Limits

- Montero-Manso and Hyndman: the bounds are worst-case and loose, assume independent series, and tighter bounds would not by themselves mean lower out-of-sample error. There are no seeds, repeats or significance tests, and the table differences are small and single-run (0.7596 against 0.7632). The deep network and trees were not tuned. On the dominick and parts (intermittent) datasets longer memory did not help, and the authors have no explanation.
- Bandara and colleagues: only two datasets (CIF2016, NN5), with M3 excluded by the authors because its series are not similar. CIF2016 holds 48 artificial series, and the clustering applies only to its 57 horizon-12 series. Rolling-origin LSTMs were not re-fitted while the benchmarks were. Significance testing uses sMAPE only, hyperparameters, seeds and run counts are not reported, and the model is an LSTM on a discontinued toolkit, with no M4 or N-BEATS-style comparison.
- The synthetic cash-flow study above comes from the course note; these two papers do not test that setting.

## What broke

- SMAPE and MASE disagreed: the four-weeks-ago naive beat the global model on SMAPE (105.0 against 123.7) and lost on MASE, because net cash passes through zero and SMAPE divides by something near it.
- A SMAPE target of 15 was out of reach for every model, so it says nothing about them.
- Direction is coarse: four weeks give three changes to call per fold; on the control, 43.1% (global) and 62.5% (random groups) on 72 calls is too few to read.
- Single customers are far harder than totals (1.145 against 0.945 for global): a forecast fit for a segment plan is not fit for one account.

## Procedure

Start with one global model and the naive row beside it. Add the segment as a feature before splitting data. Split only for a segment that wins across later folds. Compare any gain with random groups and a control, and repeat on more than one world.

## See Also
- [[Gradient-Boosted Forecasting Relative to a Known Level]] — prerequisite-for
- [[Forecast Baselines and Rolling-Origin Backtest]] — prerequisite-for
- [[Clustering Validation Against Named Baselines]] — related (random and control baselines for a clustering)
- [[Partial Pooling for Segment Winners]] — related
