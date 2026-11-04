---
title: "Hyperparameter Search Budgets and Selection Optimism"
tags: [foundations, pattern]
summary: "Random, grid and TPE searches tie when the plateau is wide; the winner's score is optimistic by an amount set by how few rows chose it, so report on untouched rows or nested folds."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--09-training-and-tuning.md
---

# Hyperparameter Search Budgets and Selection Optimism

A hyperparameter is a setting chosen, not learned; knobs interact, so one curve per knob is not enough ([[Regularisation Knobs and Early Stopping]]).

## Search methods

Grid tries every combination (4 values on 5 knobs is 1,024 fits). Random search draws each knob from a range: usually only a few knobs matter and you do not know which, so 9 random trials test the key knob at 9 values where 9 grid trials test 3; published work found 1 to 4 knobs mattered in a 7-knob problem and 8 random trials matched grids averaging 100. Trials are independent. Bayesian search (tree-structured Parzen estimator) splits past trials into good and bad, models each, and tries the setting with the highest good-over-bad density ratio; on a 32-dimensional problem it reached 14.13% error against 18.97% for random. Pruning stops trailing trials: 35.8 trials in four hours without it, 1,278.6 with.

## What happened at 32 fits (boosting, adult, 5 seeds)

Search/report rows are halves of the validation set. Default settings: 0.9222 search, 0.9244 report. Report AUC at 32 fits: grid 2x2x2x2x2 0.9285, grid 4x4x2 0.9269, random 0.9277, TPE 0.9281. All finished within 0.0003 on search rows and 0.0016 on report rows, near seed spread (0.0005 to 0.0008), each 0.0025 to 0.0041 above default. Much of the value is avoiding bad settings (worst trials averaged 0.8995 to 0.9118). They tie because the plateau is wide, the learning rate carries about 0.61 of importance (rough, 32 trials), the grid values came from knowing good boosting settings, and TPE's first 10 trials are random. The grid tried 2 learning rates, random 32.

| Situation | Use |
|---|---|
| One or two knobs, cheap fits | Grid |
| Several knobs, unfamiliar problem | Random, the baseline to beat |
| Costly fits, many knobs | TPE plus pruning |
| Boosting rounds | Early stopping, not search |

## The winner's score is optimistic

Choosing the best of 32 partly selects luck. Selecting on n rows and scoring the winner on others: 100 rows, winner 0.9308 there, 0.9223 elsewhere, optimism 0.0085 (no better than default); 300 rows 0.0046; 1,000 rows 0.0013; 3,256 rows 0.0015. Selection variance can pick a worse model and the bias can be as large as differences between algorithms.

Honest options: refit the chosen configuration on all development rows and read the test once (tuned AUC 0.9272 against default 0.9263, bootstrap 95% interval 0.9209 to 0.9337, accuracy 0.873 unchanged; logistic 0.9013), or nested cross-validation (5 outer folds, 8 tries, 3 inner folds: outer mean 0.9274, sd 0.0036, 125 fits; inner best 0.9243, lower because inner models train on less data; all folds chose learning rate 0.097). Nested scores a procedure, not a model, so run the search once on all data to ship; it earns its cost with few rows and many tries. Tuning gained 0.0009 while moving from logistic to boosting gained 0.025: choose the family and features first. See [[Cross-Validation Variants and Nested Search]].

Pitfalls: reading test while still deciding; tuning on too few rows; a winner at the edge of its range (use log ranges, widen at bounds).

## See Also
- [[Cross-Validation Variants and Nested Search]] — extends
- [[Cross-Validation Fold Spread and Choosing the Splitter]] — related
- [[Train, Validation and Test Discipline]] — prerequisite-for
- [[Gaussian Processes and Bayesian Optimisation]] — alternative-to
- [[Bootstrap Resampling and Its Failures]] — related
