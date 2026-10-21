---
title: Data Sufficiency Refusal
tags: [foundations, eval, pattern]
summary: A pure, never-raising guard reads the minimum positives in any CV fold against a stated floor and, when it fails, withholds the cost-sensitive metrics entirely — a run that refuses to answer is distinguishable from a run that failed and from a run that scored badly, and exits 0 because refusing was the correct output.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/docs/research/2026-08-15_ml-parity_fraud.md
  - data/raw/claude-docs/galactus/docs/research/2026-08-15_ml-parity_segmentation.md
  - data/raw/claude-docs/galactus/docs/research/2026-08-15_ml-parity_credit.md
  - data/raw/claude-docs/galactus/docs/DESIGN-ml-frame-sourcing.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-11-gal-4-phase2-ml-fraud-poc.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-11-gal-4-phase2-ml-fraud-poc.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-14-gal-17-customer-segmentation.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-14-gal-17-customer-segmentation.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-16-segmentation-parity.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-16-segmentation-parity.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-18-ml-parity-consolidated.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-18-ml-parity-consolidated.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-15-lending-parity.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-15-lending-parity.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-16-fraud-parity.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-16-fraud-parity.md
---

# Data Sufficiency Refusal

The fraud prototype's headline is "a refusal, not a metric." Its `sufficiency.py` decides,
before any cost figure is printed, whether the data can support the question being asked.

## Mechanism

- **Pure and never-raising.** The guard takes fold statistics and returns a verdict object;
  it does not touch I/O and does not throw. Raising would make "insufficient" look like a
  crash, which is the opposite of the intent.
- **Reads the minimum fold, not the mean.** `MIN_POSITIVES_PER_FOLD = 10`. A mean of 98
  positives per fold hides a fold with 3; the metric computed on that fold is noise, and a
  mean over folds would launder it.
- **Refusal by withholding.** When the guard fails, cost-sensitive outputs (expected cost
  at threshold, savings vs baseline) are *not computed*. The report says why. *"Not asking
  the question"* is a cleaner signal than asking it and appending a caveat nobody reads.
- **`ReportAnchorError` raises** when a report template's anchor is missing — the one
  place the code *does* raise, because a silently skipped section would be exactly the
  collapse the guard exists to prevent ([[Collapse Site Detection]]).
- **`before-guard.json` is saved** with the un-gated numbers so the refusal cannot later be
  called a strawman: anyone can see what the metric *would* have read.

## Refuse-not-abort: exit 0

The fraud run exits 0 on refusal. The credit track, built earlier, aborts non-zero on its
own guard. The research records this as a **decision divergence, not a bug**: for fraud,
"insufficient positives" is a legitimate result of the pipeline and the orchestrator should
continue (the run record carries `verdict: refused`); for credit, the guard protects a
downstream step that cannot proceed. Both are defensible; what matters is that each repo
states which it chose. A run that refuses is not a run that failed.

**Ratified split (2026-08-16):** the parity bar now allows both modes and assigns them by
the *kind* of verdict. **Leakage-class violations abort** with a non-zero exit (exit 2).
**Structure verdicts refuse** and exit 0. The difference is epistemic, not stylistic. "A
column restated the answer" means the matrix is not fit to score and there is nothing honest
to report. "No k beat the baselines" *is* the report. The split runs through a single run:
the segmentation prototype sent its four leakage rules and its weak-structure clause through
one `exit 0` path, **which made a leak look like a finding**. The exit gate adds a test that
a planted leak exits 2.

Three related findings:

- **A rule that cannot fail is not a guard.** One of the four leakage rules was a constant
  `True`. It asserted a contract instead of checking it, and its failing/clean twin tests
  could not have exercised it both ways. See [[Argued Empty List]].
- **Test the guard's contract, not the frame's current shape.** A synthetic fixture tuned to
  the stand-in frame's 800 rows and 14 positives, then asserted to refuse, keeps passing
  after a frame swap even though the real run no longer refuses. The oracle should assert
  "positives per fold < floor ⇒ refuse".
- **A refusal-shaped plan dies with its frame.** A plan built around recording a refusal
  hard-coded the refusal's measured values. Once a larger frame was chosen, the guard passed
  and the plan's premise was gone ([[Label Horizon vs Sampling Window]]).

