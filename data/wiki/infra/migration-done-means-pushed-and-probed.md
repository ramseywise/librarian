---
title: Migration Done Means Pushed and Probed
tags: [infra, pattern]
summary: A migration file existing is not evidence it ran — twice a migration was marked done while its column did not exist, and one unique index took three migrations to actually exist because `create unique index if not exists` guards on the name, not the definition — so "done" means pushed, then probed with a query that cannot be intercepted by triggers or policies, and a derived drift check runs in the gate.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/playground/skills/design-system/SKILL.md
  - data/raw/claude-docs/playground/docs/research/2026-08-28-data-stack-map.md
  - data/raw/claude-docs/akira/docs/research/2026-08-27-schema-audit.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-08-27-schema-audit.md
  - data/raw/claude-docs/akira/docs/research/2026-08-28-data-stack-map.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-08-28-data-stack-map.md
  - data/raw/claude-docs/akira/docs/research/2026-08-28-src-scripts-review.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-08-28-src-scripts-review.md
  - data/raw/claude-docs/diskoe/docs/research/2026-08-27-schema-audit.md
  - data/raw/claude-docs/playground/docs/research/2026-08-27-schema-audit.md
  - data/raw/claude-docs/diskoe/docs/research/2026-08-28-data-stack-map.md
  - data/raw/claude-docs/diskoe/docs/research/2026-08-28-src-scripts-review.md
  - data/raw/claude-docs/playground/docs/research/2026-08-28-src-scripts-review.md
  - data/raw/claude-docs/akira/skills/design-system/SKILL.md
  - data/raw/claude-docs/kiez-archive/skills/design-system/SKILL.md
  - data/raw/claude-docs/diskoe/skills/design-system/SKILL.md
  - data/raw/claude-docs/akira/docs/research/2026-09-16-dis296-structural-schema-drift.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-16-dis296-structural-schema-drift.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-16-dis296-structural-schema-drift.md
  - data/raw/repos/akira/CLAUDE.md
  - data/raw/repos/diskoe/CLAUDE.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-b48-schema-remediation.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-b48-schema-remediation.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-b48-schema-remediation.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-b48-schema-remediation.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-b48-schema-remediation.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-b48-schema-remediation.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-b48-schema-remediation.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-29-b41-partner-table.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-29-b41-partner-table.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-29-b41-partner-table.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-29-b41-partner-table.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-29-b41-partner-table.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-29-b41-partner-table.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-29-b41-partner-table.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis142-redistribution-posture.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis142-redistribution-posture.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis142-redistribution-posture.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis142-redistribution-posture.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis142-redistribution-posture.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis142-redistribution-posture.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis142-redistribution-posture.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis296-structural-schema-drift.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis296-structural-schema-drift.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis296-structural-schema-drift.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis296-structural-schema-drift.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis296-structural-schema-drift.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis295-event-edition-identity.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis295-event-edition-identity.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis295-event-edition-identity.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis295-event-edition-identity.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis295-event-edition-identity.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-24-dis384-measurement-loop.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-24-dis384-measurement-loop.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-24-dis384-measurement-loop.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-24-dis384-measurement-loop.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-25-dis386-lexical-rrf.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-25-dis386-lexical-rrf.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-25-dis386-lexical-rrf.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-25-dis386-lexical-rrf.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-25-dis386-lexical-rrf.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-25-dis392-s4-reputation-flag.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-25-dis392-s4-reputation-flag.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-25-dis392-s4-reputation-flag.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-25-dis392-s4-reputation-flag.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-25-dis392-s4-reputation-flag.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-25-lifecycle-operating-contract.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-25-lifecycle-operating-contract.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-25-lifecycle-operating-contract.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-25-lifecycle-operating-contract.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-25-lifecycle-operating-contract.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-19-pr342-fp16-poll-list.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-19-pr342-fp16-poll-list.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-19-pr342-fp16-poll-list.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-19-pr342-fp16-poll-list.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-19-pr342-fp16-poll-list.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-22-dis340-audience-attribute.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-22-dis340-audience-attribute.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-22-dis340-audience-attribute.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-22-dis340-audience-attribute.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-22-dis340-audience-attribute.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-07-dis35-rls-behaviour-tests.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-07-dis35-rls-behaviour-tests.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-07-dis35-rls-behaviour-tests.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-07-dis35-rls-behaviour-tests.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-07-dis35-rls-behaviour-tests.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-07-dis35-rls-behaviour-tests.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-07-dis35-rls-behaviour-tests.md
  - data/raw/repos/playground/CLAUDE.md
  - data/raw/repos/playground/README.md
---

# Migration Done Means Pushed and Probed

Schema conventions from a Supabase/Postgres project (repo akira), each with the defect
that earned it.

## `IF NOT EXISTS` guards on name, not definition

