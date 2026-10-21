---
title: Landed Is Not Complete
tags: [eval, infra, pattern]
summary: A logging gate that awaits the row write proves a row landed, not that it is complete or joinable — audit against production rows with a schema probe that cannot lie, split rows at the migration boundary, and never declare VERIFIED on a cross-table check that passed because the population it conditions on was empty.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-08-29-v5-t0-audit.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-29-v5-t0-audit.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-29-v5-t0-audit.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-29-v5-t0-audit.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-29-v5-t0-audit.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-29-v5-t0-audit.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-29-v5-t0-audit.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-31-data-tab-revision.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-31-data-tab-revision.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-31-data-tab-revision.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-31-data-tab-revision.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-31-data-tab-revision.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-31-data-tab-revision.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-31-data-tab-revision.md
---

# Landed Is Not Complete

From an audit of recommendation logging (repo akira, 2026-08). The serving path awaited
`recordResultSet` before returning, so the gate "every served result set has a log row"
was enforced in code. The roadmap's criterion was stronger — "100% of result sets carry a
**complete** row" — and nothing enforced that. The check reported green on the weaker
property.

## Two ways a landed row is incomplete

1. **No column at all.** Fields the spec requires were never migrated. The row lands
   cleanly because there is nowhere to put the value. These are not backfillable.
2. **Column present, value null.** The migration ran, the column exists, but some writer
   path does not populate it — or the row predates the migration.

A third, found while drawing the schema as an entity graph: **complete but not
joinable.** Two interaction tables declared `event_id uuid not null` with no `references`
clause, two lines below a properly constrained `result_set_id`. Every row is complete,
and the join that personalization depends on is unenforced.

## How the audit was run

- **Production rows, not fixtures.** Fixture tests had already passed; the claim was
  about live data.
- **The schema probe is ground truth when docs disagree.** One doc said most stamp and
  pool fields had no column; the roadmap said all were wired. The probe settled it. When
  the REST client cannot read `information_schema`, select every expected column by name
  in one query — it errors if any column is absent ([[Migration Done Means Pushed and Probed]]).
- **Split rows at the migration boundary.** Eight pre-migration rows had nulls in the new
  fields (expected); ten post-migration rows had to be complete. Mixing them makes either
  conclusion wrong.
- **Read-only script, results appended to the plan.**

## The vacuous pass

The cross-table check was "no result set with `returned_count > 0` and zero viewport
rows" — i.e. nothing served but untracked. It passed. But **all 18 result sets had
returned zero items**, so the condition could not fail on any of them. The audit still
headlined "VERIFIED". A conditional check must report the size of the population it
conditions on; N=0 is "unexercised", not "clean"
([[Scan-Floor Guard Against Silent No-Op Checks]]).

## Thresholds are free until rows exist

A dwell threshold disagreed between code (500 ms) and spec (1000 ms). With no viewport
rows yet, changing it costs nothing. Once rows exist, the value is baked in at write time,
so a change splits the series and needs a version stamp so queries can filter to
comparable windows ([[Frozen Version Stamps on Logged Results]]). Decide such constants
before the first production row, not after.

## See Also
- [[Scan-Floor Guard Against Silent No-Op Checks]] — instance-of (a conditional check over an empty population)
- [[Silence Reads as Clean]] — instance-of
- [[Frozen Version Stamps on Logged Results]] — related (the threshold-change half)
- [[Migration Done Means Pushed and Probed]] — related (the probe that settles doc contradictions)
- [[Every Column Names Its Reader]] — related (a written table nothing joins is the mirror defect)
- [[UNGATED Metric Convention]] — related (gates that pass without measuring)
- [[Baseline Only a Decided, Deterministic State]] — instance-of (one viewport of two delivered, recorded rather than closed)
