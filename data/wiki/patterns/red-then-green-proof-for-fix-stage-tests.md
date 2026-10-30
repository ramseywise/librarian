---
title: Red-Then-Green Proof for Fix-Stage Tests
tags: [llm, eval, pattern]
summary: When a fix's job is to make a test guard something, the agent must show the test failing against the old code before showing it passing against the new — because a weak assertion (`expect(status).not.toBe(429)`) is satisfied by a 500 and would have passed before the fix too.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/playground/agents/build-scout.md
  - data/raw/claude-docs/akira/agents/build-scout.md
  - data/raw/claude-docs/kiez-archive/agents/build-scout.md
  - data/raw/claude-docs/diskoe/agents/build-scout.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-02-dis53-layouts.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-02-dis53-layouts.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-02-dis53-layouts.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-02-dis53-layouts.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-02-dis53-layouts.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-02-dis53-layouts.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-02-dis53-layouts.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-02-dis53-layouts.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-02-dis53-layouts.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-02-dis53-layouts.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-02-dis53-layouts.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-02-dis53-layouts.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-02-dis53-layouts.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-02-dis53-layouts.md
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
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis37-replay-corpus.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis37-replay-corpus.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis37-replay-corpus.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis37-replay-corpus.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis37-replay-corpus.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis37-replay-corpus.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis37-replay-corpus.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis43-anonymous-rate-limiting.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis43-anonymous-rate-limiting.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis43-anonymous-rate-limiting.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis43-anonymous-rate-limiting.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis43-anonymous-rate-limiting.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis43-anonymous-rate-limiting.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis43-anonymous-rate-limiting.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis46-restore-drill.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis46-restore-drill.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis46-restore-drill.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis46-restore-drill.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis46-restore-drill.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis46-restore-drill.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis46-restore-drill.md
---

# Red-Then-Green Proof for Fix-Stage Tests

A rule in the akira build-agent definition for the fix round that follows review.

## The rule

If a review finding says *"this path is unguarded"* and the fix adds a test, the fix is
not done when the test is green. It is done when the agent has shown:

1. the test **red** against the pre-fix code (stash the fix, run, record the failure), then
2. the test **green** with the fix applied.

Both outputs go in the report. A green-only report is rejected.

## Why green alone proves nothing

The motivating case: a finding asked for a guard against rate-limit responses. The fix
added `expect(res.status).not.toBe(429)`. The test passed — and would have passed
before the fix, because the endpoint returned 500. The assertion did not describe the
guarded behaviour; it described one thing the behaviour was not. Red-then-green would
have caught it in seconds: the test could not be made red against the old code, so it
was not testing the change.

This is the agent-shaped version of the TDD discipline in [[TDD as Coding-Agent Harness]]:
the failing test is the only proof that the test constrains anything. The extra
constraint here is that it applies at fix time, when the temptation is to write the
assertion that passes rather than the one that fails first.

Two further cases from the same review record, both green on the unfixed code: a
schema-shape test that asserted 5 of 15 columns while the defect sat in the other ten, and
a four-test fix of which two tests passed before the fix was applied. In each the review
round found it later, at the cost of a full round, when the red observation would have
cost one command. The red run must also fail *for the right reason* — the assertion
message should name the defect, not a setup error.

## The same proof for gates and guards (akira, 2026-09)

Three later review rounds applied the rule beyond unit tests:

- **A guard calibrated to pass.** A grep-count regression guard asserted `toBe(3)` because
  it counted the one real layout, a component test, and its own source. It asserted
  whatever was true, not the invariant ("exactly one"). Scoped to production code it
  asserts 1 — and a guard nobody has watched fail is not yet a guard, so the structural
  replacement was proven by mutation (move a route in → fails; out → fails; restore →
  green). See [[Layout Membership by Location]].
- **A check proven to fail for the wrong reason.** A new drift layer was "verified" by
  showing it went red when its own RPC was missing — proof that it fails when it cannot
  run, not that it detects the defect. Closed by planting the defect: a scratch table with
  RLS off was reported, then flipped when RLS was enabled. See
  [[Unfinished Work Must Fail Closed]].
- **An integration test proven by reverting the fix.** The regression test for a
  wrong-client bug was run with the fix reverted, failed, and was restored green — the
  only evidence it exercised the real code path rather than a mock. See
  [[Audit the Class, Not the Instance]].
- **Three more plans from the same 2026-09-07 fix wave** did it routinely. A retention
  archive's pre-fix SQL body was installed on the local database outside git, and one run
  turned two tests red at once. A rate limiter's eviction sweep call was deleted, and the
  eviction test went red while the two tests that don't need eviction stayed green, which
  proves the test is aimed precisely. A CLI's exit-code ternary was inverted, and both wiring
  tests went red. See [[Atomic Archive-Then-Delete for Irreversible Retention]] and
  [[Rate-Limit Keying: Identity Over IP]].

## See Also
- [[TDD as Coding-Agent Harness]] — instance-of (the same guardrail applied to the review-fix round)
- [[Scoped Phase Dispatch with Pre-Resolved Files]] — complements (same agent definition)
- [[Verification Loops]] — extends (a verification step the agent cannot satisfy by weakening the check)
- [[Always-Red Check Carries No Signal]] — related (the mirror failure: a check that cannot go green)
- [[Review Reporter Ground Rules]] — extends
- [[Layout Membership by Location]] — instance-of (structural guard proven by mutation in both directions)
- [[Unfinished Work Must Fail Closed]] — related (prove the check detects, not just that it fails when its dependency is missing)
- [[Audit the Class, Not the Instance]] — instance-of (integration test proven by reverting the fix)
- [[Atomic Archive-Then-Delete for Irreversible Retention]] — instance-of (pre-fix SQL body installed locally to prove two archive tests)
- [[Expected-Failure Tests Pass for Any Throw]] — related (an inverted trip-wire test that went green on a setup error)
- [[Behaviour-Preserving Test Suite Split]] — instance-of (a stateful property model shipped with a mutant expectation that must fail)
- [[Green Lint Proves Absence, Not That the Rule Fires]] — instance-of (red-then-green applied to lint rules)
- [[Render-Scoped Component Types Remount Their Subtree]] (a fix planned repro-test-first)
