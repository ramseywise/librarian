---
title: Expected-Failure Tests Pass for Any Throw
tags: [eval, pattern]
summary: "A known-bug trip-wire written as `it.fails(...)` goes green when *anything* in the test throws, including a broken seed in a hook. One regression test passed because its fixture insert failed, not because the bug reproduced. Assert today's buggy behaviour with a plain `it(...)` instead: fixing the bug still turns it red, and a setup failure stays loud."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis24-ingestion-integration-harness.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis24-ingestion-integration-harness.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis24-ingestion-integration-harness.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-03-dis24-ingestion-integration-harness.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-03-dis24-ingestion-integration-harness.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-03-dis24-ingestion-integration-harness.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-03-dis24-ingestion-integration-harness.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-03-dis24-ingestion-integration-harness.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-03-dis24-ingestion-integration-harness.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-03-dis24-ingestion-integration-harness.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis24-ingestion-integration-harness.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis24-ingestion-integration-harness.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis24-ingestion-integration-harness.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis24-ingestion-integration-harness.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-15-dis266-environment-target-a1.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-15-dis266-environment-target-a1.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-15-dis266-environment-target-a1.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-15-dis266-environment-target-a1.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-15-dis266-environment-target-a1.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-07-dis43-rate-limiting.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-07-dis43-rate-limiting.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-07-dis43-rate-limiting.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-07-dis43-rate-limiting.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-07-dis43-rate-limiting.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-07-dis43-rate-limiting.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-07-dis43-rate-limiting.md
---

# Expected-Failure Tests Pass for Any Throw

From an integration-test harness for an ingestion write path (repo akira). A known merge
defect was meant to be reproduced, not fixed, so the plan pinned it with vitest's
`it.fails(...)`. The idea was that the test passes while the bug exists and goes red
once someone fixes it, reminding them to flip it.

## What went wrong

On the suite's first live run the test was green **for the wrong reason**. The seed
fixture inserted a value that a CHECK constraint rejected, so the test threw before it
reached the merge it was meant to exercise. `it.fails` inverts *any* failure. A thrown
setup error and a failed assertion on the bug look the same to it.

Moving the seed into `beforeEach` was proposed as the fix. Reproduction showed this does
not help: the runner sets the same failed state for a hook throw as for an assertion in
the test body, and `fails` flips on that state. The orchestrator suggested the hook fix
and the fixer proved it wrong, so trust the reproduction over the instruction.

## The fix

Write a plain `it(...)` that **asserts the current, buggy outcome directly**. For
example, assert that two occurrences on different dates merged into one row.

- Fixing the bug changes the outcome, so the test goes red. The trip-wire still works.
- A broken seed, a missing grant or a schema drift now fails the test loudly instead of
  passing it.
- Put the issue number in the test name so `grep -rn "#NN"` finds it even when the fix
  lands somewhere that never touches this file.

## General rule

An inverted assertion (`fails`, `xfail`, "expect this to throw") only carries signal if
the *specific* failure is checked. Either match the error type or message, or assert the
observable bad state positively. An inverted test that cannot tell "the bug happened" from
"nothing ran" is a silent no-op, the test-level version of [[Silence Reads as Clean]].

## The same hole in refusal tests (akira reviews, 2026-09)

A guard's refusal test written as `await expect(run()).rejects.toThrow()`, with no message,
passes for any error, including a broken fixture. A "downstream was never called" assertion
is vacuous when the fake would have produced nothing to call it with anyway, for example a
client that returns zero sources. Assert the refusal message, and assert on a call that the
fake *would* have made without the guard. Then prove it by commenting out the guard and
watching every refusal case go red. The rate-limit version of the same weakness, where
`.not.toBe(429)` is satisfied by a 500, is in [[Red-Then-Green Proof for Fix-Stage Tests]].

## See Also
- [[Red-Then-Green Proof for Fix-Stage Tests]] — related (prove a test detects the defect, not just that it goes red)
- [[Silence Reads as Clean]] — instance-of (an inverted test that passes on any throw)
- [[Live-Database Test Harness Hazards]] — related (the harness review where this surfaced)
- [[Always-Red Check Carries No Signal]] — alternative-to (the mirror failure: a check that can never go green)
- [[Behaviour-Preserving Test Suite Split]] — related (a property model proven load-bearing by a deliberately wrong expectation)