## Honest signatures of missing pieces

The same research reads *absences* as evidence: three `pytest` skips were "the honest
signature of a missing `--dry-run`" — tests written against a flag the script does not yet
have, left skipping rather than deleted, so the gap stays visible in the test report.

## Unsupervised analogue

The segmentation prototype has no positives to count, but the same principle applies as a
weak-structure clause: `k=4` with silhouette 0.25 is reported as *weak structure*, and the
run record should carry the internal-validity index as what it is rather than borrowing a
supervised record's `metric` slot — a supervised-shaped record would make a
`NotApplicable` look like a pass. (The registry's typed `NotApplicable` blocks the
omission but not a false reason; see [[A Sentinel Catches Forgetting, Not Asserting]].) Baseline and candidate scores are computed in the same
call so neither can drift from the other. See [[HDBSCAN with KMeans Fallback]] for the
all-noise case handled the same way.

## The measured "before" run

The fraud proof-of-concept built the guard around a photograph of the failure, not a
claim about it. On 800 rows with 14 positives (1.75%), the unguarded toolkit ran three
models with **no warning from any layer**. Every PR-AUC was within 0.003 of the 0.0175
prevalence floor, ROC-AUC was around 0.49, and each model still reported a cost-minimising
threshold with three-decimal precision that flagged one row and caught zero positives. The
run was kept word for word as an artifact and asserted against: *"a guard whose necessity
is asserted is much weaker than one whose necessity was photographed."*

Mechanisms worth knowing:

- **sklearn stays silent.** `StratifiedKFold` only warns when a class has fewer members
  than `n_splits`. 14 ≥ 5, so 2–3 positives per test fold went unflagged. A fold with 2
  positives supports exactly three recall values (0, 0.5, 1.0), much coarser than the
  four decimals the report printed.
- **The inner layer is thinner still.** Calibration cross-validates *inside* the training
  rows (`cv=3`), so each inner fold saw about 3.7 positives, and the threshold was chosen
  downstream of that. Sigmoid calibration itself held up (Brier improved 4×). The honest
  finding was "sigmoid is fine and the threshold is not". Reporting a calibration failure
  would have been wrong.
- **Fewer folds do not create evidence.** Going to 3 or 2 folds re-partitions the same 14
  events. That was recorded as a rejected mitigation, and the guard is stated per fold so
  that lowering `n_splits` to get around it is visible.
- **The floor was computed, then thrown away.** The metrics layer stored `prevalence` and
  the PR curve carried `baseline=prevalence`, but the HTML report rendered neither. At a
  0.2056 floor (an earlier lending frame), 0.4351 obviously reads as good. At 0.0175,
  0.0200 looks like a small number that could be anything. This was a display fix, not a
  computation fix. The report also used "baseline" for the logistic model while the
  metrics layer used it for chance, a naming collision worth removing.
- **Refuse by not asking.** The guard withholds the cost inputs, so no threshold is ever
  computed and then hidden. The guard's *expression* in the report still broke. See
  [[Tested Decision, Untested Expression]].

## See Also
- [[ML Frame Sourcing — License, Horizon, Prevalence]] — prerequisite-for (the frame chosen to exercise this guard)
- [[Collapse Site Detection]] — instance-of
- [[HDBSCAN with KMeans Fallback]] — extends (refusal shape for clustering)
- [[Scan-Floor Guard Against Silent No-Op Checks]] — alternative-to (a floor on tests collected rather than positives per fold)
- [[RAG Eval Gate Contract]] — alternative-to (gate that fails vs guard that abstains)
- [[REUSE/ADAPT/SKIP Asset Verdicts]] — extends
- [[Tested Decision, Untested Expression]] — extends (the refusal banner that silently failed to render)
- [[Calibrated Score, Deterministic Decision Rule]] — extends (the threshold the guard withholds)
- [[Clustering Validation Against Named Baselines]] — extends (full unsupervised validation method)
- [[A Sentinel Catches Forgetting, Not Asserting]] — extends (the unsupervised record's `seed` field)
- [[Argued Empty List]] — extends (empty findings list is not a pass; constant-True rule)
- [[ML Run Reproducibility Bar]] — extends (ratifies abort-vs-refuse as a taxonomy across runs)
