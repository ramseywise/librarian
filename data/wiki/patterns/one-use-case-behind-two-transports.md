---
title: One Use Case Behind Two Transports
tags: [patterns, infra, pattern]
summary: "When an HTTP route and a Server Action each implement the same command, they drift and each one inherits the same non-atomic write. Put the business rules in one transport-neutral use case, make each multi-row command a single service-role-only transactional RPC with replacement semantics and typed error codes, and keep only parsing, rate limits, cookies and response mapping in the adapters."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis305-poll-transactional-use-cases.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis305-poll-transactional-use-cases.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis305-poll-transactional-use-cases.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis305-poll-transactional-use-cases.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis305-poll-transactional-use-cases.md
---

# One Use Case Behind Two Transports

From an akira plan for group polls in a Next.js and Supabase app. The poll commands were
exposed twice, once as HTTP routes and once as Server Actions. An earlier decision had kept
the two adapters "independent, not delegated", so neither called the other.

## The two atomicity defects

- **Poll creation made two requests**: insert the poll, then insert its options. If the
  second request failed, the poll was left orphaned.
- **Ballot submission looped over one upsert per option.** A failure mid-loop left a
  partial ballot. Both adapters had their own copy of the loop, so both had the defect.

## The fix

1. **One transactional RPC per command.** `create_poll_with_options` and
   `submit_poll_ballot` each run as a single function body, which is a single transaction.
   Ballot submission locks the poll row (`for update`). It checks open status and deadline,
   exact option coverage, no duplicate option ids, option membership in this poll, and the
   choice vocabulary, all **before** deleting or upserting anything.
2. **Replace the whole ballot.** Both adapters already required a vote for every option on
   each submission. Replacing the complete ballot keeps that contract and also removes stale
   choices if the option set changes.
3. **Use an existing foreign key as the existence check.** Pre-checking that an event exists
   in SQL was dropped. The existing FK on the options table already rejects a missing event
   and rolls back the poll insert with it.
4. **Lock down the grants.** The functions are `security invoker`, with an empty
   `search_path` and schema-qualified names. EXECUTE is revoked from public, anon and
   authenticated and granted only to `service_role`, the only caller. This matches the
   project's other migrations.
5. **Typed error codes across the seam.** The store raises `CreatePollError` and
   `SubmitBallotError` with stable codes (`poll_not_open`, `ballot_incomplete`,
   `ballot_option_not_in_poll`, …). The use case maps these to domain results. Anything
   else is rethrown so the calling adapter logs and translates it.
6. **A transport-neutral use-case module.** Create and ballot validation, poll-state checks
   and typed results live in one `useCases.ts`. Adapters keep request and FormData parsing,
   rate limiting, cookie issuance, logging and HTTP or UI-state mapping. Done means the same
   inputs through either adapter produce the same domain result.

## Superseding a decision only where it was wrong

The earlier "independent adapters" decision was not reversed. It was **narrowed**. The two
transports still do not call each other, which was the point of the decision. Only the
business rules moved into the shared layer. The refinement was recorded in the design
requirements so that the old decision is not cited later as a reason to duplicate rules.

## Notes

- Changing the store's interface from `submitVote` to `submitBallot` broke every caller
  that looped, every caller's mocks, and four sibling route tests that stubbed the whole
  store shape. A plan that lists only the store files has undercounted the change.
- Atomicity tests must exercise PostgreSQL itself. Forced option or vote failures must
  leave zero orphan rows and zero partial ballots, and cross-poll ids must fail. A mocked
  client cannot show a rollback.
- At the docs and gate step, the hosted push turned out to be already applied. The drift
  check ran its real comparison and was not skipped. The plan recorded this as found, not
  as done by the step.

## See Also
- [[Principal Write-Surface Matrix]] — related (who may call which write path)
- [[RLS On, No Policy for Server-Mediated Tables]] — related (the service-role-only posture these RPCs extend)
- [[Migration Done Means Pushed and Probed]] — related (push, probe grants, regenerate types)
- [[Live-Database Test Harness Hazards]] — related (the database-backed failure tests)
- [[Server Shell, Client Leaf]] — related (another Next.js seam that splits transport from logic)
- [[Edit In Place by Diffing on the Natural Key]] — extends (a third transactional RPC behind the same use-case split)
