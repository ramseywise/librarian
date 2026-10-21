---
title: Live-Database Test Harness Hazards
tags: [infra, eval, pattern]
summary: "A test harness that seeds and deletes rows in a real Postgres has defect classes of its own. A suite with no local-host guard can delete production rows. Cleanup that swallows its errors leaks rows while every test stays green. A health probe can return 200 for a junk key. Per-test BEGIN/ROLLBACK is impossible through a stateless HTTP client, so isolation means cleanup-between with per-test unique scope. And 'code-complete, unverified' is not done: the first live run failed 3 of 4 tests."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis24-ingestion-integration-harness.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis24-ingestion-integration-harness.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis24-ingestion-integration-harness.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-03-dis24-ingestion-integration-harness.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-03-dis24-ingestion-integration-harness.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-03-dis24-ingestion-integration-harness.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-03-dis24-ingestion-integration-harness.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-03-dis24-ingestion-integration-harness.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-03-dis24-ingestion-integration-harness.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-03-dis24-ingestion-integration-harness.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis24-ingestion-integration-harness.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis24-ingestion-integration-harness.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis24-ingestion-integration-harness.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis24-ingestion-integration-harness.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-07-dis35-rls-behaviour-tests.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-07-dis35-rls-behaviour-tests.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-07-dis35-rls-behaviour-tests.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-07-dis35-rls-behaviour-tests.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-07-dis35-rls-behaviour-tests.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-07-dis35-rls-behaviour-tests.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-07-dis35-rls-behaviour-tests.md
---

# Live-Database Test Harness Hazards

From building the first integration tests for an ingestion write path against a local
Supabase stack (repo akira). Two issues shared the harness: one for upsert idempotency,
natural-key dedup and a known merge bug, and one for RLS behaviour (see
[[Make Each RLS Policy Individually Falsifiable]]). The harness is test code, but it holds
a privileged client that writes and deletes rows. That gives it failure modes ordinary
unit tests do not have.

## Isolation: rollback was not available

The checklist preferred `BEGIN`/`ROLLBACK` per test because it has zero cleanup cost.
That option was **architecturally unavailable**, not just fragile. The production code
takes a `SupabaseClient`, which talks to Postgres through PostgREST's stateless HTTP API,
so every request is its own transaction. A test cannot hold a transaction open across
several `insert()` calls. Two workarounds existed and both were wrong. Changing the
production function's parameter type just to serve a test is the wrong kind of change. A
raw `pg` connection would wrap a transaction the code under test never joins.

The chosen design was **cleanup-between with per-test unique scope**. Each test seeds its
own venue with a random suffix, and the natural-key lookup is scoped by venue. Parallel
test files never see each other's rows, with no lock and no serial mode. The parallel
safety comes from the data model, not from runner config. One risk was left named and
unmitigated: connection exhaustion under heavy parallelism. A pool-size cap is the
reversible fix if it ever shows up.

## Defect classes the review found

The build agent's Docker daemon never started, so the suite was reported as
"code-complete, blocked on environment". **On its first live run it failed 3 of 4.**
Every finding below was invisible until then.

1. **The suite could run against production and delete rows.** The URL getter checked
   that the env var was *set*, never that it was *local*. The Makefile target set it from
   the local stack, but the npm script could also be run directly, and it inherited
   `.env.local`, which pointed at the hosted project. Worse, the service-role constructor
   delegated to a shared admin-client factory that **read the environment itself** and
   never passed through the guarded getter. Guarding one path would have left the
   privileged, deleting client open. Fix: an `assertLocalStack()` that rejects any host
   other than localhost/127.0.0.1/::1, called on the anon path, the service-role path and
   in global setup, so the run fails before any credentials leave the process. Put a
   destructive-capability guard on *every* constructor, especially wrappers that do their
   own config reads.
2. **Cleanup swallowed its own errors, behind a comment that was wrong.** Each undo step
   was wrapped in `try { … } catch { /* swept by the next run's unique-suffix isolation */ }`.
   A unique suffix gives each run fresh ids. It does not remove rows a failed DELETE left
   behind. Add an FK or revoke a grant later, and cleanup fails on every run, rows leak on
   every run, and every test stays green. That is the silent-failure class the harness
   exists to catch, rebuilt inside the harness. Fix: try *all* undo steps, collect the
   failures, and throw with a count and the word "leaked". Keep the original insert error
   as the diagnostic and attach rollback failures as `cause`.
3. **The health check asserted nothing.** A bare `await fetch(...)` rejects only on
   network errors. The first fix added `res.ok` against the REST root, and measurement
   showed that endpoint returns **200 with the real key, a junk key and no key**. The probe
   now queries a table the seed actually writes, which returns 404 when the schema is
   missing. Its comment states what it still cannot catch: a wrong anon key, and missing
   grants. Measure a probe against the failure it claims to detect. See
   [[Artifact Is Not Evidence: Push and Probe]].
4. **The known-bug regression test was green for the wrong reason.** See
   [[Expected-Failure Tests Pass for Any Throw]].
5. **A constraint value from a neighbouring column.** The seed wrote a value that belongs
   to a different table's enum. After that, every CHECK-constrained column the seed writes
   was queried live and verified.

Verifying the fix: run the suite **twice in a row without a reset**, with row counts the
same before and after. Break an insert on purpose and confirm rollback leaves zero rows
and keeps the original error. Check the unit/db project split at the *file* level. A loose
`grep -c integration` counted test *names* and nearly produced a false violation report.

## Policy: block from the first landing

The CI job blocks from the start, with no advisory grace period. That follows the repo's
history: a drift check that printed "skipped" for weeks was worse than no check, because
it looked like a pass. Advisory mode is justified only when a credential is truly missing
in CI. This job needs only Docker, which every runner already has.

## Accepted duplication

The grant-restoration SQL ended up in three places: a Makefile target, the e2e CI job and
the new integration job. The coordinator first ruled against this under the repo's
no-duplication rule, then reversed. The scoping is in [[Derive the Gate, Don't Copy It]]:
that rule targets copies of a *derived fact* that go silently wrong, not boilerplate that
fails loudly when stale. The cost was accepted knowingly and written into Risks, so the
next person to change the grant model knows there are three copies.

## See Also
- [[Expected-Failure Tests Pass for Any Throw]] — extends (defect 4 in depth)
- [[Make Each RLS Policy Individually Falsifiable]] — prerequisite-for (the second suite built on this harness)
- [[Silent Failure Catalogue]] — instance-of (swallowed cleanup errors and assert-nothing probes)
- [[Scan-Floor Guard Against Silent No-Op Checks]] — related (a check that cannot tell clean from not-run)
- [[Artifact Is Not Evidence: Push and Probe]] — related (code-complete is not run)
- [[Written-but-Inert RLS Policies]] — related (same repo's operator scripts refuse non-local writes without confirmation)
