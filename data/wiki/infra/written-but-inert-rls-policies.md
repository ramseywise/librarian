---
title: Written-but-Inert RLS Policies
tags: [infra, pattern]
summary: A row-level-security policy in the migration chain does nothing until `enable row level security` runs on its table — five policies were written and inert, four tables had RLS enabled out-of-band with no migration saying so, an admin review queue read 95 rows through the anon client and silently showed zero, and two policies gated on a status value their tables had never written; the diagnostic is one probe, anon vs service-role row counts on the same filter.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/playground/skills/design-system/SKILL.md
  - data/raw/claude-docs/playground/docs/research/2026-08-28-data-stack-map.md
  - data/raw/claude-docs/akira/docs/research/2026-09-03-dis121-rls-migration-gap.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-03-dis121-rls-migration-gap.md
  - data/raw/claude-docs/akira/docs/research/2026-08-28-data-stack-map.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-08-28-data-stack-map.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-03-dis121-rls-migration-gap.md
  - data/raw/claude-docs/playground/docs/research/2026-09-03-dis121-rls-migration-gap.md
  - data/raw/claude-docs/diskoe/docs/research/2026-08-28-data-stack-map.md
  - data/raw/claude-docs/akira/skills/design-system/SKILL.md
  - data/raw/claude-docs/kiez-archive/skills/design-system/SKILL.md
  - data/raw/claude-docs/diskoe/skills/design-system/SKILL.md
  - data/raw/repos/akira/README.md
  - data/raw/repos/diskoe/README.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis35-rls-behaviour-tests.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis35-rls-behaviour-tests.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis35-rls-behaviour-tests.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis35-rls-behaviour-tests.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis35-rls-behaviour-tests.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis35-rls-behaviour-tests.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis35-rls-behaviour-tests.md
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
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis121-rls-enable-migration.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis121-rls-enable-migration.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis121-rls-enable-migration.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis121-rls-enable-migration.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis121-rls-enable-migration.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis121-rls-enable-migration.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis121-rls-enable-migration.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis122-admin-review-queue.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis122-admin-review-queue.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis122-admin-review-queue.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-03-dis122-admin-review-queue.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-03-dis122-admin-review-queue.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-03-dis122-admin-review-queue.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-03-dis122-admin-review-queue.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-03-dis122-admin-review-queue.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-03-dis122-admin-review-queue.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-03-dis122-admin-review-queue.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis122-admin-review-queue.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis122-admin-review-queue.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis122-admin-review-queue.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis122-admin-review-queue.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis46-restore-drill.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis46-restore-drill.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis46-restore-drill.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis46-restore-drill.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis46-restore-drill.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis46-restore-drill.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis46-restore-drill.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/repos/playground/README.md
  - data/raw/repos/nonprofit-success-ai/.claude--docs--research--smoke-test.md
---

# Written-but-Inert RLS Policies

From a Supabase project (repo akira) where which client factory a file imports *is* its
authorization model — anon (browser), anon + user cookie (server, as the user), service
role (admin, bypasses RLS) — with no other layer.

## Three ways a policy fails to be in force

1. **Written, never enabled.** `create policy` succeeded; `alter table … enable row level
   security` was never issued, so the policy existed in `pg_policies` and gated nothing.
   Nothing in the chain or CI checked `pg_class.relrowsecurity`.
2. **Enabled out-of-band.** Four of six tables had RLS on in production via a dashboard
   action no migration recorded ("Class C"). Correct behaviour, unreproducible from the
   chain, invisible to drift checks keyed on migration history. The fix migration
   re-issues `enable row level security` unconditionally — it is a boolean and a no-op
   when already set, so it converts the undocumented state into a documented one with zero
   behaviour change.
3. **Enabled, with a predicate no row satisfies.** Two tables' public-read policies gated
   on `review_status = 'published'`; the live distribution was `needs_review` and
   `approved`. The policy would admit nothing forever, and nobody would notice until a
   consumer surface appeared — the security-layer version of
   [[Every Column Names Its Reader]].

## The silent production bug

The admin review queue read `events … where needs_review = true` through the **anon**
server client, while the active public-read policy required `needs_review = false`. The
query could never return a row. Probed live:

```
anon,    needs_review=true → 200, content-range */0,  0 rows
service, needs_review=true → 200, content-range 0-94/95, 95 rows
```

