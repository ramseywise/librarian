---
title: Gate Pass Rate Measures Effort, Not Readiness
tags: [eval, pattern]
summary: A readiness gate whose own pass rate is high says nothing about whether its output is ready. 81% of triaged issues reached READY, but READY issues passed their first build review only 16% of the time, against 25% for untriaged ones. The discriminating number is a downstream join, not anything the gate's own ledger records.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/playground/skills/workflow-triage/SKILL.md
  - data/raw/claude-docs/playground/skills/workflow-build/SKILL.md
---

# Gate Pass Rate Measures Effort, Not Readiness

## The measurement

An agentic triage pipeline (research, then plan, then refine) promoted issues to READY
before build. Its own ledger looked healthy:

- **81%** of triaged items reached READY.
- `retries` read 0 in 134 of 135 rows.

Joining the triage ledger to the build ledger on `issue` told a different story. Issues
that arrived at build as READY were approved on **round 1 only 16% of the time**. The
handful that skipped triage entirely ran at **25%**. The control group is small, but the
direction is that READY was not buying first-pass quality.

> A gate whose pass rate is 81% and whose output approves on the first try 16% of the time
> is measuring effort, not readiness.

## Why the gate's own fields cannot see it

Every field inside the gate's ledger records what the gate *did*: stages run, retries,
time to ready. None records whether the artifact *held up*. The only signal that separates
a good triage run from a fast one is downstream: does the plan survive its first review?
That number lives in another ledger and exists only as a join.

## Feeding the downstream signal back

Two fields close the loop:

- **`reopened_from`** marks an issue re-entering triage because build rejected its plan
  (`PLAN_INVALID`). It was non-null in **2 of 88** rows, while refine reported filling or
  leaving gaps on **72%** of plans. The rework was real, and the field was starved because
  build had no outcome that meant "the plan was wrong" (see
  [[Plan-Insufficient Is Not Blocked]]).
- **`scope_delta`** (`unchanged` / `widened` / `narrowed` / `split` / `absorbed` /
  `premise_false`). Re-scoping is triage's highest-value output, and it lived only in
  free-text notes. Scope found at triage is cheap; found at review it costs a fix round;
  found after merge it is an incident. A *falling* scope-change rate is ambiguous: either
  the issues got better, or triage stopped looking.

## The general rule

For any gate, ask what downstream event would show that its PASS was wrong. Then record
the join key that connects the two ledgers. A pass rate measured only inside the gate
rewards the gate for being permissive.

## See Also
- [[Workflow Pipeline Telemetry Audit]] — extends (the audit that found the ledgers did not join; this is the join)
- [[Plan-Insufficient Is Not Blocked]] — prerequisite-for (the build outcome that feeds `reopened_from`)
- [[Loop Detection and the Two-Retry Rule]] — related (why the retry counter carried no signal)
- [[Validated Concept vs Unmeasured System]] — related (a number reported without what produced it)
- [[Count the Violation, Not the Token]] — instance-of (a `scope_delta: premise_false` case)
