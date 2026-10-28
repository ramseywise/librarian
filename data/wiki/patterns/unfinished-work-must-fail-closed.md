---
title: Unfinished Work Must Fail Closed
tags: [patterns, infra, pattern]
summary: "A half-finished artifact whose \"do not apply yet\" warning lives in a comment will apply cleanly and report success — a migration hardening 3 of 6 functions, with the other 3 as a commented placeholder, would have been recorded as applied while the invariant was never in force — so the first executable statement of anything unfinished must be a guard that refuses to run."
updated: 2026-10-17
sources:
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
  - data/raw/claude-docs/akira/docs/plans/2026-09-02-dis59-server-error-handling.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-02-dis59-server-error-handling.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-02-dis59-server-error-handling.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-02-dis59-server-error-handling.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-02-dis59-server-error-handling.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-02-dis59-server-error-handling.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-02-dis59-server-error-handling.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-06-dis197a-beta-blockers.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-06-dis197a-beta-blockers.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-06-dis197a-beta-blockers.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-06-dis197a-beta-blockers.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-06-dis197a-beta-blockers.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-06-dis197a-beta-blockers.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-06-dis197a-beta-blockers.md
---

# Unfinished Work Must Fail Closed

Found in review of a row-level-security closure on a Supabase project (repo akira).

## The defect

A migration pinned `search_path = ''` on six database functions. Three of the bodies
were known; the other three had been created by hand outside the migration chain, so
their current definitions had to be read from production before a `CREATE OR REPLACE`
could be written safely (guessing a trigger body risks silently changing behaviour —
worse than the search-path bug itself). The author left a clearly-worded placeholder:
*"must not be pushed until the three bodies are pasted in."*

The placeholder was **entirely SQL comments**. The file applied cleanly, hardened three
of six functions, and reported success. Had an operator run `db push` before the
pre-read, the migration history would say "applied" while three `SECURITY DEFINER`
functions kept a mutable search path — the project's signature failure, "recorded as
applied while the invariant was never in force" (see
[[Migration Done Means Pushed and Probed]]).

## The fix

Make the guard executable and put it **first**:

```sql
do $$ begin
  raise exception 'UNFINISHED: bodies for f1, f2, f3 not yet pasted from pg_proc; '
                  'applying now would harden 3 of 6 and report success. See plan Step 2.';
end $$;
```

Verified against a disposable local database: the migration tool exits non-zero and
refuses the file. The guard is deleted in the same edit that pastes the real bodies. The
message names what is missing, what a premature apply would silently do, and how to
finish — so the refusal is also the instructions.

## The general rule

A warning a human must read is not a control; a statement the runtime executes is.
Anything committed in a partial state — a migration, a config with placeholder values, a
script with a TODO step — should be shaped so that running it early **fails**, not so
that it does the safe-looking subset. Doing the subset is the worst outcome because it
turns "not done" into "done" in every record a later check consults.

Same project, same lesson at the plan level: a placeholder host allowlist in a plan was
written as literal `REPLACE_WITH_QUERY_RESULT_1` strings with a "DO NOT ship" comment —
values that would fail loudly if copied, rather than plausible-looking example hosts that
would not.

The same holds for public-facing facts that are unknown at plan time. A pre-beta checklist
needed a legal entity name, a contact domain and a crawler contact URL. Instead of guessing
plausible values, every unknown went in as a greppable `[[NEEDS: ...]]` token. The tokens
were collected into one owner checklist, and the launch gate is zero grep hits for
`[[NEEDS:` across the shipped tree. A guessed value that looks right passes review; a token
cannot ship unnoticed.

## Prove the check detects, not just that it fails

The same review caught a second, related gap. A new drift-check layer asserting RLS was
enabled on every table had been "verified" by showing it failed when its helper RPC was
missing. That proves the check fails when it cannot run — a different claim from "the
check detects a table with RLS off", and only the second is the safeguard. Closed by
direct experiment on the local stack: create a scratch table with RLS off, confirm the
check reports it, enable RLS, confirm it flips, drop the table. See
[[Red-Then-Green Proof for Fix-Stage Tests]].

## See Also
- [[Migration Done Means Pushed and Probed]] — extends (a partial migration is the fastest way to "applied but not in force")
- [[Written-but-Inert RLS Policies]] — related (same closure effort)
- [[A Check Must Say Why It Could Not Check]] — related (UNCHECKED vs FAILED; here, unfinished vs done)
- [[Red-Then-Green Proof for Fix-Stage Tests]] — related (prove detection by planting the defect)
- [[Silence Reads as Clean]] — related
- [[Polite Crawler Robots Compliance]] — related (the crawler user-agent contact placeholder that uses the same token)
