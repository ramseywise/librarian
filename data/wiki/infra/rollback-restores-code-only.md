---
title: Rollback Restores Code Only
tags: [infra, pattern]
summary: "A host rollback restores code, never migrations, rows or schedules. So the promotion runbook states that scope before anyone needs it, sits on deploy invariants (a deploy never migrates, never runs the pipeline, never enables a schedule; promotion needs CI green on the exact SHA), invents no auto-promote threshold, and is authored before the host exists so its first read is not mid-incident."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-29-dis268-deploy-promotion-path.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-29-dis268-deploy-promotion-path.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-29-dis268-deploy-promotion-path.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-29-dis268-deploy-promotion-path.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-29-dis268-deploy-promotion-path.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-29-dis36-production-smoke.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-29-dis36-production-smoke.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-29-dis36-production-smoke.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-29-dis36-production-smoke.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-29-dis36-production-smoke.md
---

# Rollback Restores Code Only

From two linked plans for a first production deploy (repo akira, 2026-09-29): the
**promotion path** (how code reaches production and comes back) and the **production
smoke** (what gets checked once it is there).

## The scope sentence the runbook leads with

A host's "roll back to previous deployment" restores **code only**. It does not undo:

- a migration applied before or after the rollback point. If the promoted commit's
  migration already ran, rolling the code back leaves the new schema in place.
- any row written, updated or deleted since the rollback point.
- a schedule that the newer code enabled.

The runbook says this before any rollback is ever run. The risk the plan could not
design away was that the one real rehearsal is a real production operation. The only
mitigation was making sure whoever runs it is not learning the migration-vs-code
distinction for the first time under pressure. This is the deploy-side form of
[[Reversibility Cliff]]: code is cheap to reverse, schema and data are not.

## Invariants that make code-only rollback safe

Code-only rollback is only enough if a deploy never does the irreversible things:

- A deploy **never applies a migration**. Migrations are pushed and probed (drift check
  green) *before* the code that reads them is promoted. See
  [[Migration Done Means Pushed and Probed]].
- A deploy **never runs ingestion, enrichment or publishing**, and never enables the
  ingest schedule.
- **Promotion requires CI green on the exact commit being promoted.** This is a required
  check in host or branch-protection settings, not a convention anyone can skip. Where that
  setting is a UI toggle that cannot be committed, the runbook names the toggle. It never
  ships a no-op config file that pretends to be the control.

The invariants live in one release-checklist doc that the operator reads before promoting,
not only in an issue thread. Each release is one row: SHA, who promoted it, timestamp, and a
one-line description. For a rollback, record the SHA rolled back to, the reason, and the
time it took.

## Decisions that refused to invent a number

- **Eval gate on the served SHA: yes, by SHA correlation, not a re-run.** The check is that
  the gate's workflow concluded green on the exact SHA now serving, which `gh run list
  --json headSha,conclusion` answers. A re-run proves a different execution.
- **When to auto-promote: never, for this beta.** "N green smoke runs, then auto-promote"
  would be an unmeasured threshold invented for the plan. If it is ever wanted, it is a
  separate decision with its own record.
- **Who may promote** is a host-access setting, not a new role column in the app schema.

## Author before the host exists

The host did not exist yet. The plan split the work into a deliverable-now half (runbook,
invariants, CI-check documentation: doc-only, zero runtime blast radius) and a blocked
remainder (one real promote → roll back → time it, run once the host lands). The blocked
half was named as an operational rehearsal rather than sized as engineering effort.
Writing the runbook first means it has been reviewed before anyone uses it. Waiting would
mean its first read happens during the first production promote.

## The smoke that follows the promote

The production smoke check follows the same honesty rules:

- **One script, `--target <url>`**, run against staging first and then production. It
  **replaces** the manual checklist in the team's notes tool, rather than adding a second
  list that can drift from it.
- **Split by what each check needs.** Lane A was buildable with no app host: 6 of 14 checks,
  including a bundle-secrets scan, an error-body regression guard, schema drift against the
  current database, and the DB-only slice of the anon-key RLS probes. Lane B needs a deployed
  origin.
- **Unrunnable checks say why.** They report `SKIPPED — no target` or `NOT IMPLEMENTED —
  in-memory store` (for the shared rate limiter), never a false pass. See
  [[A Check Must Say Why It Could Not Check]].
- **Reuse, don't re-specify.** The RLS check reuses the restore drill's existing
  anon-key visibility queries rather than writing a second copy.
- **Re-verify the premise.** One planned check assumed raw DB error text could reach a
  response body. Re-verification at triage showed every site already returned a stable
  code, so the check became a regression guard expected to pass. An earlier version of the
  plan had reached READY and never been executed. See [[Path-Verified Build State Markers]].

## See Also
- [[Migration Done Means Pushed and Probed]] — prerequisite-for (the invariant that keeps a rollback code-only-safe)
- [[Reversibility Cliff]] — instance-of (code reverses, schema and rows do not)
- [[Gate vs Ship Make Targets]] — related (the gate that must be green on the promoted SHA)
- [[A Check Must Say Why It Could Not Check]] — related (SKIPPED / NOT IMPLEMENTED in the smoke script)
- [[Audit-Don't-Assert Release Checklist]] — related (every checklist item names an artifact and a verifier)
- [[Paid Tiers Start at the Beta, Not the Alpha]] — related (the host decision the rehearsal waits on)