The same unique index took three migrations to exist. The first created it non-unique.
The second used `create unique index if not exists` with the same name — Postgres saw
the name taken and skipped, so uniqueness was never enforced while the migration chain
claimed it was. The third dropped first, then created. A fourth created differently-named
indexes and dropped the old, on the reasoning that a fresh name cannot collide with
anything for a guard to skip on.

Contrast: `alter table … enable row level security` has no guard and needs none — it
sets a boolean, so re-running converges to the same state. The trap needs a *named*
object whose existence check and definition check can diverge.

## Probe in a way that cannot be intercepted

The probe that "tested" the index was itself wrong. It inserted a second `is_current`
row, saw success, and read it as "not enforced" — but a supersede trigger (present in
production, absent from the chain) had flipped the existing row to `is_current = false`.
The insert never collided; it superseded. Deleting the probe row then left one entity
with history and no current row, repaired by hand.

The correct probe inserts with `is_current = false` (no trigger fires), then tries to
UPDATE it to true — refused with `23505`, which is the real confirmation. **Never verify
against production data with a destructive probe.**

Same class, different layer: a grant check via `information_schema.role_table_grants`
can return a confidently empty result because those views filter to grants the current
role is party to. `pg_class.relacl` is the stored ACL and is not filtered. *A check that
cannot see half its subject is not a check.*

## Done = pushed and probed

Twice a migration was marked done while its column did not exist — once because
`supabase/config.toml` was missing so every `db push` silently failed with "cannot find
project ref", and once with two items where one check failed *closed* (a select errored)
and one failed *open* (a content-hash read returned null and re-enriched everything). Two
silent failure modes, one root cause: the file was taken as evidence of the run.

Rule: a `B-` item is not done until `make db-drift` (a derived check comparing the chain
against the live schema) passes, and CI re-runs it on `main` after merge. The audit's
conclusion on tooling: what was missing was **not a reviewer but an invariant checker** —
two instances of the same bug are not prevented by more review prose.

## Index the predicate you actually serve

25 indexes existed and none covered the filter every public read used (`review_status`),
which the app applied and the RLS policy applied a second time. Fixed with a partial
index, small because 9 of 476 rows qualify, and landed before the catalogue grew by
orders of magnitude — the only cheap time.

## The natural key, deliberately not unique

`source_url` was unique (correct for provenance) and exactly why the catalogue
multiplied: the same event at two URLs became two rows (17 duplicate groups). A unique
index on the natural key `(venue, lower(title), start_at)` would lie twice — 17 pairs
already violate it, and NULL `start_at` values are DISTINCT in a Postgres unique index.
It became a lookup index instead: ingest asks cheaply whether a colliding row exists and
routes the loser to `review_status = 'duplicate'` rather than failing the write.

## Structural Drift the History Check Misses

A drift check that compares only migration history, a short column list (~14 columns) and
RLS on/off booleans passed while a measured structural diff between local and production
found **93 differences**: 6 missing triggers, 34 production-only indexes, and 27
nullability/default mismatches. Sort them into three classes before acting:

- **A — missing objects** (a trigger that exists in migrations but not in prod, or the
  reverse): need a migration.
- **B — redundant production-only objects** (hand-added indexes): reconcile into a
  migration or allowlist them by name.
- **C — known pre-history**: objects older than the migration history; allowlist.

A full schema diff (`db diff --linked`, migra-based) needs Docker, takes 1–2 minutes and
does not cover policies or grants, so it is wrong for the local pre-merge gate. Run it in
post-merge CI or on manual dispatch against a committed baseline/allowlist: report the
known set and **fail only on a new difference by name**.

### Building the structural check (decisions from the plan)

- **Allowlist, don't reconcile, in a detection issue.** Class B (duplicate indexes, 27
  nullability/default diffs) was allowlisted with a reason on every entry, not fixed by a
  migration. Dropping one of a duplicate index pair on a live table needs a query-plan
  check. Adding `NOT NULL` needs a backfill first. Folding that work in would have turned a
  drift-*detection* issue into a drift-*repair* issue that skipped those reviews. The
  reconciliation became a checklist item on the same issue, not a new issue and not an
  unfiled "follow-up #TBD" that nobody could chase.
- **Never allowlist the defect class.** The six missing triggers were never put in the
  baseline. A regression test asserts that trigger statements always count as violations.
- **Do not wire a known-red check into every-push CI before the fix lands.** If the CI step
  had landed before the trigger fix, every push to `main` would have reported red. That
  noise looks the same as a new regression and trains people to reach for the skip
  variable. The manual `make` target can be red, and should be. The automatic CI step was
  gated on the fix being merged **and** pushed to production, checked against the remote
  migration list.
- **Capture a real fixture before writing the parser.** A live read-only capture showed the
  output was one 24.7 KB string of semicolon-terminated statements. It also showed that the
  drafted baseline missed reality: non-unique duplicate indexes, a `drop extension`, and
  same-name/different-definition constraints that migra emits as drop + add-not-valid +
  validate triples. Several hours later the branch had moved and the capture differed again.
  The convergence test was rewritten to say "all N statements accounted for" instead of a
  count the plan had predicted.
