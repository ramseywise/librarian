---
title: Mocked-Away Body Hides the Defect
tags: [eval, pattern]
summary: "A test that patches out the very function containing a bug never executes its body — a function-local import of a name that did not exist sat behind such a patch, and an unawaited coroutine sat on a fire-and-forget path no test reached — so mock one level below the unit under test, and treat rare-branch and background-task code as untested until something actually runs it."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/listen-wiseer/docs/plans/LIS-77-plan.md
  - data/raw/repos/listen-wiseer/.claude--docs--plans--LIS-77-plan.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-31-f1-component-test-harness.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-31-f1-component-test-harness.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-31-f1-component-test-harness.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-31-f1-component-test-harness.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-31-f1-component-test-harness.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-31-f1-component-test-harness.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-31-f1-component-test-harness.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-06-dis57-forms-server-actions.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-06-dis57-forms-server-actions.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-06-dis57-forms-server-actions.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-06-dis57-forms-server-actions.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-06-dis57-forms-server-actions.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-06-dis57-forms-server-actions.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-06-dis57-forms-server-actions.md
---

# Mocked-Away Body Hides the Defect

Two runtime bugs in listen-wiseer survived a green suite of ~470 unit tests and were found
only by a repo-wide review sweep. Both share a shape: **the code containing the defect was
never executed by any test, though tests nominally "covered" it.**

## Case 1 — the patched-away function

A synthesis helper did a function-local `from agent.graph_nodes import _llm`. No `_llm`
existed — the module exposed a lazy accessor `_get_llm()`. The import would raise
`ImportError` the first time the helper ran, which only happened when agentic search fanned
out to more than one sub-query. The multi-hit test patched the helper *itself*
(`patch("...web_search._synthesize")`), so its body — and the broken import — never ran.

**Fix:** a test that runs the helper for real and mocks only its dependency. Because the
import is function-local, the patch target must be the *defining* module
(`agent.graph_nodes._get_llm`); patching the name in the consuming module would not work,
since it is never bound at module scope. The new test was required to fail against the
pre-fix code and pass after ([[Red-Then-Green Proof for Fix-Stage Tests]]).

## Case 2 — the fire-and-forget path

The chat entry point passed `get_store()` — an `async def` — unawaited into a sync
fire-and-forget scheduler for a background prompt optimizer. The optimizer received a
coroutine object instead of a store. Nothing failed loudly: the work ran inside a detached
task, and the Chainlit handler had no unit test. Adding `await` at the call site was not
possible (the scheduler is sync); the fix reused the store already awaited once during graph
construction, cached as a module-level singleton beside the existing graph singleton. A
companion annotation bug typed the parameter as the dev-only `InMemoryStore` while production
supplied a Postgres store; widened to the `BaseStore` base class.

With no test harness for the entry point, the fix was verified statically — an AST/grep
assertion that no bare `get_store()` call remains plus a pyright run against a pre-change
baseline — rather than by building session scaffolding inside a bug-fix issue.

## Case 3 — component tests that never render (akira, 2026-08)

Six files named like component tests (`VoteForm.test.ts`, `EventDetail.test.ts`, an
`accessibility.test.ts`) imported only helper functions; none called `render()`, and the
config ran `.test.ts` in a node environment with no DOM library installed. They passed
because they never touched the view layer — the view layer had never been rendered in a
test. Building the real harness (a jsdom project beside the untouched node project)
surfaced two more ways a mock silently does not apply:

- **`vi.mock()` is hoisted only in the test file itself.** A shared helper module that
  calls `vi.mock()` is not hoisted, so importing it leaves the real module running. Each
  test file declares its own mock; the shared file is documentation of the stub shape.
- **`restoreAllMocks()` un-stubs module-factory mocks**, so hooks returned `undefined`;
  `clearAllMocks()` clears call history and keeps implementations.

## Rules

- **Mock one level below the unit under test**, never the unit itself. A patch on the
  function you claim to test makes the test a test of the caller.
- **Function-local imports are runtime code.** They are invisible to module import checks
  and to linting of the call site; only executing the function proves them.
- **Rare branches and detached tasks are untested by default.** A fan-out path gated on
  query complexity, or a `create_task` whose exceptions nobody awaits, needs an explicit test
  or an explicit static check — the suite's pass count says nothing about them
  ([[Silence Reads as Clean]]).
- **A test's file name is not evidence of what it exercises.** Check that a "component"
  test renders, and that a mock declared elsewhere is actually in effect.
- **Type the parameter at the interface the real producer returns**, not the dev
  implementation the tests happen to construct.

## See Also
- [[A Fake That Conforms to a Broken Seam]] — related (the double faithfully reproduces the break; here the double replaces the break)
- [[Red-Then-Green Proof for Fix-Stage Tests]] — prerequisite-for (how the regression test proved it reaches the defect)
- [[Silence Reads as Clean]] — instance-of (no error from a path that never ran)
- [[Listen-Wiseer Project]] — instance-of
- [[Name the Rollback, Then Test It]] — prerequisite-for (an optimistic rollback in an anonymous catch shipped unasserted)
