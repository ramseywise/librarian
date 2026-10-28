---
title: Every Registration Site Needs a Guard
tags: [patterns, eval, pattern]
summary: When adding one member to a closed set (a review dimension, a reporter, an enum) must be mirrored in N places, a test that cross-checks two of them gives false confidence for the rest — enumerate every registration site, guard each one, mutation-test each guard, and assert completeness where the set is consumed.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/docs/plans/2026-08-09-prototyping-review-subsystem.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-09-prototyping-review-subsystem.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-10-ml-capability-parity.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-10-ml-capability-parity.md
---

# Every Registration Site Needs a Guard

The galactus review subsystem has a closed set of review dimensions. Adding one is not a
single edit. The dimension had to appear in **five places**: the `Reporter` enum, the
`REPORTER_ID_PREFIX` map, the skill tree (`review-*/SKILL.md` with a `prefix:` key), the
orchestrator's dispatch table, and the orchestrator's per-run accounting table. Prose
references (`finding-schema.md`'s prefix table and `reporter:` enum) made the count
higher still.

There was one arbiter test, `test_prefix_map.py`. It read the enum and the skill tree, and
nothing else.

## How it failed, twice

1. An eleventh dimension (`performance`) was registered in the enum, in always-on signal
   selection, and in the skill tree. The test went green. The orchestrator skill still
   said "ten dimensions", left `performance` out of its dispatch table, and the schema
   reference left it out of the prefix table. **The orchestrator would never have
   dispatched a dimension the tests considered registered.**
2. The commit that fixed the first miss also left `leakage` out of the accounting table,
   under a bolded line reading "all eleven dimensions get a row, every run — no
   exceptions", and left both new dimensions out of the schema's `reporter:` enum. A
   `performance` dispatch that read its own contract found no valid value for itself.

A mutation in a throwaway worktree proved the gap: deleting `performance` from both
orchestrator tables left the suite at 86 passed, unchanged.

The detail worth keeping is that `finding-schema.md` **claimed** `test_prefix_map.py`
guarded it. No test read that file. The claim is plausibly *why* the row went missing,
because nobody re-checks a file they believe a test already covers. A false "this is
guarded" note is worse than no note.

## The fix pattern

- **List every site first.** Write down every place the set is mirrored, including docs an
  agent reads as its contract (dispatch tables, schema references). Count the sites, then
  count the guards.
- **One guard per site.** The fix added `test_doc_registry.py` with one test per uncovered
  site (dispatch table, accounting table, schema prefix table, schema reporter enum).
- **Mutation-test every guard.** Each guard was proved by deleting one entry and watching
  that specific test go red. A guard you have not seen fail is an assumption (see
  [[Red-Then-Green Proof for Fix-Stage Tests]]).
- **Assert completeness where the set is consumed.** `active_dimensions` now binds its
  always-on list to `REPORTER_ID_PREFIX` when it returns, and raises if a registered
  member lands in neither `active` nor `skipped`. That was the one failure the
  active/skipped split existed to prevent, and nothing had enforced it.
- **Exclude by declared property, not by name.** A cross-cutting skill (`review-defense`)
  matched the `review-*` glob and turned the prefix test red. The fix excluded skills that
  declare a `job:` key, so future cross-band skills are excluded automatically, instead of
  hardcoding one more name into an exception list.
- **Pin counts in assertions, not in names.** `test_all_eleven_dimensions_accounted_for`
  asserted against `REPORTER_ID_PREFIX` itself, so it passed for any N. The "eleven" in
  the name was never checked.

## Registered is not dispatched

The ML parity plan added a `leakage` dimension that runs only when ML code changes,
rather than on every diff. Its definition of done needed **three** separate claims:
*registered* (enum, prefix map, both mirrored tables), *activates* (dispatched on an ML
changed-file list, and recorded as skipped with a reason on a prose-only one), and
*detects* (flags a planted leak, not just errors on empty input). Registration alone
proves only that the name exists. A dimension that never activates, recorded as
"skipped" with a plausible reason, looks like a deliberate choice rather than a gap.

## See Also
- [[Stated Seams Drift, Enforced Seams Hold]] — extends (the prose site that claimed a guard it did not have)
- [[Parallel Dimension Scanner Architecture]] — instance-of (the dimension registry this happened in)
- [[Scan-Floor Guard Against Silent No-Op Checks]] — extends (a check with a blind spot)
- [[Red-Then-Green Proof for Fix-Stage Tests]] — prerequisite-for (mutation-proving each guard)
- [[An Unrun Scan Is Not a Clean Scan]] — extends (registered-but-never-dispatched)
- [[Derive the Gate, Don't Copy It]] — alternative-to (generate the mirrored list instead of guarding copies)
- [[Config Reference Rot]] — extends (the reverse direction: source additions the mirrored list never heard of)
- [[Default-Deny Guard With a Named Allowlist]] — extends (tree scan plus named opt-outs instead of a hardcoded list)
