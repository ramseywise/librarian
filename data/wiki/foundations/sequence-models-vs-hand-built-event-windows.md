---
title: "Sequence Models vs Hand-Built Event Windows"
tags: [foundations, comparison]
summary: "On generated card events with a planted order-dependent fraud pattern, boosting on velocity windows and recent events beat a GRU (PR-AUC 0.855 vs 0.791); order matters, but hand-written order features may capture it, and untuned baselines hand the GRU undeserved wins."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--notes--05-sequence-models.md
---

# Sequence Models vs Hand-Built Event Windows

Before training a recurrent model on ordered events, ask what hand-built windows already capture.

## Setup

Generated charges with a planted fraud pattern: small online tests, then a large charge soon after, with decoys holding the same charges in another order or further apart. The pattern was chosen to favour order, so the result is a fact about this generator. Test days: 130 frauds, 0.27% base rate, time split, GRU reading the last 12 events.

## Results (PR-AUC with 90% bootstrap intervals)

- boosting on totals and 30-day counts and sums: 0.097 [0.083, 0.126]
- boosting on velocity windows plus last 3 events: 0.855 [0.820, 0.899]
- GRU over the last 12 event embeddings: 0.791 [0.746, 0.847]
- the velocity model with untuned large trees: 0.353 [0.275, 0.421]
- GRU with each window's order scrambled: 0.149

Order clearly matters (totals cannot see it; scrambling breaks the GRU), but gaps and the last three events are order written by hand, and beat the GRU by 0.061 (interval 0.025 to 0.098); they led on all three generated datasets, by 0.021 and 0.009 on the other two. The GRU got one architecture and no search and the pattern fits a short window, so this is not a verdict on GRUs. The large-tree row is the warning: first boosting settings overfit the few positives and handed the GRU a win it had not earned. Tune both on later days before comparing. See [[Forecast Baselines and Rolling-Origin Backtest]] for the same discipline in forecasting and [[Tabular ML Leakage Taxonomy]] for time-split hygiene.

## Drift

Concept shift is silent to [[Population Stability Index]]: when the fraud pattern changed, every model fell below 0.01 PR-AUC while PSI stayed at 0.002 or less. Late chargebacks also decide what labels hold: after the pattern changed, on days 360 to 420, retraining on everything reported so far reached 0.528 PR-AUC (boosting) and 0.491 (GRU), against 0.006 and 0.005 when training only on mature labels (older than 75 days). Mature labels contain none of the new pattern, so waiting for them keeps unreported fraud from counting as clean but blinds the model to change. These are one run on one generator; do not read 0.528 vs 0.491 as a ranking.

## See Also
- [[LSTM Forget-Gate Bias and Vanishing Gradients]] — related
- [[Forecast Baselines and Rolling-Origin Backtest]] — related
- [[Population Stability Index]] — related
