---
title: Unit Tests Encode the Checker's Assumption
tags: [patterns, eval, pattern]
summary: "A checker's unit tests are written by the same mind with the same model of the input, so they pass on a checker that is 100% wrong (65 findings, 0 true positives, 20/20 green); only a live-corpus spot-check, a test that pins a known defect and is later inverted, or a mutation of the real enforcement proves the checker sees the world."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-12-wake-consistency-check.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-14-gua-109-occurrence-date.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-14-gua-111-review-field-discrimination.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-15-gua-118-install-the-clock.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-19-telemetry-truth-pass.md
---

# Unit Tests Encode the Checker's Assumption

Finding from guacamayo's consistency-check and telemetry work (2026-08). The fixtures for a
checker's unit tests are built from the author's mental model of the input, which is the
same model the checker was built from. If that model is wrong, the checker is wrong and
the tests still pass.

## The instance

A stale-path checker scanned issue bodies for file paths that no longer exist. It produced
**65 findings with 0 true positives**, while **all 20 unit tests were green**. The wrong
assumption was that any path mentioned in an issue is an assertion that the path exists.
In practice a mentioned path takes one of three shapes:

1. It asserts the path exists. This is the only checkable shape.
2. It reports the path as missing, which is the bug being filed.
3. It proposes creating the path, which is the plan.

Every fixture used shape 1, so the tests agreed with the checker. Only a spot-check
against the live corpus found the problem.

Two more costs followed. **A table that is 100% noise teaches the reader to skip it**,
including the real rows that share it, so a noisy checker hides other checkers' output.
In the same run, the issue-join regex matched only one reference syntax. The documents
that followed the newer convention were exactly the ones that joined to nothing, and the
`unmatchable` count looked normal (see [[Control Plane Owns the Join, Not the Truth]]).

## Probes that do see the world

- **A live-corpus spot-check before trusting any count.** Hand-label a sample of real
  findings. One look at the precision is worth more than the whole green suite.
- **Pin the defect, then invert.** While a defect is known and unfixed, write a test that
  *asserts* it, and say in the docstring when to delete it. Example: a test asserting that
  the corpus dates are run dates, not occurrence dates. Once the fix lands, replace it with
  the opposite property: no single day above 50% of rows, and at least 6 ISO weeks
  covered. Then a future bulk sweep that re-concentrates the corpus fails loudly (see
  [[Trend on Occurrence Date, Not Run Date]]).
- **Prove negative tests by mutating the enforcement.** Break the real hook and confirm the
  test goes red. A negative test that cannot fail proves nothing.
- **Sweep the corpus by invoking the real hook,** not a re-implementation. One sweep
  rejected 36 of 161 docs, against an estimate that was off by an order of magnitude.
- **Test the installed artifact, not the proposal copy.** A verdict-gate test still pointed
  at the `proposed/` copy of a hook after the hook had been installed globally, so it
  tested a file nothing executes.
- **Add a stopped-job negative test for anything scheduled.** Stop the job and assert that
  the dashboard goes stale. Otherwise "the clock is installed and lying" is
  indistinguishable from a healthy clock.
- **Run positive controls for absence checks.** Before trusting "grep found nothing", grep
  for something known to be present.

## Rule of thumb

A checker is unverified until it has produced at least one hand-confirmed true positive on
real data and gone red under at least one deliberate mutation. Green unit tests are
necessary, but they only show that the code matches the author's model.

## See Also
- [[Build the Checker Before the Generator]] — extends
- [[Silence Reads as Clean]] — extends
- [[Re-Derive, Never Re-Read]] — extends
- [[Control Plane Owns the Join, Not the Truth]] — extends
- [[Telemetry Claim Verification Gate]] — extends
