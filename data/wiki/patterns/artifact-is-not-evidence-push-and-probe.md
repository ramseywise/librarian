---
title: "Artifact Is Not Evidence: Push and Probe"
tags: [patterns, infra, pattern, conflict]
summary: A migration file, a posture table, or a workflow existing in the repo proves nothing about production — every security or retention claim must be probed against the live system with a probe that can distinguish "blocked" from "empty".
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/research/2026-09-03-rls-closure.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-03-rls-closure.md
  - data/raw/claude-docs/akira/docs/research/2026-09-03-divergence-since-waslosheute-mvp.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-03-divergence-since-waslosheute-mvp.md
  - data/raw/claude-docs/akira/docs/research/2026-09-16-dis288-favourites-feedback-loop.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-16-dis288-favourites-feedback-loop.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-16-dis288-favourites-feedback-loop.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-03-divergence-since-diskoe-mvp.md
  - data/raw/claude-docs/playground/docs/research/2026-09-03-divergence-since-diskoe-mvp.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-03-rls-closure.md
  - data/raw/claude-docs/playground/docs/research/2026-09-03-rls-closure.md
  - data/raw/claude-docs/akira/docs/research/2026-09-27-berlin-venue-provenance.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-27-berlin-venue-provenance.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-27-berlin-venue-provenance.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis118-rls-closure.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis118-rls-closure.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis118-rls-closure.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-03-dis118-rls-closure.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-03-dis118-rls-closure.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-03-dis118-rls-closure.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-03-dis118-rls-closure.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-03-dis118-rls-closure.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-03-dis118-rls-closure.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-03-dis118-rls-closure.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis118-rls-closure.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis118-rls-closure.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis118-rls-closure.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis118-rls-closure.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-14-dis265-activity-date-range.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-14-dis265-activity-date-range.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-14-dis265-activity-date-range.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-14-dis265-activity-date-range.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-14-dis265-activity-date-range.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-14-dis265-activity-date-range.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-14-dis265-activity-date-range.md
---

# Artifact Is Not Evidence: Push and Probe

Found while closing row-level-security (RLS) gaps on a Supabase-backed product (akira).
The repo contained a migration enabling RLS on every table and a security-posture table in
the docs asserting "RLS on" per table. Production disagreed.

## How artifacts get mistaken for evidence

- **A migration present in the tree is not a migration that ran.** The CLI's
  `migration repair` command marks a migration as applied *without executing its SQL*. The
  history table and the file list agreed; the database did not.
- **A posture table is an assertion, not a measurement.** The docs' per-table "RLS: on"
  column had been filled from the migration files, never from `pg_class.relrowsecurity`.
- **A stale "nothing invokes this" claim is the mirror image.** An issue asserted a
  retention job was unscheduled; the workflow was live and had been running weekly. The
  claim had been copied from an older doc, not re-verified against the tree.

In each case the artifact was real, the belief it supported was false, and no check was
positioned to notice.

## The probe has to be able to say "no"

The first probe attempted — select from each table with the anonymous key and count rows —
is itself vacuous: zero rows means either "RLS blocked me" or "the table is empty". See
[[Scan-Floor Guard Against Silent No-Op Checks]]. The probe that works reads the policy
state directly: a `SECURITY DEFINER` RPC that returns `relrowsecurity` for every table in
`public`, callable from CI with the service role, with the result asserted per table.

Two design rules fell out of writing it:

- **Derive the enumeration from the migrations, not a hand-kept list.** The posture table
  drifted because it was maintained by hand; the probe's table list is parsed from the
  migration files so a new table is probed the moment it exists.
- **Drop an unread surface rather than secure it.** A view no code read still had to be
  either policy-protected or removed; removing it is the smaller, more honest change.
  *(Conflict flagged 2026-10-17: the fix plan reversed this — the owner kept the view with
  `security_invoker = true` because external readers cannot be ruled out from the repo and a
  drop is irreversible. See `_conflicts.md` and [[Written-but-Inert RLS Policies]].)*

## Push and probe as a protocol

Every migration or workflow change that carries a security or data-lifecycle claim ships
with a probe that fails if production does not exhibit the claimed state. The deploy step
is "push", the CI job afterward is "probe", and the docs table is generated from the probe
output rather than typed. The same discipline applies to retention jobs: a cascade on
`result_set_id` was deleting telemetry rows in the same transaction that archived their
parent, and the archive's own column list was the only evidence anyone had checked.

## The crawl ran; the load didn't

A provenance check on a venue catalogue (repo akira, 2026-09-27) asked why the database
showed only one district as probed after a city-wide crawl. The crawl **had run** (4,361
sites read), but it wrote only a JSONL file. The database columns were written by a
**second, separate load command** that was last run three days earlier, so zero of the
new sites had a probe timestamp. The run file also showed `finished_at: null`, because
the process was interrupted before writing its footer. The artifact (a full crawl
directory) looked like evidence of a populated database. Two-step pipelines need the
probe to read the destination, not the intermediate file. The same check found the
calendar classifier over-firing on opening-hours pages for shops, restaurants and cafés,
so read the classified URL before trusting a row of those kinds.

## A read path that selects an unpushed column

A plan adding two date columns to a content table (repo akira, 2026-09) was split at the
push. Phase A (migration and write path) had to be **pushed and probed** before Phase B
(the read path that selects the new columns) could merge. The loader throws on a select
error, so deploying B first makes every recommendations request fail on "column does not
exist", the same failure shape an earlier incident had produced. Three rules:

- **The schema probe derives its column list from the real loader constant**, so a new
  column is probed at boot the moment the loader selects it. A hand-kept probe list is
  deliberately not one entry per migration.
- **A migration-drift gate failing on exactly the one expected unapplied migration is the
  acceptable state** for a built-but-unpushed slice. The plan header said so explicitly,
  so the red was not mistaken for noise or "fixed" by skipping.
- **Rollback a column only after the reading code is reverted and deployed**, never in the
  same push. The columns are additive and harmless while unread.

## See Also
- [[Scan-Floor Guard Against Silent No-Op Checks]] — prerequisite-for (a probe that can vacuously pass is no probe)
- [[Deterministic Review Substrate]] — extends (tool output as the evidence class, not prose assertions)
- [[Data Clusters by Writer and Trust]] — complements (which tables' deletion changes what a user sees)
- [[Verification Loops]] — instance-of (an independent verifier positioned after the change)
- [[Fallback Mistaken for the Design]] — related (a rendered surface that was the empty-pool fallback, not the ranked path)
- [[Restore Drill: Rebuild-from-Migrations Visibility Probe]] — extends (probing the rebuilt-from-artifacts database, not just production)
- [[Dated Node Must Name the Row]] — related (the plan whose read path had to wait for the push)
