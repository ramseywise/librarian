---
title: Principal Write-Surface Matrix
tags: [infra, mcp, pattern]
summary: List every principal (users, tenants, operators, services, and the model provider) as a row with submit/read/mutate/cause columns, then ask whether any principal's write surface exceeds its authority — the test that found a tenant able to approve its own lifecycle transition.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/playground/skills/design-system/SKILL.md
  - data/raw/claude-docs/akira/skills/design-system/SKILL.md
  - data/raw/claude-docs/kiez-archive/skills/design-system/SKILL.md
  - data/raw/claude-docs/diskoe/skills/design-system/SKILL.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-b28-social-schema.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-b28-social-schema.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-b28-social-schema.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-b28-social-schema.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-b28-social-schema.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-b28-social-schema.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-b28-social-schema.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-b29-reports-moderation.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-b29-reports-moderation.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-b29-reports-moderation.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-b29-reports-moderation.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-b29-reports-moderation.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-b29-reports-moderation.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-b29-reports-moderation.md
---

# Principal Write-Surface Matrix

## Method

akira's system-design skill requires a trust-boundary plate: one row per **principal** —
including non-human ones such as background jobs and **the model provider** — with columns:

| Principal | Can submit | Can read | Can mutate | Can cause (side effects) |
|---|---|---|---|---|

The single test: **does any principal's write surface exceed its authority?**

## What it found

A tenant could write the column that advances its own lifecycle state — making it its own
approver. Enumerating write surfaces per principal, rather than reviewing policies per
table, is what surfaced it.

## Companion system-plate rules

- **Semantics plate:** lifecycle state machine, an idempotency key per consequential
  command, concurrency rules, and a failure taxonomy that names DB unavailable / approval
  unavailable / duplicate request / concurrent write explicitly.
- One lifecycle column per entity; RLS with no anonymous select reads as "no data", not as
  an error; mark each schema item WRITTEN vs APPLIED.

## Owner-writable moderation status (akira social schema, 2026-08)

A social schema for saves, collections, follows, comments and reports had the same flaw
at column level. The owner-only `comments_update` row policy let an author update any
column of their own comment, including `moderation_status`. So an author could reset a
removed or flagged comment to `pending`. A row-level policy answers "whose row?", not
"which columns may this principal write?". The planned fix was a trigger that resets the
status to `pending` whenever the comment text changes. The moderation status is then
written only by the operator principal, or by the system as a consequence. It was
recorded as an open decision because comment moderation was not live yet. Related
choices from the same pair of plans:

- A moderation action sets the comment to `removed` and never deletes the row, so the
  evidence is kept. The report row gets additive audit columns (`actioned_by`,
  `actioned_at`, `admin_notes`) *before* any UI writes to it.
- The polymorphic `reported_entity_id` has no foreign key on purpose. The application
  checks the target exists, and the queue shows "(deleted)" when a join misses.
- One shared basic-auth credential on the admin surface means `actioned_by` is free text.
  There is no per-operator identity until roles exist, so the audit column records a
  claim, not a principal.
- Admin reads go through the service role, which bypasses RLS, so no admin policies are
  written. The public-read policy exists only for approved comments.

## See Also
- [[Written-but-Inert RLS Policies]] — extends (policy existence vs policy authority)
- [[Four-Source Provenance Contract]] — related (who caused a state change)
- [[Realtime Is UI Sync, Not the Event Bus]] — related (same plate)
- [[Four-Stage Design Pipeline with Backflow]] — related (part of; system stage)
- [[Agent Credential Ceiling]] — related (an agent principal's read column capped at its human's)
- [[Paired Allow Test for Deny Rules]] — related (executing the matrix's denials, each paired with an allowed operation)
- [[State Writer Never Owns Its Side Effects]] — related (sole-writer ownership of a lifecycle field)
- [[Advance-Only Machine Writes on a Shared Lifecycle]] — instance-of (the machine principal's transitions on a shared lifecycle column)
- [[Async Seam Before the Table]] — related (operator identity: the principal the moderation audit columns lacked)
- [[Single-Writer Transition Command]] — extends (the fix for a tenant able to drive its own lifecycle transition)