95 events awaited review; the dashboard showed none. The write path on the same screen
used the admin client and worked if handed an id — there was just no way to discover one.
Every symptom read as "no data" rather than "no permission", which is why it had never
been filed.

## The diagnostic

One read-only probe settles most of this: run the same filter with the anon key and the
service-role key and compare `content-range`. Equal counts → RLS off or the policy is
open; zero vs N → a policy (or the lack of one with RLS on) is hiding rows; zero vs zero
→ the vocabulary mismatch case. For grants, read `pg_class.relacl` directly rather than
`information_schema` views, which under-report other roles' grants.

## Severity labelling

The issue was filed at a severity resting on one unmeasured claim (that anon held write
grants on two tables). The research supplied the instrument — the `relacl` query — and
explicitly left the production reading to the operator rather than predicting it. "RLS
off" and "anon can write" are different facts; the second was inferred from a CI comment,
not measured.

## Enforcing the client boundary as an import-graph gate

Because the imported client *is* the authorization model, the service-role client was
moved into its own module so a Client Component cannot reach it by autocomplete. A
`make gate admin-client` check then walks the import graph from every `'use client'` file,
stops where the bundler stops (a `'use server'` module), and fails if the admin module is
reachable. It catches **transitive** reachability too, which is the case a reviewer misses.
The same repo's operator scripts default to dry run, print `[target]` (the project they are
about to touch) first, and refuse a non-local write without `--confirm-production`.

## Closing it: decisions from the fix plans

The closure (repo akira, 2026-09-03) shipped as four migrations on one branch, pushed in
one session. The reasoning worth reusing:

- **Make the fix correct regardless of the unknown root cause.** Why two of three
  consecutive `enable row level security` statements were not in force could not be
  settled from the repo (candidates: the migration was history-marked via `migration
  repair` and never ran, plus one out-of-band dashboard toggle; or something later
  disabled RLS). The fix re-issues `enable` unconditionally on every affected relation,
  which is correct under both explanations. The forensic question (does anything besides
  a migration change RLS here?) was recorded, not blocked on.
- **RLS on, no policy, for service-role-only tables.** Every reader of the leaked relations
  was traced to the admin client, so enabling RLS with zero policies changed nothing for
  the app and closed only the direct REST path. A table nothing reads publicly gets no
  public policy yet — "if nothing selects it, it is not a column yet" generalised.
- **Open reference tables keep a `using (true)` policy, and the probe checks the join.**
  Enabling RLS with no policy on `venues` would have nulled the `events → venues` embed on
  every public page while the parent row count stayed identical. The fix reused the
  existing (inert) open-read policy, and verification asserted a non-null embed on a live
  published event — a row-count match alone cannot catch a joined-field regression.
- **Keep-and-harden beats drop when consumers are unknowable.** An unread view was a
  candidate for `DROP`. The project owner chose `security_invoker = true` instead: "no
  reader in this repo" cannot rule out a dashboard query, saved SQL, a BI card or a
  partner integration, a drop is unrecoverable for those, and the flag closes the same
  exposure reversibly. The view then inherits the base table's RLS, so both the view and
  its table must be probed — an invoker-rights view over an RLS table looks fixed while a
  mistake in either half leaves it open. (This revised the general rule: drop an unread surface
  only when its consumers are enumerable; see [[Artifact Is Not Evidence: Push and Probe]].)
- **`SECURITY DEFINER` + public `EXECUTE` + mutable `search_path` is the escalation path.**
  All flagged functions were pinned to `search_path = ''`; `EXECUTE` was revoked from anon
  and authenticated only on the one directly callable definer function (the others were
  triggers). Three hand-created function bodies had to be read from `pg_proc` before any
  `CREATE OR REPLACE` — see [[Unfinished Work Must Fail Closed]].
- **Don't fold a product decision into a security migration.** The vocabulary-mismatch
  predicate on two verticals was documented, not fixed: changing what makes a row public
  is a product call, and a reviewer would be approving it under a security label.
- **Severity confirmation does not gate a fix that is safe either way.** Whether anon held
  write grants only changed the label (critical vs high); the migration closes the
  exposure if it exists and is a zero-behaviour reproducibility fix if not. A write-attempt
  probe was ruled out — a successful one would itself mutate production.
