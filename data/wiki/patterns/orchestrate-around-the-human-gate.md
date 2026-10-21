---
title: Orchestrate Around the Human Gate
tags: [meta, llm, pattern]
summary: "When a loop contains a human gate that can stay open for days, the orchestrator's job is to detect the gate, halt with a printed next step, and re-derive its position from files on every re-invocation. It never dispatches the gate stage. It drives the skills it consumes through what it dispatches and what it reads, never by editing them."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-20-meta-orchestrator.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-08-20-meta-orchestrator.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-20-build-orchestrator.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-08-20-build-orchestrator.md
---

# Orchestrate Around the Human Gate

guacamayo runs three orchestrators: triage (backlog → READY plan), build (READY →
execute → review → fix → ship-ready), and meta (insights → feedback → retro → proposed
config changes). The meta loop is the hard one, because its middle stage, feedback
verification, is a human gate by design ("the gate is the point").

## The shape

```
insights   (automatic, dispatched to a sub-agent)
   ↓
FEEDBACK   orchestrator finds verified-but-unconsumed findings, or no feedback run
           at all, and HALTS: prints what to run, exits
   ↓       (a human runs the gate in a separate session, with no time bound)
   ↓       (the human re-invokes the orchestrator whenever they like)
retro      (automatic, propose-only)
   ↓
config diffs proposed in the retro report; a human reviews, applies, commits
```

The orchestrator never substitutes judgment for the gate. Its value is sequencing,
state detection and telemetry, not removing a decision point. The build orchestrator
works the same way. A `merge_impact: blocker` finding stops the loop and escalates. The
fix sub-agent only touches non-blocking findings. After three review rounds the loop
escalates rather than continuing.

## Resumability is the central design problem

Build's review rounds finish in one sitting. The feedback gate can stay open for a week.
A naive re-run while it is open either re-runs insights pointlessly, producing a
duplicate dated section, or misses that feedback already ran and exits as a no-op when
retro is actually ready to fire. So:

- **Every invocation re-derives its position from real files**: the feedback log, the
  insights log, the ledger, the action log and a cascade-state flag file. It never relies
  on memory of the last run (see [[Re-Derive, Never Re-Read]]).
- **Due conditions come from signals that already exist** (the cron's due flags, plus
  "feedback is newer than retro's last consumption"). The orchestrator does not invent
  new thresholds.
- **Every decision is logged, including no-op and gate-halt outcomes**, with the
  classifier's input dates in each row. A misclassification can then be diagnosed after
  the fact even if nothing caught it beforehand.
- **A standing tripwire test** asserts that a gate-halt outcome never dispatches a stage.
  The skill's tool allowlist also has no path that could run the gate skill unattended.

### The resumability bug refinement caught

The draft read "latest entry" with `grep -m1` / `tail -1`. Both logs it read were out of
chronological file order in the live repo: one was self-annotated "newest-first order
broken here", and the other had round R12 before R11. The draft's own worked example
picked the wrong retro round, and it skipped a flag check that its own state table
checked first. The fix was to extract (date, label) pairs, sort by **date**, and take
the max. Sorting by round number was ruled out too, because it only happens to track
date. Schema tests would not catch this, because they validate row shape and not the
extraction. Only a manual walkthrough against live state verifies it.

## Consumed skills stay unmodified

Both orchestrators consume existing skills as they are. The build orchestrator tells its
execute-stage scout "do not auto-dispatch review", and passes `Authorization: auto-post`
to the review stage, which already had an "if authorized" branch. The dispatch prompt
*is* the authorization. The meta orchestrator reuses an existing persistence agent that
already ran exactly its two automatable stages, instead of adding a new scout with
duplicate constraints. As a result rollback is purely additive: delete the new skill
file.

## See Also
- [[Stage-Scoped Scout Agents]] — extends (the one-stage-per-invocation sub-agents these orchestrators dispatch)
- [[Re-Derive, Never Re-Read]] — prerequisite-for (position is re-derived from files on every run)
- [[Decision-Seat Inventory for a Control Plane]] — related (most seats stay human; the orchestrator sequences around them)
- [[Due-vs-Acked Trigger Counters]] — related (the due signals the orchestrator reads rather than reinvents)
- [[Append-Only Log Writer Invariants]] — related (read the current entry by maximum key, never by position)
