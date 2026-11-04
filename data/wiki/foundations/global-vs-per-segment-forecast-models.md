---
title: "Global vs Per-Segment Forecast Models"
tags: [foundations, comparison]
summary: "Start with one global model plus the naive row, add the segment as a feature before splitting the data, and split only where later folds confirm it; one eight-fold table gave the wrong answer on synthetic cash-flow data."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--05-time-series-and-recommenders--notes--01-time-series-ml.md
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

Random partitioning can help a model constrained in complexity, which shows that similar series are not why global methods work; boosted trees are not so constrained, so random splits mostly cost data. Clustering knowledge can enter as features (a global network with features scored 0.7596 against 0.7632 for clustering by periodicity and 0.8149 plain, on one-step forecasts). Per-cluster recurrent models gained on one dataset (0.93 against 0.95 on 111 ATM series, where simple exponential smoothing at 0.87 beat both) and showed no significant difference on another.

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
