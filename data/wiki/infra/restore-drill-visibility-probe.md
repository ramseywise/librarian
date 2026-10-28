---
title: "Restore Drill: Rebuild-from-Migrations Visibility Probe"
tags: [infra, pattern]
summary: A restore drill rebuilds the database from the migration chain alone, seeds a published and an unpublished row per gated table, and diffs anon vs service-role visibility against production — it catches what a boolean RLS-state check cannot (a vacuous policy predicate, security state applied outside the migrations), provided the local rebuild uses production's grant model.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis46-restore-drill.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis46-restore-drill.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis46-restore-drill.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis46-restore-drill.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis46-restore-drill.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis46-restore-drill.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis46-restore-drill.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-07-dis46-restore-drill.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-07-dis46-restore-drill.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-07-dis46-restore-drill.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-07-dis46-restore-drill.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-07-dis46-restore-drill.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-07-dis46-restore-drill.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-07-dis46-restore-drill.md
---

# Restore Drill: Rebuild-from-Migrations Visibility Probe

From a hardening item on a Next.js + hosted-Postgres app (akira). The question it answers:
*if production were lost and rebuilt from the migrations directory alone, would the
anonymous client see only what the visibility gate intends?* The motivating defect: several
tables had row-level security turned on in production with no migration saying so. A
rebuild would bring them back with RLS off, the Postgres default. That would leak the
unpublished catalogue on day one of a real repair. See [[Written-but-Inert RLS Policies]].

## Two checks, two questions

- **A drift layer** asks whether production's RLS boolean per table matches what the
  migration chain implies. It is cheap: `enable row level security` is deterministic DDL, so
  a table list derived from `create table` statements plus one RPC reading
  `pg_class.relrowsecurity` gives the whole answer. No rebuild needed.
- **The restore drill** asks whether a fresh rebuild is *safe*. A boolean cannot answer
  that. A table with RLS on and a predicate no row ever satisfies (a policy gated on
  `review_status = 'published'` in a table whose importer never writes that value) reads as
  `rls_enabled: true` and is still a trap. Only a content probe sees it.

The drill reuses the drift layer's table list and RPC instead of building a parallel one.
Both feed one diff, computed by a pure module.

## Mechanism

1. Rebuild a local stack from the migrations directory alone (`db reset`).
2. **Override the local grant model to match production.** Current local tooling ships a
   restrictive default (no `SELECT` grant to the API roles). Production still runs the
   legacy `grant all` model, with RLS as the only restraint. Without the override every table
   reads 403 to the anon key whatever its RLS state. That is a false "everything is safe": a
   tooling default posing as evidence.
3. **Seed a published and an unpublished row per gated table.** An empty table returns
   nothing to everyone, so an anon `select` on it proves nothing. One row cannot separate
   "correctly gated" from "vacuous predicate". A pair can.
4. Probe anon vs service-role row counts, read-only, on the local rebuild and on production.
   Diff them. Never run a write probe against production.
5. Append a dated block to a committed log. Never overwrite earlier runs.

The runbook (human-run, writes the log) and the scheduled workflow (weekly, fails the job)
are two ways of invoking the same check, not two implementations. The drill is kept out of
the pre-commit gate: it needs Docker and a full migration replay.

## Failure semantics

The check fails rather than skips when credentials are missing, and names the variable. It
has an explicit, separately named escape hatch. Review rounds then found three further
places where it could pass without checking anything. See
[[A Check Must Say Why It Could Not Check]] and
[[Scan-Floor Guard Against Silent No-Op Checks]].

## Known limit

The drill's table list is hand-maintained. A cross-check against the derived table list
catches a drill table that has vanished from the schema. It does not catch a new gated table
the drill doesn't cover yet. This is the same trade-off hand-maintained column probes accept.
It was flagged, not solved.

## See Also
- [[Written-but-Inert RLS Policies]] — extends (the defect class the drill generalizes)
- [[Artifact Is Not Evidence: Push and Probe]] — instance-of (the migration chain is the artifact; the rebuilt database is the evidence)
- [[Migration Done Means Pushed and Probed]] — related (the drift gate whose RLS layer the drill reuses)
- [[A Check Must Say Why It Could Not Check]] — related (PITR check fix from the same review)
- [[Scan-Floor Guard Against Silent No-Op Checks]] — related (zero-tables-probed fix from the same review)
