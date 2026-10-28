---
title: Paired Allow Test for Deny Rules
tags: [infra, pattern]
summary: Turn a written threat model into executable tests where each attack vector must fail closed and is paired with the legitimate operation that must succeed. Without the pair, a deny-everything policy passes. The threat model carries over when the stack changes; the test harness does not.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/dssg/docs/milestones/customer-portal.md
  - data/raw/claude-docs/dssg/docs/scoping/customer-portal.md
  - data/raw/claude-docs/dssg/docs/overview/roadmap.md
  - data/raw/claude-docs/dssg/docs/overview/design.md
---

# Paired Allow Test for Deny Rules

From the hardening plan for a client portal prototype (2026-07). Its security rules were
unusually mature for the stage (default-deny, owner-id immutability, terminal-state locking)
and backed by a documented twelve-vector threat model. There were zero tests. The rules were
*asserted*, not proven.

## The mechanism

- **Each vector becomes a test that must fail closed.** Example: a client-role user reads
  another tenant's engagement, flips its own role, or edits a locked terminal-state record.
- **Each failing-closed test is paired with the legitimate operation that must succeed.**
  Example: the same user reads *their own* engagement. A deny-all rule set, or a predicate no
  row satisfies, passes every deny test. Only the paired allow test catches it.
- **"Actually run, not just written."** The milestone is done when the suite executes and
  passes, not when the test file exists.
- **Before more features.** The plan puts the suite ahead of further feature work, and
  feature scoping waits on it. Once passing, the suite is the data-model contract: UI
  invariants (e.g. no admin-role toggle rendered for a client-role user) are verified against
  it, and dependent designs build on it.

## The threat model transfers, the harness doesn't

The portal was mid-decision between keeping a document-store backend and migrating to
Postgres. The plan made the harness conditional on that decision. The same twelve vectors run
either as document-store rules tests against an emulator or as RLS policy tests on a local
Postgres. The threat model is the durable asset. Every rule written in the old harness is code
to re-express later, which is one reason to settle the stack before writing more rules.

## See Also
- [[Written-but-Inert RLS Policies]] — extends (a policy that admits nothing is invisible without an allow-side probe)
- [[Principal Write-Surface Matrix]] — related (the principals × actions grid the vectors are drawn from)
- [[Agent Credential Ceiling]] — related (isolation claims an agent relies on)
- [[Specification by Example]] — instance-of (each vector is an executable example)
