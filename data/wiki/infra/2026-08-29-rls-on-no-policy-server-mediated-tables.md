---
title: RLS On, No Policy for Server-Mediated Tables
tags: [infra, decision]
summary: "A table whose rows are each harmless can still be a customer list in aggregate, and RLS gates rows, not query shape. When every reader is server-side code using the admin client, enable RLS and write no anon policy: a policy names its reader, and this table has none on the anon key. Then prove the CHECK constraint fires with a rejected INSERT."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-08-29-b41-partner-table.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-29-b41-partner-table.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-29-b41-partner-table.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-29-b41-partner-table.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-29-b41-partner-table.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-29-b41-partner-table.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-29-b41-partner-table.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-14-dis73-occurrence-read-path-pr1.md
---

# RLS On, No Policy for Server-Mediated Tables

## Context

An event-discovery app (repo akira) moved a hard-coded partner list into a Supabase table,
with partner slugs used as short codes in shareable links. Each row is innocuous: a name, a
slug, a district. The obvious posture, an anon `SELECT` policy like the other public
tables, would expose the whole table to anyone holding the anon key.

## Decision

**Enable RLS with no policy.** Every reader is a Server Component using the admin
(service-role) client, so no policy is needed and none is written.

## Why

- **Harmless per row, sensitive in aggregate.** A full `select *` is the venue and partner
  list, effectively a customer list. Row-level security asks *which rows* a caller may see.
  It has no notion of "one row per request is fine, all rows at once is not". If anon can
  read one row, anon can read them all.
- **Short codes are enumerable.** A slug short enough to share is short enough to
  brute-force. A public read path turns the share code into a directory lookup.
- **A policy names its reader.** Writing an anon policy "for later" declares a reader that
  doesn't exist. That is the same trap as a column nobody reads, and on the security
  surface it is worse.
- **RLS on, rather than RLS off**, so that a future direct anon read fails closed (zero
  rows) instead of open. The diagnostic from [[Written-but-Inert RLS Policies]] applies:
  compare anon and service-role counts.

## Accepted tradeoffs and rules

- **A CHECK constraint duplicates the district list** already defined in application code.
  This is accepted drift risk: the database rejects an unknown district on any write path,
  at the cost of two lists to keep in sync.
- **Prove the constraint fires, not that it exists.** Verification is an `INSERT` with a bad
  value that the database *rejects*. Seeing the constraint in a schema dump is not evidence.
  See [[Migration Done Means Pushed and Probed]].
- **No env toggle for the data source** (table vs. hard-coded list). A toggle doubles the
  states to test and lets production silently serve the stale list.
- **The rename lands first, as a separate mechanical commit**, so the behavioural diff
  (table read, constraint) can be reviewed without rename noise.

## When the table gains a reader (akira review, 2026-09-14)

The premise "no anon reader" expired without notice. A later read path queried one of these
tables through the anon client and got an empty set, not an error, on every request. A plan
that adds the first anon-side reader of a no-policy table has to size the policy migration
alongside it. See [[Written-but-Inert RLS Policies]] for that instance.

## See Also
- [[Written-but-Inert RLS Policies]] — extends (the deliberate counterpart: RLS on with no policy, on purpose and documented)
- [[Data Clusters by Writer and Trust]] — related (classify the table by its writer and readers before choosing a posture)
- [[Capability Token in a Serialized Row]] — related (the other way a server-mediated table leaks: the server ships the row to the client)
- [[Migration Done Means Pushed and Probed]] — related (the constraint is verified by a rejected write)
- [[Every Column Names Its Reader]] — extends (the same rule applied to policies)
