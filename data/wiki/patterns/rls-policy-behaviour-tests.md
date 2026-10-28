---
title: Make Each RLS Policy Individually Falsifiable
tags: [infra, pattern]
summary: "Testing that RLS is enabled is not testing what a policy allows. Exercise every policy through the client role it governs, never service-role (which bypasses RLS). Tell a WITH CHECK rejection (an error) apart from a USING filter (zero rows, no error, confirmed by a service-role read). Import the app's visibility predicate instead of restating it. Assert the counter-intuitive shapes, such as an author who cannot read their own pending comment. And probe pg_class, because migration tracking reported local == remote on a volume five migrations behind."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis35-rls-behaviour-tests.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis35-rls-behaviour-tests.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis35-rls-behaviour-tests.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis35-rls-behaviour-tests.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis35-rls-behaviour-tests.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis35-rls-behaviour-tests.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis35-rls-behaviour-tests.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-07-dis35-rls-behaviour-tests.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-07-dis35-rls-behaviour-tests.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-07-dis35-rls-behaviour-tests.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-07-dis35-rls-behaviour-tests.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-07-dis35-rls-behaviour-tests.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-07-dis35-rls-behaviour-tests.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-07-dis35-rls-behaviour-tests.md
---

# Make Each RLS Policy Individually Falsifiable

From an RLS behaviour suite in a Supabase-backed product (repo akira). It runs anon,
signed-in and service-role clients against a local stack, on the shared harness described
in [[Live-Database Test Harness Hazards]]. The issue existed because a six-relation
exposure had shipped behind a green drift check. That check verified that RLS was *on*.
Nothing verified what each policy *did*.

## Two different claims

- **"RLS is enabled"** is a catalogue fact (`pg_class.relrowsecurity`). A drift check
  owns it.
- **"This policy admits exactly the right rows for this principal"** is behaviour. Only a
  seeded test through the right client proves it.

This suite asserts only the second and never queries the catalogue, so the two checks do
not duplicate each other.

## Mechanics that make each policy falsifiable

- **Test through the governed role, never service-role.** Service-role bypasses RLS, so an
  insert, update or delete it performs proves nothing about the insert, update or delete
  policies. A plan snippet that showed one select test per table reached 7 of 19 policies.
  Exercising insert, update and delete through owner and non-owner signed-in clients
  reached all 19.
- **Two kinds of deny look different.** A `WITH CHECK` violation comes back as an
  *error* at write time. A `USING` clause that filters the target row comes back as
  *success with zero rows affected*. Assert the right shape for each, and confirm a USING
  deny with a follow-up service-role read showing the row is unchanged. Otherwise "denied"
  and "silently did nothing for another reason" look the same.
- **Import the predicate, don't restate it.** The public-read policy for content tables
  matched an existing app function (`isAppVisibleContent`) exactly. The test calls that
  function to compute the expected visible set, so the suite cannot become a second,
  competing statement of the visibility rule. The same function degraded correctly on
  tables without a `needs_review` column. The test header states this so nobody relies
  on it by accident.
- **Assert the counter-intuitive shapes explicitly.** These are the cases a reviewer
  "knows" work:
  - `follows` is readable by any *signed-in* user but returns 0 rows to anon.
  - `comments` select has no owner override, so an author cannot read their own
    *pending* comment.
  - `reports` has an insert policy and no select policy, so a reporter cannot read back
    their own report.
- **Find where the policy is the only guard.** Five social tables had no application code
  reading or writing them. A seeded test there does not duplicate app-level coverage. It
  is the *only* coverage.
- **RLS on with zero policies is a posture worth testing.** Poll tables carry
  host/participant logic in application code behind a service-role client. Here the
  useful RLS test is narrower than "host vs participant": no non-service client can reach
  `host_token` or `participant_id` at all. That is the precondition the app-layer
  distinction depends on. Compare [[RLS On, No Policy for Server-Mediated Tables]].
- **Time-dependent predicates stay out of policies.** The events read policy deliberately
  leaves out expiry, because a policy whose result changes with no write is hard to reason
  about. Expiry lives in a separate app-only function, and the test follows the same
  split.

## The local stack can lie about its own schema

Two environment findings, both "green CLI check, red actual state":

1. **Out-of-band production state is invisible to migration replay.** Production enforced
   RLS on six core tables, but no migration enabled it. The local stack rebuilds *only*
   from migrations, so locally anon could read every row. The central assertion would have
   failed for a reason unrelated to policy logic. The fix was a migration that re-issues
   `enable row level security`, which is idempotent. See
   [[Written-but-Inert RLS Policies]].
2. **A stale Docker volume.** `supabase migration list` reported every migration as
   `local == remote`. That compares the CLI's tracking history, not live state.
   `schema_migrations` held 34 of 40 rows, and `relrowsecurity` was off on exactly the
   tables the missing migrations covered. `db-reset` (drop + full replay) fixed it.
   **Probe the catalogue, not the tracker**, before trusting a local run. Same lesson as
   [[Migration Done Means Pushed and Probed]].

## Smaller lessons

- Plan snippets marked "core pattern" left out NOT NULL columns the real schema requires
  (FKs, slugs, a column a later migration made required). Treat snippets as illustrative,
  and record each forced deviation.
- A one-time backfill (`insert … select`) is not a trigger. Rows the test creates later
  get no derived row unless the test inserts one.
- While the dependent tables were still open, the plan wrote their closed-posture
  assertions as expected-failures. That self-corrected once the closing migrations
  merged, and the assertions became plain passes before execution. If you use this, check
  for the specific failure. See [[Expected-Failure Tests Pass for Any Throw]].

## See Also
- [[Written-but-Inert RLS Policies]] — extends (from "is the policy in force" to "does it do what it says")
- [[Paired Allow Test for Deny Rules]] — related (each deny paired with the legitimate operation that must succeed)
- [[Live-Database Test Harness Hazards]] — prerequisite-for (the harness this suite consumes)
- [[RLS On, No Policy for Server-Mediated Tables]] — related (the zero-policy posture tested as "no non-service client reaches it")
- [[Principal Write-Surface Matrix]] — related (per-principal enumeration of the same surface)
- [[Migration Done Means Pushed and Probed]] — related (migration tracker vs live catalogue)
- [[Do-Instead-Nothing Rule Silences a Loud Denial]] — related (a rule turns a permission error into zero rows)
