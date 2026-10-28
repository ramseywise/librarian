---
title: Single-Call LLM Gate Weakness Audit
tags: [eval, pattern]
summary: "Seven recurring defect classes in a one-LLM-call publish gate: silent sanitizer repairs, self-reported approval, anchoring on the prior verdict, one verdict answering two questions, computable checks asked in prose, unbounded undelimited input, and decorative confidence. Fix order: baseline against human labels first, deterministic fixes next, and spend-backed experiments last, where a measured 'keep it as is' counts as a finished outcome."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-21-dis357-qc-baseline-fixes.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-21-dis357-qc-baseline-fixes.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-21-dis357-qc-baseline-fixes.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-21-dis357-qc-baseline-fixes.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-21-dis357-qc-baseline-fixes.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-21-dis357-qc-baseline-fixes.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-21-dis357-qc-baseline-fixes.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-21-dis357-qc-baseline-fixes.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-21-dis357-qc-baseline-fixes.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-21-dis357-qc-baseline-fixes.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-21-qc-eval-loop.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-21-qc-eval-loop.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-21-qc-eval-loop.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-21-qc-eval-loop.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-21-qc-eval-loop.md
---

# Single-Call LLM Gate Weakness Audit

From an akira QC stage: one LLM call per event whose verdict gates publish (only
`auto_accepted` passes). It had never been scored against a human label. A code read, with
no measurement yet, found seven weaknesses. None of them could be prioritised, because
nothing could say whether the false-accept rate was 1% or 20%.

## The seven classes

| # | Class | Fix |
|---|---|---|
| W1 | **Silent repair.** The sanitizer swaps out-of-vocabulary values for fallbacks and drops array items, and the downstream gate never learns that a repair happened. | Surface `sanitizer_repaired_values` as a *non-blocking* gate reason until the repair-count distribution is seen. |
| W2 | **Self-reported approval.** Auto-approve rests on two fields the model reports about its own output. | Cross-check against a deterministic evidence score (`completeness_overclaimed` when the model says `high` and the evidence says `low`). |
| W3 | **Anchoring on the prior verdict.** The QC input carries the upstream gate's status and confidence. | An ablation (`--strip-prior`), both arms on the same sample, decides it. |
| W4 | **One verdict, two questions.** A 4-way status answers both "is this a single event?" and "is the enrichment plausible?" | Two stored booleans in the existing jsonb, so no migration. The 4-way status stays the only gate input for now. An offline benchmark already asked them separately, which confirmed the shape. |
| W5 | **Computable checks asked in prose.** The model is asked whether the URL is event-specific, the date plausible, the city right. | A deterministic precheck skips the model call on a clear reject and writes its own sentinel model id. |
| W6 | **Unbounded, undelimited raw input.** | Bound and delimit `raw_data` in the prompt. |
| W7 | **Decorative confidence.** Stored and shown, but it gates nothing. | Build a calibration table from already-collected values. If it is informative, gate on it. If it is flat, drop it from the prompt. Drop is the default. See [[Confidence That Is Not a Probability]]. |

## Fix order

1. **Baseline first.** Compute a confusion matrix and a false-accept rate with N, model and
   prompt hash recorded, before any logic change, following [[Small-N Reporting Floor]].
2. **Deterministic fixes** (W1, W2, W4, W5, W6): pure functions, tests written RED first,
   no spend.
3. **Spend-backed experiments** (W3, W7), run by the operator. The decision rule is written
   in advance: ship the strip only if false-accept does not get worse *and* verdicts
   measurably stop mirroring the prior status. Otherwise **decline explicitly**. "Measured,
   no improvement, keeping the fields" is a valid finished outcome, not a failure to finish.
4. **Re-baseline** with the exact Phase-1 CLI, then decide whether the metric gets a
   threshold. The default is no.

Decision rows are written into the registry only when their numbers exist, not
speculatively. The one with no numeric dependency (W1) can be ratified as soon as the
deterministic fixes land.

## Version bumps that do not stale anything

Bumping `QC_VERSION` or `REVIEW_GATE_VERSION` looks like it would invalidate stored
verdicts. It does not, because staleness was keyed on the enrichment id, not the version
string. Old rows keep their old version string forever, and production holds mixed
versions side by side. The PR has to say this out loud. Bump each constant **once**, in
the commit that changes the stored output *shape*. Changing the prompt's input shape, or
adding a separate precheck row, does not count.

## Review finding: a constant-true signal disarms the evidence check

The W2 evidence score returned `low` only when zero signals were present. For bars, the
signal derivation set `hasDate: true` unconditionally, because bars have no dates. So a bar
with nothing at all scored `medium`, and the `high`-vs-`low` overclaim check could never
fire for that whole vertical, with no error. The fix: a not-applicable signal is `null`,
excluded from both numerator and denominator, never `true`. This is the mirror image of
[[Always-Red Check Carries No Signal]]: a check that cannot go red for a whole slice is
just as uninformative. Add a test that the empty payload for each vertical can trip the
check.

## See Also
- [[Small-N Reporting Floor]] — prerequisite-for (the baseline step)
- [[Sanitize Never Fails, Validate Never Mutates]] — extends (W1: a repair must still be visible)
- [[Confidence That Is Not a Probability]] — related (W7)
- [[Always-Red Check Carries No Signal]] — related (inverse: never-red for a slice)
- [[Hedging Belongs in the Gate, Not the Answer]] — related
- [[Spend Gate Before the Model Call]] — related (W5 precheck short-circuits spend)
