---
title: Behaviour-Preserving Test Suite Split
tags: [eval, pattern]
summary: "To split an oversized test suite without losing coverage, use the existing describe blocks as seams, move shared fakes into one sibling fixtures module, and hold the runner-reported test count per subsystem as the preservation contract (it.each expansion makes a grep count wrong); a stateful property model added in the same pass needs a deliberately wrong expectation that must fail, or it can be vacuously green."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dsk-303-split-oversized-test-suites.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dsk-303-split-oversized-test-suites.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dsk-303-split-oversized-test-suites.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dsk-303-split-oversized-test-suites.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dsk-303-split-oversized-test-suites.md
---

# Behaviour-Preserving Test Suite Split

From an akira refactor (2026-09-16, executed 2026-09-18) that split five test suites of
790 to 1,302 lines without changing production code. Each subsystem went in its own
session and PR.

## The contract is the count, measured by the runner

- **Baseline per subsystem, from the runner.** The plan's numbers came from counting
  `it(` in each file, and two of them were wrong. In one suite, 51 `it` calls plus two
  `it.each` groups ran as **57** tests. In another, a surface-mapping table made 67 into
  71. Run the original file alone first and record the count the runner reports, then
  require the same count after the split. A smaller count is a regression even when the
  run is green.
- **Use the describe blocks as seams.** Assign each top-level `describe` to exactly one
  new file. Where the plan's line ranges overlapped or contradicted each other, the
  executor followed the intent (every block placed exactly once), not the literal ranges.
- **One sibling fixtures module per subsystem.** Shared builders and in-memory fakes move
  into `<suite>.fixtures.ts` and every split file imports them. Copying a mutable fake
  into several files would let them drift apart. Builders return valid defaults and take
  typed overrides. Consolidating fixtures across the whole repo was out of scope.
- **Run every new file alone as well as together.** Hidden reliance on shared mutation or
  file order only shows when a file runs alone. A file that needs no module mock after
  the split should be shown green without one.
- **No production edits.** If a group cannot be separated without changing production
  code, record why and keep it together.
- **Sequence around open PRs.** One suite's production file was being changed by an open
  PR. That session went last, as a per-session constraint, without blocking the other four.
- **Sweep stale path references** to the deleted monolith files in comments and docs.

## A property model has to prove it is load-bearing

The one net-new test was a `fast-check` stateful model of a batch job lifecycle (poll,
collect, retry, terminal states). Preconditions gate each command to the states the real
code allows, and postconditions compare the fake store with the model after every
command, over 200 runs. Two lessons:

- **Ship a mutant check with it.** A second, permanent test gives the model a deliberately
  wrong expectation (a dead job's item "stays pending" instead of being released) and
  asserts that `fc.assert` rejects it. Without that, a model whose preconditions never
  fire is green for nothing. See [[Red-Then-Green Proof for Fix-Stage Tests]].
- **The first counterexample is often the model's fault.** fast-check immediately found
  `[PollCompleted, CollectFailed, RetryFailed, RetryFailed]`. A second retry of the same
  item is a real no-op in the code, and an example test already covered it, but the model
  did not know. The fix was a `retried` flag and a separate repeat-retry command, not a
  production change. Check the shrunk sequence against the existing examples before
  calling it a defect.

The library was installed as an exact-pinned dev dependency, scoped to the one suite with
real lifecycle sequences. Example tests stayed for edge-specific diagnostics.

## See Also
- [[Expected-Failure Tests Pass for Any Throw]] — related (another test that can be green without exercising its subject)
- [[Red-Then-Green Proof for Fix-Stage Tests]] — extends (the mutant check is the same proof applied to a property model)
- [[Scan-Floor Guard Against Silent No-Op Checks]] — related (a count floor as the guard against silently shrinking coverage)
- [[Mutation Score Artifact from Zero-Test Runs]] — related (a green score from tests that never ran)