- **The drift check now reads RLS state.** A third layer derives its table list from
  `create table` statements in the migrations (never a hand list) and asserts
  `relrowsecurity` via an RPC. A verification grep in a follow-up plan omitted `-i` while
  the regex it was checking was case-insensitive and the SQL was uppercase — it returned
  0 matches instead of 6 and would have tripped the plan's own "stop, real gap" condition
  on a grep bug.

## A second instance: a new reader on a no-policy table (akira review, 2026-09-14)

An occurrence read path added two queries on a table that an earlier RLS-closure migration had
deliberately left at "RLS on, no policy", because at that time it had zero readers. The plan's
migration step said "none needed". The request path used the anon-key server client, so both
queries returned `{rows: 0, error: null}` on every production request. No warning fired, every
event fell back to the legacy path, and the whole PR would have been a silent no-op. The
fake-client unit suite could not see it, because fakes do not model RLS. The three-round
review only caught it when the orchestrator probed production read-only: the anon client saw 0
occurrence rows, and service role saw 502.

The fix was a `public_read` policy whose `using` clause joins to the parent row's published
state, the same shape as an existing enrichment-table policy. It was pushed on its own and
closed only after an anon probe returned the published rows, and 0 rows for an unpublished
parent. Reading through the admin client instead was rejected, because it bypasses RLS as the
visibility gate. The rule: **when a table gains its first anon-side reader, the plan has to
include the policy migration.** "RLS on, no policy" only holds while the table really has no
anon reader ([[RLS On, No Policy for Server-Mediated Tables]]).

## The mirror case: grants that were never revoked (hosted smoke test, 2026-08)

The inverse of an inert policy is a *permissive default nobody wrote*. On a hosted
Postgres platform, new tables get `ALL` granted to the anon and authenticated roles by
default. A migration history that only ever ran `grant` statements had therefore exposed
every table at the privilege layer. Forced RLS was the only thing that prevented an actual
leak. A follow-up migration added explicit `revoke`s. The first run of the previously
never-run pgTAP suite found this, along with 2 test bugs, which argues for running a
DB-level test suite against the *hosted* instance, not only local.
Check: list `information_schema.role_table_grants` for anon/authenticated on every table,
and treat any grant that no migration states explicitly as a finding.

## See Also
- [[Migration Done Means Pushed and Probed]] — extends (the policy-layer instance of file-exists-is-not-evidence)
- [[Every Column Names Its Reader]] — related (a policy predicate nobody writes is the same plausible trap)
- [[Split Service Deployment]] — extends (the three-client trust model it assumes)
- [[Production Hardening Patterns]] — extends
- [[Agent Security Risk Taxonomy]] — related (mitigation belongs in the component that owns the risk — here the table, not the app)
- [[Principal Write-Surface Matrix]] — extends (per-principal enumeration finds authority gaps per-table review misses)
- [[Budget Without a Meter Is a Preference]] — related (permission-denied rendered as no data)
- [[Paired Allow Test for Deny Rules]] — related (the allow-side test that catches a predicate admitting nothing)
- [[Capability Token in a Serialized Row]] — related (RLS can be correct and the server still leaks the row to the client)
- [[RLS On, No Policy for Server-Mediated Tables]] — related (the deliberate no-policy posture, documented as a decision)
- [[Audit the Class, Not the Instance]] — extends (the review-queue fix, audited across the whole admin boundary)
- [[Unfinished Work Must Fail Closed]] — related (the function-hardening migration from the same closure)
- [[Make Each RLS Policy Individually Falsifiable]] — extends (behaviour tests for what each in-force policy admits, per principal)
- [[Restore Drill: Rebuild-from-Migrations Visibility Probe]] — extends (periodic rebuild-and-probe that catches this class before a real repair)
- [[Production Write Guard: Explicit Override, Never Ambient]] — extends (the operator-script target print and override in full)
- [[RLS Gates Rows, Not Columns]] — related (row policy that leaked columns)
- [[Tighten a Visibility Gate by Backfilling the Visible State]] — related (the inverse risk: tightening a policy that a live route depends on)
- [[Signal Without a Consumer]] — instance-of (a defined control nothing activates)
- [[ACL-Aware Retrieval and Tenant Isolation]] — extends (RLS as the tenancy layer for a shared retrieval index, with its pooling and ownership footguns)
- [[Pin Client-Executable Functions With an Allow-List]] — extends (the function-EXECUTE analogue: PUBLIC-default grants pinned by an exact allow-list)
- [[Single-Writer Transition Command]] — extends (definer function + caller JWT as the only writer)
