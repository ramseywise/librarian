---
title: Pin Client-Executable Functions With an Allow-List
tags: [patterns, infra, pattern]
summary: "Postgres functions are PUBLIC-executable by default, so assert the exact set of functions anon and authenticated can execute (an allow-list via routine_privileges and results_eq), not \"nothing dangerous\"; trigger-only functions can be revoked because EXECUTE is checked only at create-trigger time."
updated: 2026-10-17
sources:
  - data/raw/repos/nonprofit-success-ai/.claude--docs--plans--2026-10-07-r11-hardening-ci.md
---

# Pin Client-Executable Functions With an Allow-List

In a Supabase/PostgREST app every function in the exposed schema is an RPC endpoint. Postgres
grants EXECUTE to PUBLIC by default, so every `create function` that lacks an explicit
revoke can be called by `anon` and `authenticated`. That includes trigger functions that
were never meant to be called. A hardening pass on nonprofit-success-ai found the signup
trigger function plus **seven more** trigger-only functions still executable by clients.

## Mechanism

- **Probe for an exact allow-list, not for absence.** Query
  `information_schema.routine_privileges where routine_schema = 'public' and grantee in
  ('anon','authenticated')` and compare it with `results_eq` against the expected lists
  written in the pgTAP file. Add a comment per entry naming the migration that grants it.
  A new function with a default grant then fails the test instead of slipping through
  silently.
- **Look hardest at functions that default to PUBLIC.** Names like `*_enforce_*` and
  `*_guard_*` are trigger-only, and nobody should call them over RPC.
- **Revoking EXECUTE on a trigger function is safe.** Postgres checks EXECUTE when the
  trigger is created, not when it fires, so the auth trigger keeps working after
  `revoke execute ... from public, anon, authenticated`.
- **Keep deliberate exceptions on the list.** Helpers that RLS policies call (`is_admin()`,
  `user_org_ids()`) keep anon EXECUTE on purpose, and the allow-list says so.
- **Test scaffolding belongs inside the test transaction.** Seed helpers that used to live in
  a migration move into the test file's `begin;`. A test-only migration would otherwise
  become part of the shipped schema.

## Risk

The allow-list probe is the most likely blind failure: a missed PUBLIC-default function
leaves the expected list wrong. When the SQL was written without a database to run it on,
the plan header says so in an `Outstanding:` line that names the exact command to run
(`make db-reset && make db-test`).

## See Also
- [[Default-Deny Guard With a Named Allowlist]] — instance-of
- [[Written-but-Inert RLS Policies]] — extends
- [[Single-Writer Transition Command]] — extends
- [[Paired Allow Test for Deny Rules]] — extends
