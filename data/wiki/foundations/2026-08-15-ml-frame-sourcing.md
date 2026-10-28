---
title: ML Frame Sourcing — License, Horizon, Prevalence
tags: [foundations, decision, conflict]
summary: Choosing public datasets for ML prototype frames on three constraints — a license that permits redistribution of derived artifacts, a time column that supports a temporal split, and a positive rate low enough to exercise the sufficiency guard — with the explicit note that class imbalance is not data insufficiency and that pre-registered hypotheses stay unedited after results.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/docs/DESIGN-ml-frame-sourcing.md
  - data/raw/claude-docs/galactus/docs/decisions/ml-frame-sourcing-decisions.md
  - data/raw/claude-docs/galactus/docs/research/2026-08-15_ml-parity_credit.md
  - data/raw/claude-docs/galactus/docs/research/2026-08-15_ml-parity_fraud.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-18-ml-frame-sourcing.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-18-ml-frame-sourcing.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-18-ml-parity-consolidated.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-18-ml-parity-consolidated.md
---

# ML Frame Sourcing — License, Horizon, Prevalence

**Status:** Accepted 2026-08-15. **Context:** a prototyping repo needed public frames for
two ML tracks (credit default, card fraud) that could be committed, re-run and reviewed
without a private data path.

## Three constraints, in order

1. **License permits redistribution of derived artifacts.** Not just "free to download" —
   the frame manifest, aggregates and run records are committed, so the licence must cover
   derived works. A CC BY 4.0 credit-default dataset passed; a Kaggle fraud set required
   checking the specific dataset's terms rather than the platform's.
2. **A time column supporting a temporal split.** A frame with no horizon forces a random
   split, which for anything with drift is a leakage candidate. The fraud set's `Time`
   column (seconds since first transaction) is enough; the credit set has none, which is
   recorded as a limitation rather than papered over.
3. **Positive prevalence low enough to exercise the sufficiency guard.** The fraud set's
   0.172% positive rate was chosen *because* it is extreme — it is the fixture that proves
   [[Data Sufficiency Refusal]] fires.

## Imbalance is not insufficiency

Two different questions were being conflated in early drafts: *are there enough positives
per fold to estimate a metric?* (sufficiency — a count) and *is the positive class rare?*
(imbalance — a ratio). A 0.17% rate over 284k rows still yields ~98 positives per fold
and clears a `MIN_POSITIVES_PER_FOLD = 10` floor; the guard is about the count, and the
decision says so to stop the two being merged again.

## Pre-registration is left unedited

The design doc's hypotheses section was written before any run and **is not edited after
results come in**; outcomes go in the run record and the research notes. The credit track's
anti-finding — fold-to-fold variance dwarfed the difference between candidate models —
stayed a finding *because* the pre-registered claim it refuted was still there to refute.

## Also recorded

- **Reversibility class** per decision (dataset swap: reversible, one manifest edit;
  committed aggregates: reversible but leaves history).
- **What was not asked, and why** — a required section; a decision doc that lists only
  what it chose hides the search space.
- **Provenance from an unversioned private path** is flagged as a parity gap: a frame whose
  origin cannot be re-fetched is reproducible only on one machine.
- The spec the design should have been checked against did not exist yet; the gap is
  named in the decision rather than assumed away.

## Verification pass (2026-08-18)

A research pass checked both frames against the three constraints by downloading the files
and reading the licences. **Conflict flagged.** It reads "horizon" as the *label* horizon,
not as a time column, and on that reading it reverses this page's constraint-2 verdicts. See
`_conflicts.md` and [[Label Horizon vs Sampling Window]].

- **Credit frame: confirmed on every claim.** CC BY 4.0. Prevalence counted at 22.12%
  (6,636/30,000). The thinnest 5-fold test fold has about 1,327 positives against a floor of
  10. The horizon is source-stated ("default payment next month") in the curated variables
  table, not in the prose.
- **Fraud frame: no stated label horizon, licence unverified.** The `Time` column fixes a
  two-day *sampling* window. The labeling window is unstated, and the source declines to give
  background. The ODbL badge renders client-side and could not be confirmed without auth.
  ODbL vs DbCL is exactly the distinction that changes the redistribution analysis. The plan
  went ahead for credit only. Fraud was left to an operator decision: narrow the claim or
  hold the standard.
- **ODbL share-alike does not reach a metrics report.** A metrics summary, AUC, PR curves,
  threshold sweeps or coefficients are a *Produced Work* (§4.5(b)) and need only an
  attribution notice. The CSV, a resampled or split copy, a feature-engineered row-level
  table, or per-row predictions joined to source rows are a *Derivative Database* and carry
  share-alike. Purely internal use in a private repo triggers neither. Bound the summary spec
  so outputs never get fine-grained enough to reconstruct rows.
- **Undocumented codes are kept as distinct levels.** About 58% of repayment-status values
  are `-2` or `0`, codes the source never defines (the documented scale starts at `-1`).
  Education and marriage fields also have off-scale values. Remapping them would assert a
  meaning the source does not state, so each is kept as its own level and recorded as a
  decision. Other traps found: there is no `PAY_1` column, 35 rows are duplicates, and the
  CSV header is cryptic `X1..X23`.
- **Automated provenance comes back empty.** The dataset API's `license` and `dataset_doi`
  fields are both `null`. Those are the two fields the design most wanted, and they appear
  only in page HTML.
- **Name the baseline before computing.** The credit PR-AUC prevalence floor is 0.2212 and
  majority-class accuracy is 77.88%. Read any model against 0.2212, not 0.5.
- **Even a confirmed horizon leaves the threshold open.** The cost ratio is still not given,
  so no threshold is reported. Borrowing a sibling run's stipulated 4:1 would be a guess
  presented as a decision.
- **The leakage list was written fresh**, not ported. The new schema shares no column names
  with the sibling run, so porting would only rename columns. The list came out empty and
  argued; see [[Argued Empty List]].

## See Also
- [[Label Horizon vs Sampling Window]] — extends (the 2026-08-18 verification and its conflict)
- [[Argued Empty List]] — extends (the credit leakage list)
- [[Data Sufficiency Refusal]] — prerequisite-for
- [[Deferred Decision Status]] — extends ("not asked and why" is a deferral register)
- [[Profile Then Select]] — extends (frame-level choice precedes column-level profiling)
- [[Experiment Tracking Schemas]] — extends (what the run record must carry for the frame to be reproducible)
