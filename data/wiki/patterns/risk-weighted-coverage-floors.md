---
title: Risk-Weighted Coverage Floors
tags: [patterns, eval, pattern]
summary: "Enforce coverage as per-directory floors on the riskiest code, each set just below the current measurement and proven able to fail, rather than one repository-wide percentage that averages weak areas into strong ones. Write tests before thresholds, keep integration-only code report-only, and raise floors only to a stable value below each new observation."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis299-coverage-enforcement.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis299-coverage-enforcement.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis299-coverage-enforcement.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis299-coverage-enforcement.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis299-coverage-enforcement.md
---

# Risk-Weighted Coverage Floors

From an akira plan that turned a measured coverage baseline into enforcement for a
TypeScript pipeline (Vitest).

## The policy

1. **Tests before thresholds.** Close the named high-risk gaps first, then freeze what was
   earned. A threshold set before the tests only records the gap.
2. **Per-directory glob floors, no global number.** Floors were set only on the two weakest
   high-risk directories, ingestion and ops, using Vitest's glob `thresholds` map. A
   repository-wide percentage lets a well-tested UI hide a weak importer.
3. **Floor just below the current measurement.** Each floor sat about 2 points under the
   measured statements, branches, functions and lines, so normal churn passes and a real
   regression fails.
4. **Prove every floor can fail.** Raise one floor above the measurement temporarily,
   confirm the gate rejects it with the named threshold error, then revert. A threshold
   that was never seen red is not yet evidence. See [[Red-Then-Green Proof for Fix-Stage Tests]].
5. **Integration-only code stays report-only.** Database adapters are exercised mostly by
   integration tests that unit coverage does not count. They are kept out of every gated
   glob and stay visible but uncounted. Unit coverage would otherwise call them unprotected,
   or a mixed count would call them protected.
6. **Ratchet with margin, never blindly.** After new tests land, re-measure with the same
   command and config, then raise floors only to a stable value below the new observation.
   The re-measure also showed that part of the repo-wide gain came from other work merged in
   the same window. The floor credits only what this work earned.
7. **Diff coverage is deferred until there is a reliable merge base.** Changed-file
   enforcement needs a known base SHA, which CI could not provide while scheduling was
   blocked. The deferral was written down as a decision, not left implied.

The gate is a separate `make coverage-gate` target, outside the main pre-merge gate.
Out of scope: chasing 100%, loosening exclusions, browser/E2E coverage.

## What the gap tests found

- **A real defect behind the first named gap.** `atob()` on a malformed
  `Authorization: Basic` header threw unhandled and returned 500 instead of 401. The new
  test was red against the old code and green after the fix.
- **Re-measure before picking targets.** Two files the baseline flagged as worst (36% and
  48% branch coverage) had already risen to 76–78% from other work. A run-log module at 44%
  became the target instead. Picking targets from a stale baseline wastes the session.
- **Uncovered branches clustered in failure paths**: dry-run branches, read-error
  propagation, status-normalisation message sniffing (timeout, rate-limited, network), and
  partial-result merges. Behaviour tests asserted visible outcomes, not private calls.

## Rollback rule

Roll back an individual floor if it turns noisy, for example when generated files enter a
glob. Never delete the tests that revealed the gap.

## See Also
- [[Mutation Score Artifact from Zero-Test Runs]] — related (the companion trial: coverage cannot show whether assertions distinguish subtle changes)
- [[Always-Red Check Carries No Signal]] — related (a floor nobody has seen fail is the mirror case)
- [[UNGATED Metric Convention]] — related (report-only for the measurements not yet fit to gate)
- [[Red-Then-Green Proof for Fix-Stage Tests]] — instance-of (each floor and each gap test was proven red first)
