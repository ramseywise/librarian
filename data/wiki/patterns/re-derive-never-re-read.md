---
title: Re-Derive, Never Re-Read
tags: [eval, meta, pattern]
summary: A status field, ledger row or issue body that says "met" is a claim, not evidence — verify by running the command the claim names and pasting its output, because recorded prose decays while the live command is the only witness.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/skills/meta-retro/SKILL.md
  - data/raw/claude-docs/guacamayo/skills/meta-feedback/SKILL.md
  - data/raw/claude-docs/guacamayo/skills/meta-wake/SKILL.md
  - data/raw/claude-docs/guacamayo/skills/meta-grow/SKILL.md
  - data/raw/claude-docs/guacamayo/skills/meta-dream/SKILL.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-20-meta-orchestrator.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-08-20-meta-orchestrator.md
---

# Re-Derive, Never Re-Read

guacamayo's tooling retro audits a ledger of hypotheses ("this hook will stop that
friction"), each with a typed metric (`presence:`, `absence:`, `count-drop:`, `ratio:`).
Its standing rule for verification: **for each row with a checkable metric, run the command
the metric names and paste command + output into the retro.** A row whose Status column
says "metric met" is a claim; a row verified from its own Status column is unverified.

## Prose decays too

Not just the status cell — the row's *description* rots the same way. Two recorded misses:

- A retro re-derived "scheduler plist still unloaded" from the row text while
  `launchctl list` showed the job running.
- Another read "both presence metrics met" while one target had **zero** matches, and the
  miss went undetected across two retro windows.

## The same rule in other places

- **Agent success reports.** When a capture skill spawns the retro as a sub-agent, it does
  not trust the agent's "done": it greps the ledger log for a header dated today before
  acknowledging. An ack written on an unverified spawn is how the retro silently stops
  running while the ledger claims it ran (see [[Due-vs-Acked Trigger Counters]]).
- **Board consistency.** An issue body is a cache that rots faster than the code — labels
  most of all. The orientation skill does not re-derive in prose whether the board's
  claims hold; it **runs the consistency check** and renders its output. A conformance
  claim must be produced by invoking the enforcement, never by re-deriving its rules from
  memory.
- **Dashboards.** The provenance rule — every recommendation carries the command that
  produced its number and the corpus it ran against — extends this rule from the ledger to
  the whole telemetry surface (see [[Telemetry Claim Verification Gate]]).
- **Ordering assumptions.** "Last" retro header is read by sorting on the R-number, not by
  file position, because the log is not in append order.

## Rule

If the evidence is something you can re-run, re-run it. Anything read back from a field
that a human or agent wrote is a pointer to evidence, not the evidence.

## Refinement: sort by date, not by round number (meta orchestrator plan)

The meta-orchestrator plan tightened the ordering rule above. Its draft used `grep -m1`
/ `tail -1` and picked the wrong "latest" retro round, because the ledger log had R12
before R11 in file position. The refined plan sorts extracted (date, label) pairs **by
date**. It rejects both file position and round number, noting that the round number
"happens to correlate with date today but the table's own state logic must not assume it
always will". Both sources agree that file position is wrong. They differ on whether the
round number is a safe key.

## See Also
- [[Path-Verified Build State Markers]] — extends (status markers verified against the tree)
- [[Falsifiable Hypothesis Gate]] — prerequisite-for (a row must be checkable before it can be re-derived)
- [[Append-Only Log Writer Invariants]] — extends (read by max key, not position)
- [[Silence Reads as Clean]] — extends
- [[Control Plane Owns the Join, Not the Truth]] — extends (world-tier state is re-read, never cached)
- [[Orchestrate Around the Human Gate]] — extends (an orchestrator that re-derives its position on every invocation)
- [[Verify the Issue's Premise Before Planning]] — extends (the issue body as a recorded claim)
