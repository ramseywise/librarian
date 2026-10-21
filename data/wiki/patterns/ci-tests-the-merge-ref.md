---
title: CI Tests the Merge Ref, Not the Branch Tip
tags: [infra, pattern]
summary: "PR CI builds the merge commit (main ∪ branch), so a default changed on main underneath a branch can turn it red in CI while it stays green locally; reproduce against the merge ref, collapse N failing legs to their one root cause, and check that the fix targets the right tool (a formatter does not fix a lint rule)."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/ai-project-template/docs/reviews/AIT-43-review.md
  - data/raw/repos/ai-project-template/.claude--docs--reviews--AIT-43-review.md
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-08-01-49-llm-starter-kit.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-08-01-49-llm-starter-kit.md
---

# CI Tests the Merge Ref, Not the Branch Tip

A PR wiring four modules into a rendered LangGraph agent was green locally and failed 13
of 27 CI legs with ruff `I001` (unsorted imports). The branch had not changed anything
about import order.

## What actually happened

- Another PR had just merged to main, changing the template's **default render** from a
  flat layout (`py_project_root = "."`) to a `backend/` layout.
- PR CI tests the **merge commit** of main and the branch, so CI rendered `backend/`.
  The branch tip alone still rendered `.`. Locally: clean. In CI: red.
- Ruff's `known-first-party` pinned only two packages; the others were classified by
  src-based resolution, which succeeds when the project root is `.` and fails when it is
  a real directory — demoting them to third-party and demanding a different import
  grouping (the layout-dependent half of this is in [[Execute Every Toggle Configuration]]).
- A previous fix attempt ran `ruff format`. `I001` is a **lint** rule, not a formatter
  rule; formatting does not sort imports. The attempt was aimed at the wrong tool and
  changed nothing.

The fix was one config line: pin every package under the source root as first-party, so
import order is layout-invariant. Verified by rendering five configs against the merge
ref (both layouts, before and after), plus the full test run.

## The pattern

1. **Reproduce against the merge ref**, not the branch tip, when CI and local disagree.
   `git rev-list --left-right --count origin/main...HEAD` showing the branch behind main
   is the first clue that main moved underneath it.
2. **Collapse legs to root causes.** Thirteen red legs were one cause; main itself was red
   on only one leg, so the other twelve were branch-introduced *in combination with* main.
3. **Check the fix's tool matches the failure's rule.** Formatter vs linter, unit vs
   integration — a fix aimed at the neighbouring tool reads as an attempt and changes
   nothing.
4. **Rebase before claiming the fix.** A fix is only provably correct post-merge; confirm
   the edited file is identical between branch and main so the rebase cannot conflict.

## The same trap in audits

A planning pass found that an audit said "the agent emits no token-usage spans" while the
code plainly wired them. Both were right: the audit had read `origin/main`, and the wiring
lived on a branch that was still unmerged. The plan recorded the verdict per tree and turned
it into a sequencing constraint (branch from the unmerged work, or land the independent part
first). Before trusting an audit, review, or CI verdict, name the ref it read; a disagreement
between audit and code is first a question of *which tree*, not of who is right.

## See Also
- [[Execute Every Toggle Configuration]] — extends (a default change is a configuration change)
- [[Verify CI Steps by Extraction, Not Retyping]] — related (run the real CI command, not a retyped one)
- [[Verify Merge State by Content, Not Label]] — related (the same review's bookkeeping findings)
- [[Test Derived Defaults Without Overrides]] — related (a derived default that flipped every render)
