---
title: Audit-Don't-Assert Release Checklist
tags: [eval, pattern]
summary: "A per-stage release checklist whose every item names an artifact and a verifier, takes the value true, false or error, stays false when it cannot be verified, and starts with rows written from failures the repo has already produced. Error and failed-gate route differently, so the schema must be able to tell them apart."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/docs/plans/2026-08-15-fast-loop-borrowables.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-15-fast-loop-borrowables.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-15-gal-27-band-contract-hitl-gates.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-15-gal-27-band-contract-hitl-gates.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-15-gal-23-proto-pipeline-dry-run.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-15-gal-23-proto-pipeline-dry-run.md
---

# Audit-Don't-Assert Release Checklist

From the galactus "fast loop" design: a ~60-minute prototyping pipeline split into four
time-boxed bands (triage, prototype, optimize, harden), each of which must pass a release
checklist before the next band starts. The research ranked one borrowed rule as the
single most valuable change. It costs one paragraph, and it guards against the failure
most likely to grow under time pressure:

> **Audit, don't assert.** Every item is the result of looking at a real artifact this
> run. If an item cannot be verified, it stays `false`. It is never marked true on memory
> or intent.

Speed pressure is exactly when a check gets marked green on intent. The repo had already
produced two live cases of this, and both were found by *reading* artifacts, without
running anything (see "Seed rows" below).

## Item shape

`id | expectation | verifier (file path or command) | value`

The *shape* comes from a template's gate tables: booleans checked against artifacts, each
with a named verifier. The *rows* were not copied, because they were tied to machinery the
template owns. Copy the shape and write your own rows.

### Three values, not two

The first draft used `true | false`, plus a prose rule that errors and failed gates must
route differently. A failure-pass reviewer pointed out that this rule **cannot be
enforced given its own schema**: both values are gate outcomes, so there is nowhere to
record "the verifier itself could not run." An instruction contradicted by the schema one
line above it sits at the weakest layer of the enforcement ladder
(`hook > linter > test > tool schema > instruction`). The fix:

| Value | Means | Routes to |
|---|---|---|
| `true` | verifier ran, expectation held | proceed |
| `false` | verifier ran, expectation did not hold (or could not be confirmed) | **back one band** |
| `error` | verifier could not run: missing file, failed import, moved path | **stop for repair**, never route back |

An unreadable or missing artifact is an **error, not a failed gate**. The existing
readiness gate already drew that line ("an unreadable or empty target is an error, not a
failed gate"). The checklist had to carry it into its value domain, not just its prose.

## Seed rows from documented failures

Write the first rows from failures the repo has already shown, so the checklist has teeth
on day one. Then **verify the checklist against a known-bad artifact**. A checklist that
passes a run you know is bad is assertion theater.

- **A nested field read flat.** A run summary nested `operating_point_reported` under a
  `refusal` object. A check keyed on the flat name reads `None`, which is falsy, and that
  is identical to "no refusal reported". The finding is inverted inside the very check
  meant to catch it.
- **A component silently absent from a verdict.** `"skipped": {"catboost": ...}`: one
  model failed to fit, and `beats_baseline: false` was computed over the models that
  survived. Nothing gated on `skipped` being non-empty. The checklist item fails when
  `skipped` is non-empty.

### Two traps found while writing those rows

- **A criterion that demands the wrong value inverts the item.** The first draft's verify
  step required the nested field to be `True`. Run against the real artifact, it was
  `False`, and `False` was the correct reading, because the artifact genuinely reports no
  operating point. An executor chasing the stated criterion would have kept "fixing"
  things until the checklist passed on a known-bad artifact. The item was restated to
  separate *absent* (`None`, read flat) from *a real `False`* (read nested).
- **A declared cap creates a blind spot in the skip check.** When a run caps its candidate
  set, a model excluded by the cap was never scheduled, so it never shows up in `skipped`.
  The skip item catches failures mid-run but not exclusions that were never scheduled. It
  was widened to also fail on "candidate set was capped", and the cap became a first-class
  field in the run artifact.

## The consumer-side twin: stage-gated inertness

The same research named a companion mechanism. **An artifact is not readable until the
gate that owns it says so.** A later stage that reads an earlier stage's output must not
consume half-written work. In a template's design file, nothing is read until the gate
marks its stage complete. The research found that a status contract other processes can
read (producer side) and gate-blessed inertness (consumer side) are one decision seen from
two ends.

## See Also
- [[A Check Must Say Why It Could Not Check]] — extends (the same UNCHECKED-vs-FAILED split, encoded in a checklist schema)
- [[Silence Reads as Clean]] — prerequisite-for
- [[Vacuous Check Turns Backwards on Policy Change]] — extends (the flat-key read is a check that passes by reading nothing)
- [[Size the Gate to the Blast Radius]] — extends (the readiness gate's Light/Full cost ladder this sits beside)
- [[Hoist Irreversible Decisions to the Attended Band]] — extends (the bands these checklists gate)
- [[HITL Gradient]] — prerequisite-for
