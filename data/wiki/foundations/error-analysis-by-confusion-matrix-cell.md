---
title: "Error Analysis by Confusion-Matrix Cell"
tags: [foundations, pattern]
summary: "Read a model's errors in order: name the positive class, set the table at the decision threshold, compare the four cells, read random rows before confident ones, then diagnose before touching the model."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--12-reading-the-errors.md
---

# Error Analysis by Confusion-Matrix Cell

A metric says how often a model is wrong; only the wrong rows say why. The procedure is six steps (name, profile, read, slice, diagnose, confirm). This page covers the first three plus the diagnosis table; slicing and confirmation are in [[Slicing Errors With Correction and the Rate Identity]], and guarding against fitting to what you read is in [[Eyeball and Blackbox Sets and Fixes That Fit the Reading]].

The running case is a boosted credit-default model with a 5:1 cost ratio, so the decline threshold is 1/6 (see [[Classification Metrics, Confusion Matrix and Thresholds]]). Base rate 22.1% (natural, not downsampled to 3%, so each cell has rows to read); eyeball set 1,500 rows with 332 defaulters.

## Step 1: name the errors, at the decision threshold

State which class is positive (here "will default", predicted positive = declined) and give each error its domain meaning: a false positive is a good customer declined, a false negative a defaulter approved. Flip the positive class and the names swap, so an unlabelled table cannot be read.

Set the table at the threshold the business uses, not the library default of 0.5. Same model, eyeball set:

| Threshold | TP | FP | FN | TN | Declined | Cost per 1,000 |
|---|---|---|---|---|---|---|
| 0.500 | 123 | 69 | 209 | 1,099 | 0.128 | 742.7 |
| 0.167 | 244 | 445 | 88 | 723 | 0.459 | 590.0 |

Approve-everyone costs 1,106.7. At 0.5 errors are mostly missed defaulters, at 1/6 mostly declined good customers; studying the 0.5 table fixes a problem the lender does not have. Accuracy falls from 81.5% to 64.5% at the cheaper threshold.

## Step 2: profile the four cells

Compare cell medians and standardised differences (0.2 small, 0.8 large). Two comparisons carry the information:

- **FN vs TP** shows which defaulters are missed: late months 0.10 against 2.73 (standardised gap -1.77), higher limits. The model finds defaulters who have already started missing payments.
- **FP vs TN** shows which good customers look risky: 1.14 SD more late months, smaller limits and payments.
- **FN vs TN** matters most. They look alike on status and late months (-0.12, 0.10). Among the approved, a fresh logistic on the same inputs separates FN from TN at ROC-AUC 0.699 against 0.683 from the model's own score, so little extra signal is available in these columns.

Calibration of the groups confirms it: approved rows defaulted at 10.9% against mean predicted risk 10.2%. A false negative at score 0.12 is a lost bet at 12%, not a mistake (compare [[Probability Calibration and Reliability Curves]]).

## Step 3: read rows, random ones first

Read random rows from each error cell before the most confident ones; confident mistakes are unusual by construction. Here the five most confident false positives were people six months behind at status 2 or 3, suggesting the model over-trusts payment status, while random false positives were large-limit customers with tiny bills who paid little, so the model treats a small payment as a warning. Treat any such reading as a story about a few rows, to be tested.

- Reading guidance: about 10 errors is very small, 20 rough, 50 good, 100 very good; 1,500 rows here held 533 errors, more than anyone reads. On a task humans cannot do from the row (credit default may be one) reading yields hypotheses, rarely certainties.
- **Check labels too.** 38 rows had no bill and no payment in six months, yet 13 (0.342) were labelled default, and the model declines all 13, so none are false negatives. Flag it for whoever owns the labels. Across ten widely used benchmarks at least 3.3% of test labels were wrong, enough that a ranking of two models can flip with 6% more mislabels. Fixing only the labels of misclassified rows biases the evaluation; audit correct rows as well.
- Per-row attribution says what drove the score, not why the person defaulted. The most confident FN (score 0.036) paid 60,396 on a 30,625 bill at status -1: everything visible looks excellent, so no reweighting of these columns would catch it ([[SHAP Attributions and the Limits of Explanations]]).
- Define each error group precisely and apply the definition to the whole set including correct rows; one group's share of errors ranged from 13.8% to 45.2% depending on definition in a review of published analyses (a 50 to 200 error sample is often under 5% of errors).

## Step 5: diagnose, then act

| Pattern | Meaning | Action |
|---|---|---|
| Errors identical to correct rows on every feature | Information is not in the data | New source or accept the limit |
| Labels look wrong | Label noise | Audit labels first |
| One group's errors concentrate | Underfit or small group | General feature, more data, partial pooling |
| FP and FN trade along the score | The threshold | Move it from the cost ratio |
| Errors grow with time | Drift | See [[Drift Types and What Monitors Can See]] |

High slice cost is not automatically underfitting: limits under 50k default at 34% so more land near the threshold. Check calibration inside the slice (predicted 0.310, actual 0.314 on the unread set) before changing the model.

Threshold sweep on the eyeball set preferred 0.13 (568.7 against 590.0 at 1/6), but on the unread set 0.13 cost 563.3 against 541.6 at 1/6, so the cost-ratio threshold stood.

## Pitfalls

- Reading the table at 0.5; reading only confident mistakes; calling a lost bet an error (about one in nine approved defaulters here, forecast in advance).
- Using a flat prior on a tiny slice: an "other education" group showed FNR 1.000 from one defaulter in 20 rows ([[Small-N Trap and Shrinkage]]).
- Adding a feature that knows the future: compare each new feature's timestamp with the decision's ([[Tabular ML Leakage Taxonomy]]).

## See Also
- [[Error Analysis, Bias and Variance Gaps]] — related
- [[Classification Metrics, Confusion Matrix and Thresholds]] — prerequisite-for
- [[Slicing Errors With Correction and the Rate Identity]] — extends
- [[Eyeball and Blackbox Sets and Fixes That Fit the Reading]] — extends
