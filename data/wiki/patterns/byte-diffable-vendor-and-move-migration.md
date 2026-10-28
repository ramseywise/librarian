---
title: Byte-Diffable Vendor-and-Move Migration
tags: [patterns, infra, pattern]
summary: Move a subsystem between repos by vendoring a byte-identical subset with cross-referencing provenance headers, deferring fixes until after the cutover, running old and new captures in parallel, and deleting from the origin only after one verified scheduled run.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-04-gua-93-telemetry-migration.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-08-04-gua-93-telemetry-migration.md
---

# Byte-Diffable Vendor-and-Move Migration

Source: the guacamayo telemetry migration (GUA-93), which moved the daily
session-capture pipeline out of a sibling repo.

## Why vendor instead of depend

About 660 of 1,458 LOC (plus the log config) were copied rather than imported. Every
dependency option was worse:
- A **uv path dependency** works locally but breaks GitHub CI.
- A **git dependency** needs private-repo auth and pulls in the whole dependency tree.
- **Re-cutting the seam** as a service adds a serialization contract nobody needed.

## Keep the copy byte-diffable

- **Provenance headers name the other copy**, in both files. A future reader knows a twin
  exists.
- **Drift breaks loudly.** Both copies parse the same daily JSONL, so a format divergence
  makes one of them fail visibly.
- **Defer fixes in vendored code.** Review findings against the copied code were
  reclassified as deferred, to a phase after the cutover. Fixing them during the move
  breaks `diff` as the proof that the move changed nothing.

## Cut over without a capture gap

- The source JSONL **rotates every ~5–15 days**, so a missed capture is permanent loss.
  Run both daily jobs in parallel during the overlap.
- **Copy the irreplaceable store** (`sessions.db`). Never rebuild it from sources that
  have already rotated away.
- **Delete from the origin only after one verified scheduled capture** in the new home.
  A manual run is not proof that the schedule works ([[Reversibility Cliff]]).

## Batch vs agentic split

The migrated half makes **zero LLM calls**, by decision. Earlier scheduled LLM reports
produced summaries nobody read, and they made an empty pipeline look healthy. Agentic
value belongs on demand and event-driven, and it should produce **dispositions, not
summaries**. The first target is drift triage for human-in-the-loop review. The
dashboard stays a static committed artifact over a JSON data layer
([[Format Contract Lives in the Parser]]).

## See Also
- [[Name-Only Sync Guards Miss Content Drift]] — extends
- [[Vendored Hooks Resolve to the Global Copy]] — alternative-to
- [[Reversibility Cliff]] — instance-of
- [[Format Contract Lives in the Parser]] — extends
