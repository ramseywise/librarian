---
title: "Drift Types and What Monitors Can See"
tags: [foundations, pattern]
summary: "Covariate shift is loud and harmless, prior and concept shift are silent to input monitors, and feature skew can break a model while the score monitor barely moves; bin coded columns by level."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--10-imbalance-errors-and-drift.md
---

# Drift Types and What Monitors Can See

[[Population Stability Index]] (PSI) was computed per feature and on the score against a validation window, on simulated shifts applied to real held-out rows (about 2,400 rows, 72 defaulters per window, 20 seeds, a boosted model on a 3% default book). Cases:

| Scenario | Default rate | Worst feature PSI | Score PSI | ROC-AUC | Cost |
|---|---|---|---|---|---|
| No change | 0.030 | 0.011 | 0.007 | 0.764 | 141.0 |
| Covariate (low credit limits) | 0.036 | 0.319 | 0.083 | 0.759 | 169.0 |
| Prior (default rate doubles) | 0.060 | 0.011 | 0.008 | 0.757 | 262.661 |
| Concept (what predicts default changes) | 0.034 | 0.011 | 0.007 | 0.600 | 177.854 |
| Skew: features one month stale | 0.030 | 0.531 (by level; 0.049 quantile) | 0.012 | 0.726 | 152.3 |
| Skew: amounts in thousands | 0.030 | 7.706 | 3.291 | 0.753 | 145.081 |
| Skew: a status filled with 0 | 0.030 | 3.539 | 0.073 | 0.717 | 150.3 |

- **Covariate shift** P(x) moves, P(y given x) does not: loud, model still right (mean PD matches 0.036); the business decision changes.
- **Prior shift** is nearly silent: only 3% of rows changed, so rare classes hide from feature monitors.
- **Concept shift** is silent: features identical, PSI reads no labels; only outcomes (early delinquency as a proxy, then full labels) reveal it.
- **Train/serve skew**: the world has not moved but serving computes features differently. A late-join null filled with 0 collapsed declines from 2.4% to 0.1% (cost reaching the approve-everyone line) with score PSI only 0.073. A broken-units feed raised PSI to 7.7 with moderate harm.

Score monitoring alone misses most of this; watch inputs too. **Bin coded columns by level**: a recording change put 3,688 customers on one status code against 28 the month before; PSI by level went 0.031 to 0.927 while quantile bins said 0.050. PSI's noise floor here was 0.011 (max 0.014 over 20 seeds); the 0.1 and 0.25 lines are conventions to calibrate on your own windows. Where labels arrive about a year late, input and prediction monitors are what exists, and a broken feed is an incident rather than a reason to retrain.

## See Also
- [[Population Stability Index]] — prerequisite-for
- [[Imbalance Remedies Versus a Tuned Threshold]] — related
- [[Calibrated Score, Deterministic Decision Rule]] — related
