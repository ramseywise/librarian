---
title: RLS Gates Rows, Not Columns
tags: [infra, pattern]
summary: "Row-level security decides which rows a role can read, never which columns, so adding audit columns (who set a flag, their free-text reason) to a table with a public read policy publishes them to anonymous clients — keep the value the reader needs on the public row and move the audit trail to an admin-only side table, written in the same request with a loud failure if the audit write fails."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-25-dis392-s4-reputation-flag.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-25-dis392-s4-reputation-flag.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-25-dis392-s4-reputation-flag.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-25-dis392-s4-reputation-flag.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-25-dis392-s4-reputation-flag.md
---

# RLS Gates Rows, Not Columns

Found in review of an operator-set venue flag in an events-discovery product (repo akira,
2026-09-25). The flag demotes a known tourist-trap venue in ranking (see
[[Specificity-Adaptive Ranking and Slate Composition]]).

## What happened

The migration added four columns to `venues`: `reputation_flag` plus three audit
columns, `_note`, `_set_by` and `_set_at`. The plan's RLS reasoning looked sound. The
table already had RLS on, a public `SELECT` policy, and no anon or authenticated write
policy. So the flag would be "publicly readable like `category` already is, writable only
through the service-role admin route."

The plan missed that the public policy was `using (true)`. **A row policy gates rows,
not columns.** Every column on the table, including new ones, is readable by `anon`. The
API route as written would have published the operator's email and their free-text
reason for calling a named business a tourist trap. The migration had already been
pushed.

## The fix

- A follow-up migration **dropped** the three audit columns from `venues`. It was checked
  in a rolled-back transaction on the local stack (apply the first migration, then the
  drop, and confirm only the flag remains).
- The audit trail moved to a new admin-only table, `venue_reputation_flag_changes`, with
  RLS on and no policy (see [[RLS On, No Policy for Server-Mediated Tables]]). The
  operator page reads the latest note from there through the admin client.
- The flag itself stayed on `venues`, because its reader is the scorer's venue join.
  **Whether a public `tourist_trap` value on a named business is acceptable was left as
  an open question for the product owner**, not decided in code.

## Two writes, one request

The route updates the flag, then inserts the audit row. If the audit insert fails after
the flag update succeeded, the route returns **500 `audit_write_failed`**, not a silent
200. The module doc records that the flag change has already taken effect by then. That
is a deliberate, documented partial-failure contract, not an oversight.

## Checks

- Before adding a column to a table, read its `SELECT` policies. With `using (true)`,
  every new column is public.
- Sensitive per-row metadata (actor identity, free-text justification) goes in a
  separate table whose policy matches *its* audience.
- Postgres column privileges (`grant select (col, ...)`) are the column-level tool. RLS is
  not.

## See Also
- [[Written-but-Inert RLS Policies]] — related (another way RLS looks right on paper and isn't)
- [[RLS On, No Policy for Server-Mediated Tables]] — instance-of (the posture the audit table uses)
- [[Capability Token in a Serialized Row]] — related (correct RLS, leaked fields anyway)
- [[Every Column Names Its Reader]] — extends (the reader decides which table a column belongs on)
- [[Kiez Project]] — instance-of
- [[Tighten a Visibility Gate by Backfilling the Visible State]] — related (tightening a `using (true)` policy without a blackout)
- [[ACL-Aware Retrieval and Tenant Isolation]] — extends (RLS used for tenant isolation in a shared vector index)
