---
title: Hash the Frame as Fitted, Not the Source File
tags: [eval, foundations, pattern]
summary: "A run record's data identity must fingerprint the matrix the model was actually fitted on (post-derivation content hash, row/column counts, ordered column names) — a source-file hash stays identical across runs whose preprocessing diverged and certifies exactly the discrepancy it was built to catch."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-08-11-ait-run-registry.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-08-11-ait-run-registry.md
---

# Hash the Frame as Fitted, Not the Source File

A template got a small local run registry after an ML prototype hit an unanswerable
question. A re-run of the baseline scored 0.34 where the design doc had recorded 0.42,
while the random-forest score reproduced within fold noise. The prototype's own
diagnosis was that the baseline "was scored on a differently-preprocessed frame; there is
no way to check, because nothing recorded which one."

## The load-bearing finding

The modelling frame was *derived* from a CSV by a drop pipeline (45k × 151 → 39.8k × 106,
then the group and target columns dropped again before fitting). **A hash of the source
CSV would have been identical across both runs.** The divergence sat downstream of the
file, in derivation and preprocessing. A changed source file would have moved both scores,
but only one moved.

A registry that hashed the source file would pass its own tests and fail its acceptance
test. The data identity therefore records the frame **as fitted**:

- a content hash of the post-derivation matrix, order-stable and dtype-sensitive
- row and column counts
- ordered column names (names are aggregates and safe to record; rows and indices are not)

If derivation logic changes, the git SHA catches it, but only when the derivation lives in
a tracked file. A frame derived in a notebook is not covered.

## The record shape: four independent groups

| Group | Fields | Note |
|---|---|---|
| **Code state** | git SHA + dirty flag | A dirty tree makes the SHA non-reproducible. The boolean answers "is this trustworthy" but not "what changed". |
| **Data identity** | frame-as-fitted hash, counts, column names | The load-bearing group. |
| **Execution config** | seed, resolved config, fold *plan* | Record the splitter kind, `n_splits`, group/time columns and random state, which regenerate the folds deterministically. Never record per-row fold indices: they are an index per row and violate aggregates-only. |
| **Outcome** | flat `name → value` metric map + declared `headline_metric` | The headline must be a key in the map, validated at construction. This keeps the shape from assuming PR-AUC, so ML and LLM-eval runs share one record. |

## Three supporting rules

- **Distinguish not-applicable from not-recorded.** An LLM eval harness has no seed and
  no folds, because its determinism comes from a scripted adapter. If those fields are
  merely nullable, every eval run reads as "forgot to record the seed". Use an explicit
  not-applicable sentinel. The precedent for getting this wrong was in the same
  prototype: "a missing number and an uncomputed one looked identical in the report."
- **Aggregates only, enforced at write time.** A run record gets shared, and once it
  carries a row it inherits every handling constraint the dataset has. Documentation is
  not enough. A `label → proportion` class-balance map leaks if the labels are
  themselves identifiers, so its keys are validated on write. The data hash is stored as
  a digest, never a sample.
- **Borrow the vocabulary, not the dependency.** Mirror the MLflow/W&B run, params,
  metrics and artifacts shape so a later export is mechanical. Avoid the account, key, and
  network dependency in CI until a consumer needs it.

## See Also
- [[Experiment Tracking Schemas]] — extends (the run-identity contract, with data identity defined as fitted)
- [[Reproduce to Tell a Break From a Stuck Agent]] — prerequisite-for (reproduction needs a recorded code+data state)
- [[ML Frame Sourcing — License, Horizon, Prevalence]] — related (where the frames come from)
- [[REUSE/ADAPT/SKIP Asset Verdicts]] — related (the research pass that reused the existing headline() precedent)
