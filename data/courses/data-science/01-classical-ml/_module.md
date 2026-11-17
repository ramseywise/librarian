---
imported_hash: addf0a27f859f04f
title: Classical ML
summary: 'The classical machine-learning toolkit for tabular data: linear models, trees, kernels, clustering and boosting, with the practices that make their scores believable.'
order: 1
objectives:
- Explain generalisation, bias, variance, and the train/validation/test contract (James et al.).
- Select a supervised model family and control complexity for a tabular prediction problem (Grinsztajn et al. on why trees still lead there).
- Build leakage-safe preprocessing and feature engineering pipelines.
- Choose a metric and threshold that reflect the costs of false positives and false negatives, then compare against a dummy baseline.
- Use clustering or dimensionality reduction cautiously, on numeric, categorical or mixed columns, validate the result, and avoid treating visual structure as proof.
- Compare ensembles and boosting libraries across seeds, tune with cross-validation and early stopping, and report uncertainty in a claimed improvement.
- Use permutation importance, PDPs, and SHAP appropriately while distinguishing model explanations from causal claims.
- Diagnose imbalance, recurring errors, and distribution shift before deploying a model.
- Start from the target to pick the family, loss, metric and baseline (Choosing a metric).
- Read false positives and false negatives before tuning, and fix a class of error on one split while scoring on another (Reading the errors).
- Split predictions into automate, review and reject, pricing the thresholds from error costs and review time (Automate, review or reject).
- 'Learn from corrections without trusting silence: measure label noise, test active learning against random, and audit a random sample (Learning from corrections).'
- Measure group gaps in a screening model, say which of them cannot be closed together, and state what an audit must report (Fairness in automated scoring).
- Detect anomalies with a density model, a classifier or an isolation forest, and fit a matrix-factorisation recommender on a ratings matrix (Unsupervised learning; DS 05 takes recommenders further).
source: learn-ai-engineering/data-science/01-classical-ml
readings_count: 11
---
