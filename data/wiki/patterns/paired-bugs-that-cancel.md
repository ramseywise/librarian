---
title: Paired Bugs That Cancel
tags: [eval, llm, pattern]
summary: "Two defects can hide each other so that counts look right: a dedup step keyed on a non-unique id silently dropped distinct findings, and the same dict absorbed duplicates re-added by a repair pass. Fixing either alone exposes the other, so they ship together, with a conservation test (N in → N out unless genuinely duplicate) that neither bug could pass."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/reviews/GUA-60-review.md
  - data/raw/repos/guacamayo/.claude--docs--reviews--GUA-60-review.md
---

# Paired Bugs That Cancel

From the review of guacamayo's deterministic review driver (GUA-60). The driver's core
promise was "no finding reaches a report unvalidated". The review found it was losing
valid findings before they were ever rendered.

## The pair

- **Blocker: dedup keyed on `id`.** `by_id = {f.id: f for f in findings}` silently
  discarded one of any two *different* findings that shared an id. This was not
  hypothetical. Each review dimension numbers its findings from `001`, and the repair
  round-trip re-scans the same files in a fresh session and **renumbers from `CR-001`**.
  So a repaired dimension routinely collides with its own first-pass ids. Nothing
  enforced global id uniqueness. Executed repro: two findings with the same id, different
  files and different titles, went in as 2 and came out as 1. The lost finding was gone
  from the report, the sweep record and the trend diff.
- **Important: the repair pass re-adds valid findings.** On a validation error, the
  repair block re-validated its *full* re-scan and appended to the same list without
  clearing it. Findings valid in both passes were added twice.

**The two bugs cancel.** The id-keyed dict absorbed the duplicates, so finding counts
looked correct. The reviewer verified this: with distinct ids the count was right. Fix
the dedup alone and every repaired dimension starts showing duplicates. Fix the repair
alone and silent loss continues. They must land in one change: cluster over list
indices instead of a dict, and collect the repair results into a fresh list.

## The missing test

266 tests passed and ruff was clean. No test asserted **conservation**: N findings in
yield N findings out unless there is a genuine semantic duplicate. That one invariant
would have failed for both bugs at once. Tests of each stage's behaviour passed because
each stage did what its author meant. The defect lived in the composition.

## Related review observations

- The plan's own end-to-end verification step had no evidence. The review artefacts
  directory is gitignored, so absence did not prove it was skipped, but there was no
  positive evidence either. A blocker surviving to merge-ready suggested a live run never
  exercised the dedup path.
- The review deliberately did **not** run the driver on itself. Reviewing a
  finding-loss bug with the tool that loses findings would be circular.
- Cluster representative ties were broken by list order, which depended on
  `asyncio.gather` completion order. That raised the question of whether fingerprints
  and trend diffs are reproducible across runs.

## See Also
- [[Fixing an Accidentally Load-Bearing Bug]] — related (a defect another path silently depended on)
- [[Conservation Gate on Accumulator Clear]] — extends (the same in/out conservation law, enforced as a hook)
- [[Deterministic Review Substrate]] — instance-of (defects in the deterministic layer itself)
- [[Cross-Sweep Finding Fingerprint]] — related (finding identity across runs; why id uniqueness matters)
