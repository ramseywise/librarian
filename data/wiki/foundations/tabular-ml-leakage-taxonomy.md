---
title: Tabular ML Leakage Taxonomy
tags: [foundations, eval, reference]
summary: Six leakage classes for tabular ML — target, temporal, group, fit-before-split, resampling outside the fold, train/serve skew — all answering one question ("at the moment this line runs, what does it know that it would not know at prediction time?"), plus why a leakage verdict needs the person who knows how the data was collected, not a correlation ranking.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/skills/review-leakage/SKILL.md
  - data/raw/claude-docs/galactus/skills/prototype-genesis/SKILL.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-11-gal-4-phase2-ml-fraud-poc.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-11-gal-4-phase2-ml-fraud-poc.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-10-ml-capability-parity.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-10-ml-capability-parity.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-15-lending-parity.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-15-lending-parity.md
---

# Tabular ML Leakage Taxonomy

The galactus `review-leakage` dimension reduces data leakage to a single question asked
of every `fit` and every split:

> *At the moment this line runs, what does it know that it would not know at prediction time?*

If the answer is anything at all, that is a finding. **Most leaks are correct operations in
the wrong order.** `fit_transform` before `train_test_split` is two valid lines, and their
sequence is the bug.

## The six classes

| Class | Shape | Notes |
|---|---|---|
| **Target** | Post-outcome columns (`settlement_date`, `amount_recovered`, `*_final`, `*_actual`), label proxies, IDs assigned after the outcome, aggregates over the full frame | Check what the matrix *keeps*: `df.drop(columns=["label"])` keeps every other post-outcome column. A correlation above ~0.95 or an AUC above ~0.97 on a "hard" problem is a leak until explained. Flag the *unexplained* score |
| **Temporal** | Random split or (Stratified)KFold when a date/cohort column exists; lag/rolling features with no `as_of` cutoff; imputation or scaling stats taken from the whole time range | Trains on the future to predict the past |
| **Group** | One entity (debtor, patient, user) on both sides of a row-level split | **A group key present in the frame but not passed to the splitter is a finding.** Weak keys are stated, never suppressed. One lending proxy had 1.03% of rows in multi-row groups (max size 3), recorded as "group leakage is effectively unexercised" |
| **Fit before split** | Scalers, imputers, encoders, selectors or PCA fitted on the full frame; target encoding outside the fold; top-k feature selection over all rows | The leak survives a perfectly correct downstream split. Name the fix: transform and estimator in one `Pipeline` |
| **Resampling outside the fold** | SMOTE / over- or under-sampling / Tomek / ENN before the split, or on validation data | Synthetic rows interpolate held-out data into training. Use a sampler inside an `imblearn` pipeline |
| **Train/serve skew** | Same feature name, different formula at inference; model saved without its transform; no schema check at load | Renamed or reordered columns produce wrong predictions rather than errors |

**What not to flag:** EDA that never fits a scored model; a deliberate full-data refit
*after* evaluation, when the code says so; a high AUC that the code explains (a genuinely
separable problem, a synthetic fixture). Leakage that already existed is flagged
`pre_existing: true` only if the diff makes it load-bearing.

## Why the name heuristic is not enough

In the lending POC, `last_fico_range_high` / `last_fico_range_low` scored **AUC 0.9511
against the label**, with no post-outcome name pattern and zero nulls. No regex catches
that. Only a single-feature scan does, so a missing scan is reported as a finding rather
than an empty result (see [[An Unrun Scan Is Not a Clean Scan]]).

## Leakage is decided with the operator, not by the numbers

`/prototype-genesis` (the ML prototyping interview) pushes the leakage verdict to its
feature-decision gate on purpose. Two things have to be present: real columns on screen,
and an operator who knows how the data was collected.

- A strongly correlated column is equally consistent with "leak" and "the best feature you
  have." The correlation scan produces *candidates*. The operator produces the *verdict*.
- **A prior-history column is not a leak just because it is predictive.** If subjects recur,
  earlier repayment behaviour is exactly what a lender would legitimately use. The test is
  "would this value already be known at decision time?" If yes, it is a feature however
  predictive. If it was recorded because the outcome happened, it is a leak however weak.
  The same column gets a different answer depending on where the frame is cut.
- If provenance is unavailable, park the question as **blocking** with a resolving trigger
  and mark the run provisional. Do not silently pick the conservative option: excluding a
  real feature and including a real leak are both errors, and only one of them shows up
  later.
- Exclusions carry their reason in an `EXCLUDED` dict, not in memory. A column in none of
  the categorical/numeric/ordinal/excluded lists is silently dropped, so **unaccounted
  columns are the gate.**
- When reading results, report the margin over baseline against fold variance, the
  positives per fold, and an explicit no-transform-leakage assertion. A result that looks
  better than it should is a reason to re-read the leakage answer, not to celebrate.

## A toolkit that manufactures target leakage

Column-type inference can create leakage on its own. In the galactus ML toolkit, any
column with more distinct values than a cardinality threshold (50) was bucketed as
`high_cardinality`, and the preprocessor **target-encoded** that bucket. A row-unique
`uuid` (800 distinct over 800 rows) then became a near-perfect memorisation feature
against 14 positives. The same defect had already appeared on an earlier lending frame
(a group key with ~39.5k distinct values). The recurrence was itself recorded as a
finding: *the toolkit has now created this exact hazard on two of two real frames*. Each
proof-of-concept handled it by dropping the key before inference, as a recorded decision.
The fix belongs in the toolkit.

The same frame used `age` as a raw numeric feature, and imputed missing values, so an
imputed age looks the same as a real one downstream. Age is a protected characteristic in
most credit and fraud jurisdictions. The rule applied was **record, don't silently
reproduce and don't silently drop**: keep it to match the reference implementation, and
surface it in the summary and report as a fairness note.

The ML parity research gave the reason a leakage review dimension gets priority over
building a library: these failures are silent, and a leaked feature returns AUC 0.97 and
reads as success.


## A missingness-only leak is invisible to a notna-masked alarm (galactus, 2026-08)

A per-column AUC leak alarm masked each column to `notna()` and skipped single-class
columns. It never scored missingness itself. A column populated **only** for charged-off
borrowers (the settlement/hardship shape the frame code itself documented) was skipped
unscored, although its presence alone is the label. Fix: also score
`series.notna().astype(int)`. Exercise the alarm with a planted-leak synthetic twin (see
[[ML Run Reproducibility Bar]]).

## See Also
- [[An Unrun Scan Is Not a Clean Scan]] — extends (the missing scan as a finding)
- [[Profile Then Select]] — extends ("did not exist yet at prediction time" as a leakage candidate)
- [[ML Frame Sourcing — License, Horizon, Prevalence]] — prerequisite-for (a time column for a temporal split)
- [[Prototype Genesis Interview]] — part-of
- [[Calibrated Score, Deterministic Decision Rule]] — prerequisite-for (leakage check before the training library)
- [[ML Stage Layering with Typed Contracts]] — prerequisite-for ("nothing fitted outside a fold" as a tree rule)
- [[ML Run Reproducibility Bar]] — prerequisite-for (the planted-leak twin plants these shapes)
