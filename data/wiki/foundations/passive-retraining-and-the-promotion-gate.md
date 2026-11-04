---
title: "Passive Retraining and the Promotion Gate"
tags: [foundations, pattern]
summary: "Retrain on a schedule, score champion and challenger on the same holdout newer than both, and move the alias only on a win beyond a margin; the gate decides what proceeds to rollout, not what users get."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--06-ml-platform--notes--02-experiment-tracking-and-model-registry.md
---

# Passive Retraining and the Promotion Gate

Passive retraining: on a schedule, train a new model, compare it to production on a holdout, and promote it only if it wins. It is preferred over anything more elaborate until it fails.

## The gate

```python
def promote_if_better(run_id, holdout, min_gain=0.0):
    champion = load("models:/taxi-duration@champion")
    challenger = load(f"runs:/{run_id}/model")
    c, n = rmse(holdout, champion), rmse(holdout, challenger)
    v = register(run_id)                  # always register, even a loser
    if n < c - min_gain:
        set_alias("champion", v)          # move the alias only on a win
```

Setup: ridge models on synthetic rides. A March retrain on an unchanged world scored 3.054 against the champion's 3.044 and was kept out: without a gate, a slightly worse model ships and nothing is learned. By May a mile costs more, the champion fell to 4.456 and the challenger scored 3.060, so it was promoted. Both versions stay registered ([[Model Registry Aliases and the Run Record]]); the loser is evidence.

## Rules

- Score both models on the same rows at decision time rather than trusting logged numbers.
- Use a holdout newer than both training sets, or one model has seen it.
- Set `min_gain` to a value you would defend: it protects against churn from noise, at the price of never promoting a run of small true gains.
- Same discipline as an LLM regression gate: floors for never-events, and a small win is noise until a paired test says otherwise.

## Limits

A single metric on a single holdout misses a model that wins on average and fails on one slice, and offline gains need not move the business metric: one booking platform reported across 150 models that offline gains did not translate directly to business value. A more accurate update can also hurt when people have learned how the old model behaves. So the gate admits a model to [[Model Rollout: Shadow, Canary and A/B]]; it does not decide what users get.

## See Also
- [[Model Registry Aliases and the Run Record]] — prerequisite-for
- [[Model Rollout: Shadow, Canary and A/B]] — extends
- [[Drift Types and What Monitors Can See]] — related (drift is what makes a challenger start winning)
- [[Statistical Test Selection]] — related