- **Classifier failure direction.** A quote- and dollar-quote-aware statement splitter is
  the riskiest piece. Every misparse classifies as an unknown statement, and an unknown
  statement fails the check. A parser bug can produce a false positive but never a false
  negative.
- **Its own escape hatch, checked first.** `ALLOW_SCHEMA_DIFF_SKIP` is checked before
  anything else. This copies the later grants check's order, not the original drift
  check's order, which had a bug.

## `CREATE OR REPLACE` Cannot Change a Signature

Postgres identifies a function by its full argument-type list. `CREATE OR REPLACE` with new
trailing parameters does **not** replace the old function. It creates a second overload
beside it, and PostgREST's RPC resolution then breaks on the ambiguous name. A signature
change is drop-then-create in a **new** migration, never an edit of the applied one.
Migrations run as a single transaction, so callers never see a moment where the function is
missing. Even so, do not run the migration during an active ingestion window. The new
parameters default to `null`, so rolling back the caller restores the old behaviour without
a third migration.

## Say Precisely Why It Is Unpushed

When a migration is authored but deliberately not applied, the plan records the exact reason,
because **the wrong reason points at the wrong repair.** An earlier incident diagnosed
"unapplied migration" when the real blocker was an expired CLI login. Following that
diagnosis ran `db push` into "column already exists". In the redistribution plan (akira,
2026-09), credentials worked and the drift check read live state correctly. The push was
withheld by instruction, so that changing the shared remote schema stays an explicit human
act. The plan then listed the operator steps in order: push, drift check green, regenerate
types, and a probe expecting nulls on the existing rows.

## Verify in a rolled-back transaction, never by dropping

For non-destructive verification against the local stack, wrap the probe in
`begin; \i migration.sql; <checks>; rollback;`. Volatility questions (is
`array_to_string` IMMUTABLE? no, STABLE) are answered the same way, or by reading
`pg_proc.provolatile`. In one incident a raw `drop table` on the local dev database, run
to "reset" a migration, forced a hand replay of about 120 migrations. New tables and
functions get the roles-by-name grant triple, `revoke ... from public, anon,
authenticated`, rather than relying on `public` alone.

## Served-path selects on unpushed columns (akira reviews, 2026-09)

Two reviews found code that already read and wrote columns whose migrations were unpushed. In
one, the new column was added to the served-path enrichment select; PostgREST rejects the whole
select on an unknown column, every chunk site did `if (error) return null`, and the only trace
was an aggregate "join incomplete" warning with `error.message` discarded — so production would
serve every item with no enrichment, 200 OK. The boot-time schema probe covered only the two
base tables, not the enrichment tables, leaving those columns structurally unprotected. Fixes:
log `error.message` at each `return null`, extend the probe to every table a served select
touches, and state in the handoff that the migration must be pushed before merge.

## See Also
- [[Rollback Restores Code Only]] — extends (why migrations must land before promote: rollback cannot undo them)
- [[Every Column Names Its Reader]] — complements
- [[Always-Red Check Carries No Signal]] — extends (the drift check itself was red and unread for a week)
- [[Written-but-Inert RLS Policies]] — related (the policy-layer version of "file exists ≠ it is in force")
- [[Production Hardening Patterns]] — extends
- [[Split Service Deployment]] — related (Supabase Postgres as the shared store these rules govern)
- [[Parallel Across Lanes, Migrations Alone]] — related (never run two migration-adding builds at once)
- [[Natural Key Without a Discriminator Collapses Rows]] — alternative-to (the under-specified key)
- [[Single-Subject End-to-End Trace]] — extends (done means observed in production, for a whole pipeline)
- [[A Check Must Say Why It Could Not Check]] — extends (the drift gate's diagnosis layer)
- [[Unfinished Work Must Fail Closed]] — extends (a partial migration must refuse to apply, not apply the safe subset)
- [[Event–Occurrence Split, Added Behind the Old Column]] — related (an additive migration where a missing push fails both closed and open)
- [[Coalesce Against a Never-Null Source]] — related (the RPC change that needed drop-then-create)
- [[One Use Case Behind Two Transports]] — related (transactional RPCs with service-role-only grants, pushed and probed)
- [[Widening a Postgres Function Creates an Overload]] — related (regenerated types exposed a duplicate RPC signature)
- [[Pure Derivation Is a Generated Column]] — related (volatility probed in a rolled-back transaction)
- [[RLS Gates Rows, Not Columns]] — related (a pushed migration that leaked audit columns)
- [[Item Lifecycle Ledger as a New Table]] — related (validated with begin/rollback before push)
- [[A Constraint Cannot Tell a Regression From a Legacy Null]] — related (deciding a constraint while the migration is still unpushed)
