---
title: Atomic Archive-Then-Delete for Irreversible Retention
tags: [infra, pattern]
summary: A retention job that deletes rows after copying them must do both in one database statement (a writable CTE, `DELETE ... RETURNING` feeding `INSERT ... SELECT`), behind a row ceiling enforced in the database and in the app, followed by a count-delta assertion — because there is no undo, every layer aims at refusing or detecting, not repairing.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis37-replay-corpus.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis37-replay-corpus.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis37-replay-corpus.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis37-replay-corpus.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis37-replay-corpus.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis37-replay-corpus.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis37-replay-corpus.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-29-dis359-retention-verification.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-29-dis359-retention-verification.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-29-dis359-retention-verification.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-29-dis359-retention-verification.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-29-dis359-retention-verification.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-07-dis37-replay-corpus.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-07-dis37-replay-corpus.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-07-dis37-replay-corpus.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-07-dis37-replay-corpus.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-07-dis37-replay-corpus.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-07-dis37-replay-corpus.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-07-dis37-replay-corpus.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-07-dis197-a1-latlng.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-07-dis197-a1-latlng.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-07-dis197-a1-latlng.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-07-dis197-a1-latlng.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-07-dis197-a1-latlng.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-07-dis197-a1-latlng.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-07-dis197-a1-latlng.md
---

# Atomic Archive-Then-Delete for Irreversible Retention

From a 90-day retention job on a recommendation app (akira). The job moved aged
recommendation logs into a de-identified replay corpus, then deleted the originals. The
originals were the only pre-launch measurement data the product had, and there was no
backfill. A bug in the delete could not be repaired afterwards.

## The mechanism

**One statement, not two round-trips.** The preservation half (insert into the corpus) and
the irreversible half (delete from the source) run inside one SQL function as a writable
CTE: `DELETE ... RETURNING *` feeds an `INSERT ... SELECT`. If the insert fails, the delete
rolls back with it. Two calls from application code could partially fail and leave a row
deleted with no copy.

**Four layers, each aimed at refusal or detection:**

1. **Ceiling in the database.** The SQL function takes a `p_max_rows` argument and refuses
   if more rows qualify. This holds even if the application layer has a bug. A `WHERE`
   regression that matches every row is refused rather than executed.
2. **Pre-flight in the application.** A read-only count function runs first; the library
   refuses before calling the archive function if the count exceeds the ceiling.
3. **Atomic statement**, as above.
4. **Post-call delta assertion.** The library re-counts both tables and throws loudly if the
   source lost a different number of rows than the corpus gained. The rows have already
   moved by then. The point is fast detection, not undo, because there is no undo.

Set the ceiling generous relative to real volume (here about 100x current growth). It is
not there to throttle normal operation. It is there to refuse the "delete everything"
failure.

## Unattended-run safety

- **Dry-run by default.** The CLI only writes with an explicit `--write` flag. The flag
  parsing lives in an exported pure function so the default can be tested; an untested
  default was a review finding.
- **A typed confirmation on manual dispatch.** A scheduled trigger always writes, because it
  only fires from merged, reviewed code. A manual `workflow_dispatch` writes only when a
  `confirm` input equals a fixed string (`ARCHIVE`); a blank or wrong value runs the dry
  run. CI dispatch inputs cannot enforce "must equal X", so a `required: true` field alone
  could be filled with anything. A protected-environment approval gate was rejected because
  it needs repo settings outside the branch's diff to take effect. The test runs the actual
  `run:` shell snippet under bash for each case, not a string match on the YAML.
- **Weekly, not daily.** A 90-day window tolerates a week of slip, and fewer runs mean fewer
  chances for a destructive bug to fire against production.
- **First run by hand, well before the deadline.** Dispatch once manually, verify the delta,
  then let the schedule take over. If the smoke run finds a bug, remove the `schedule:`
  trigger and keep the dry run shipping. The count function and dry run are safe to ship
  before the destructive path is trusted.

## Defects the review round found

Both blockers sat in the copy, not the delete:

- **The archive copied 15 of 25 columns.** The insert/select lists were written from one
  migration. Four migrations had touched the source table. The fix derived the full column
  set by reading every migration that names the table. An archive is a schema mirror, and
  it drifts the same way any copy of a schema does.
- **De-identification was a no-op on the wrong column.** The spec said "strip the user id".
  No such column existed. The real identifying field was raw GPS coordinates inside a JSON
  context blob. The fix rounds them to 2 decimal degrees inside the archive's select list,
  coarser than the app's finest distance bucket.

Each fix was proven by installing the pre-fix function body on the local database and
watching the test fail, then reapplying the migration. See
[[Red-Then-Green Proof for Fix-Stage Tests]].

## Build against what exists

The requirement named three fields to keep or strip. Two did not exist: no user-id column,
and no outcome column (a separate, unbuilt deliverable). The plan built retention for the
schema as it actually was. It reserved a nullable `outcome` column so the later item is an
`UPDATE`, not a second migration. It recorded the spec/code mismatch as a design-contract
entry rather than rewriting the requirement. It did not pull two larger, undated items into
the one dated item. See [[Deadline-Scope Isolation]].

## Verifying the first real run (akira, 2026-09-29)

A verification plan for the same retention job found it had never actually run. The
scheduler's minutes were exhausted, so every scheduled run failed at 0 steps, and no row
was old enough to purge until about 2026-11-27 (the first logged row plus the 90-day
window). The plan is therefore **calendar-gated**, not build work. Done means the first
real scheduled run completes, archives at least one row older than the window into the
replay corpus, and the archived row carries no location field.

**Rejected shortcut.** The CLI already accepts `--retention-days N`, so the archive path
*could* be exercised against production today with a small N. With only 18 live rows, that
would archive and delete production's only data to force a green checkbox. That is a
destructive probe, and it is forbidden. The one legitimate early check is a dry run
(`--retention-days 1`, no `--write`) against a freshly seeded local stack. It proves only
that the CLI still runs and ticks no done-when box. See
[[Path-Verified Build State Markers]] for the register that called this job "ENFORCED"
before it had ever run.

## See Also
- [[Paid Tiers Start at the Beta, Not the Alpha]] — related (exhausted CI minutes left the retention schedule silently not running)
- [[Deadline-Scope Isolation]] — extends (the research half of the same retention job)
- [[Red-Then-Green Proof for Fix-Stage Tests]] — related (how the archive fixes were proven)
- [[Migration Done Means Pushed and Probed]] — related (the archive migration is not done until pushed and probed)
- [[Silent Failure Catalogue]] — related (the delta assertion throws instead of logging)
- [[Arm Unattended Writers by Risk Type]] — related (destructive-risk writers ship with cron on but dry-run by default)
