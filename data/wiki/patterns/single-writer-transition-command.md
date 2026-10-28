---
title: Single-Writer Transition Command
tags: [patterns, infra, pattern]
summary: "Make one SECURITY DEFINER function, called with the caller's JWT, the only writer of a lifecycle: it derives the current stage, authorises, checks guards and writes event, audit and approval rows atomically; ship it additive-first and revoke direct writes in a second PR, naming the interim hole until then."
updated: 2026-10-17
sources:
  - data/raw/repos/nonprofit-success-ai/.claude--docs--plans--2026-10-07-r7-lifecycle-transition.md
  - data/raw/repos/nonprofit-success-ai/.claude--docs--plans--2026-10-07-r11-hardening-ci.md
---

# Single-Writer Transition Command

A stage-gated record (an engagement moving through intake → meeting → budget → ethics →
scoping → …) starts out with many writers. The portal updates rows directly, triggers
enforce some rules, and handlers enforce others. The [[Principal Write-Surface Matrix]]
audit found that a tenant could approve its own lifecycle transition. The fix in
nonprofit-success-ai was a single transition command.

## Mechanism

- **A definer function plus the caller's JWT, never the service role.** The API layer
  holds no service-role key. The function is `SECURITY DEFINER` with a pinned
  `search_path`. It reads role and org membership itself. Execute is revoked from
  `public`, `anon` and `service_role`, and granted only to `authenticated`.
- **Atomic in one transaction:** derive the current stage, authorise, evaluate the guard
  for the target stage, then write:
  - the stage rows;
  - an event row;
  - an audit row;
  - an approvals row for the highest-risk tier.
- **Idempotency lives on the events table.** It is a nullable `idempotency_key` with a
  partial unique index. A replay returns the original result with `replayed: true`, so no
  new table is needed.
- **Guards return named conditions.** SQLSTATEs map to HTTP: 42501→403, P0002→404,
  55000→422 `{error:'guard_unmet', condition}`, 22023→`stage_skipped`. The handler
  pre-checks only the structural guards, so a 422 names the unmet condition before any write.
- **Guards that cannot be checked yet are attested, not skipped.** If a guard's source table
  does not exist, the call must carry a non-empty reason and the event records
  `guard_deferred: '<name>'`. The attestation branch has a named deletion trigger: the
  feature that creates the table removes it.
- **One derive rule, two runtimes, pinned together.** The "current stage" rule is a pure TS
  function and a SQL function. Vitest and pgTAP both pin the same edge case ("no row in
  progress → furthest completed"), so the two cannot drift apart.
- **Trigger bypass by transaction-local GUC.** Reversals need a transition the enforcement
  trigger normally forbids. The function sets `set_config('app.lifecycle_transition','on',
  true)` and the trigger allows the move only under that flag.

## Ship it as two PRs, and say where the hole is

PR 1 is additive: function, idempotency column and handler. PR 2 revokes direct UPDATE from
the tenant role. **Until PR 2 lands, the GUC bypass is open to anyone with UPDATE**, because
a tenant can set the same setting. The plan states this, and PR 2's pgTAP asserts it is
closed. After the revoke, the tenant's remaining legitimate writes (notes) become typed
event rows written through the same path.

Follow-up hardening (r11) applied the same rule to approvals. An RLS `with check` forces
`reviewer_id = auth.uid() and reviewed_at is not null`, so an approval names the reviewer
who made it. See [[Pin Client-Executable Functions With an Allow-List]].

## See Also
- [[Principal Write-Surface Matrix]] — extends
- [[Written-but-Inert RLS Policies]] — extends
- [[Named-Trigger Deferral]] — instance-of
- [[Pin Client-Executable Functions With an Allow-List]] — extends
- [[Four-Source Provenance Contract]] — prerequisite-for
