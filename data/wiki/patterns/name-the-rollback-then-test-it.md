---
title: Name the Rollback, Then Test It
tags: [patterns, eval, pattern]
summary: "An optimistic UI update whose undo lives inside an anonymous `catch` has no seam to test, so its rollback ships unasserted. Extract each mutation into a hook with named `applyOptimistic`/`rollback` functions, write the rollback tests before the wiring, gate the refactor on existing tests passing with unchanged assertion bodies, and leave freshly-touched, entangled state where it is."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-19-dis328-venuereviewmap-split.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-19-dis328-venuereviewmap-split.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-19-dis328-venuereviewmap-split.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-19-dis328-venuereviewmap-split.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-19-dis328-venuereviewmap-split.md
---

# Name the Rollback, Then Test It

An operator review map in akira had grown to 1,562 lines, 309 more than when its issue was
filed. One component held map lifecycle, search, filters, candidate creation, corrections,
review writes and all of the presentation. Its 21 tests covered the happy path of every
mutation and asserted **zero rollback behaviour**. Each mutation did an optimistic update
inside a `try`, with the undo written inline in the matching `catch`. The only way to test
an undo was to render the whole component, make `fetch` reject, and read the DOM.

## The finding that set the priority

The research concluded that the sharpest gap was the untested rollback, not the line count.
Session 1's main deliverable was therefore making rollback independently testable, with
tests that would fail against the old structure. Line count came second.

## The mechanism

1. **Group state by owner, not by declaration order.** A state-ownership map sorted 26
   `useState`s into four owners: the map adapter, filter/search state, selection state, and
   one hook per mutation. Derived state that reads several hooks (a merged candidate list) is
   composed in the component, so each hook stays testable without knowing about the others.
2. **Per-mutation hooks with named halves.** Each hook exports `applyOptimistic` and
   `rollback` as separate functions around the fetch, instead of two anonymous `setState`
   calls in one `try/catch`. Tests call `rollback` directly, plus the hook-level cases:
   applied before the fetch resolves, rolled back on POST failure, rolled back to undefined
   on DELETE failure, no rollback on success.
3. **Additive session first.** Session 1 added only new files, imported by nothing. Its
   rollback is deleting one directory. Session 2 did the wiring as one revertible commit.
4. **Frozen-assertion regression gate.** The existing 21 tests had to stay green **with no
   assertion body changed**. Tests that assert byte-exact request bodies make any payload
   drift a real regression, not a test to fix.
5. **Share only what is truly shared.** Only the map-lifecycle adapter was shared with a
   sibling component. It removed about 200 duplicated lines and made the sibling 25%
   smaller. Venue-only filters stayed venue-only, rather than producing a shared hook
   bloated with options.

## Leave fresh entanglement alone

Selection state was **deliberately not extracted**. `git log` showed it was the most
recently touched part of the file, added the day before the issue. It was guarded by a
regression test for a real bug in which two effects raced over the same map handle and one
stomped the other's `fitBounds`. The adapter's new imperative handle opened a fresh seam for
exactly that race. The rule: entanglement that is live, not stale, waits until the simpler
extractions have been proven stable for a review cycle.

## Traps hit during execution

- **Hook return replacing a ref.** A `useRef` is declared at the top of the component. Once
  the ref came from a hook return, it was in scope only below that hook call, and it was
  already listed in a `useMemo` dependency array *above* the call, so it was read before
  initialisation. All 21 tests crashed. The fix was to move the hook call above its first
  consumer.
- **`vi.mock` hoisting.** A factory that references an imported identifier throws
  "Cannot access before initialization". Use a dynamic `import()` inside the factory.
- **Two fakes kept on purpose.** One test fake fires `load` on registration and another does
  not, because one test asserts the not-ready state. Unifying them would need an
  out-of-band config channel the real code never passes.
- **Report Done-when items you cannot meet.** The ~400-line target was not reachable without
  splitting the presentation, which none of the steps described and which carried
  visual-regression risk with no visual test. It was reported as a decision to fund, not
  improvised.

## See Also
- [[Degrade the Render, Surface the Failure]] — extends (what the UI should show when the mutation fails)
- [[Mocked-Away Body Hides the Defect]] — extends (why the catch branch went unasserted)
- [[Readiness Is Pinned to a Tree State]] — extends (the plan assumed a filter hook Session 1 never created)
