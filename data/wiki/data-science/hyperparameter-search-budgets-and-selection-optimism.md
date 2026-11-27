---
title: "Hyperparameter Search Budgets and Selection Optimism"
tags: [data-science, classical-ml, pattern]
summary: "Random, grid and TPE searches tie when the plateau is wide; the winner's score is optimistic by an amount set by how few rows chose it, so report on untouched rows or nested folds."
updated: 2026-11-20
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--09-training-and-tuning.md
  - data/raw/papers/2026-11-08-raissi-2023-open-problems-applied-deep-learning.md
  - data/raw/papers/2026-11-08-bergstra-2012-random-search-hyper-parameter-optimization.md
  - data/raw/papers/2026-11-08-bergstra-2011-algorithms-hyper-parameter-optimization.md
  - data/raw/papers/2026-11-08-akiba-2019-optuna.md
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

Choosing the best of 32 partly selects luck. Selecting on n rows and scoring the winner on others: 100 rows, winner 0.9308 there, 0.9223 elsewhere, optimism 0.0085 (no better than default); 300 rows 0.0046; 1,000 rows 0.0013; 3,256 rows 0.0015. The course note credits Cawley and Talbot (JMLR 2010) with showing that the variance of the selection score may choose the worse model, with a resulting bias comparable to the gaps between algorithms.

Honest options: refit the chosen configuration on all development rows and read the test once (tuned AUC 0.9272 against default 0.9263, bootstrap 95% interval 0.9209 to 0.9337, accuracy 0.873 unchanged; logistic 0.9013), or nested cross-validation (5 outer folds, 8 tries, 3 inner folds: outer mean 0.9274, sd 0.0036, 125 fits; inner best 0.9243, lower because inner models train on less data; all folds chose learning rate 0.097). Nested scores a procedure, not a model, so run the search once on all data to ship; it earns its cost with few rows and many tries. Tuning gained 0.0009 while moving from logistic to boosting gained 0.025: choose the family and features first. See [[Cross-Validation Variants and Nested Search]].

Pitfalls: reading test while still deciding; tuning on too few rows; a winner at the edge of its range (use log ranges, widen at bounds).

## Search as a bi-level problem

Raissi's position paper frames the iteration step as a bi-level optimisation: an inner loop minimises training loss over the weights, and an outer loop optimises a validation metric over the hyperparameters. It calls this step the costliest in time and resources of the whole pipeline, and often neglected, offering no data for the claim. It cites neural architecture search for image classification at about 450 GPUs for 3 to 4 days, and parameter sharing (warm-starting from shared weights kept in memory) cutting the cost by up to 1000x, in some cases to about 16 GPU-hours; both numbers are cited from other work. The paper advises keeping the split to train, validation and test rather than fragmenting data further to tune the extra hyperparameters, and says weights for combining several metrics (accuracy with latency or memory) are an open problem.

Limits of this section: the paper is a position paper with no experiments or measurements of its own, written in January 2023; its proposed directions are untested, and it says whether AutoML carries beyond simple supervised problems such as image classification remains to be tested.

## What the original papers measured

Bergstra and Bengio (JMLR 2012) compared random search with grid search on single-hidden-layer networks over 8 datasets, with 256 random trials per dataset subsampled into experiments of 1 to 32 or 64 trials, against published grid results from earlier work averaging 100 trials. In the 7-hyperparameter space, 8 random trials matched or beat the grid; in a 9-hyperparameter space that adds preprocessing, 32 trials were needed to beat it consistently (self-reported). A Gaussian-process fit with per-hyperparameter length scales gave an effective dimension of 1 to 4, varying with the dataset, with the learning rate always among the important ones (self-reported). On a 32-hyperparameter, 3-layer deep belief network (128 random trials against a manual-plus-grid search averaging 41), random search was better on 1 dataset, equal on 4 and worse on 3 (self-reported). Their simulation found latin hypercube sampling no better than random search. Their limits: all strategies studied were non-adaptive, the grid results were not re-run, only shallow networks on small image datasets were used, and exact accuracies appear only in figures.

The sequential comparison and its test errors are on [[Tree-Structured Parzen Estimator (TPE)]]. Optuna's authors report, for a simplified AlexNet on SVHN (one Tesla P100 per study, 4 hours, 40 repeats), about 36 trials per study without pruning for both TPE and random search, and about 1279 (TPE) and 1119 (random search) with asynchronous successive halving pruning, nearly all of them pruned (self-reported). The extraction notes that the gain blends exploring more trials with pruning more of them early, comes from one task, and has no confidence intervals in the text.

## See Also
- [[Cross-Validation Variants and Nested Search]] — extends
- [[Cross-Validation Fold Spread and Choosing the Splitter]] — related
- [[Train, Validation and Test Discipline]] — prerequisite-for
- [[Gaussian Processes and Bayesian Optimisation]] — alternative-to
- [[Bootstrap Resampling and Its Failures]] — related
- [[Tree-Structured Parzen Estimator (TPE)]] — extends
- [[Scaling Per-Entity Model Tuning: SparkTrials versus Grouped Fits]] — related
- [[ImageNetV2 and the Adaptivity Gap in Test-Set Reuse]] — related
