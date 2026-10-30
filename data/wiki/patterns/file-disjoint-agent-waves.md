---
title: File-Disjoint Agent Waves in One Working Tree
tags: [infra, llm, pattern]
summary: To fan a multi-finding fix out to parallel subagents under a stage-only rule, fix the interface contracts first (as optional props so the app type-checks before wiring), give each agent an exclusive file list per wave, keep shared manifests single-owner, run in the main tree rather than worktrees, run the touch-everything refactor alone and last, and review against the finding list rather than the agents' reports.
updated: 2026-10-30
sources:
  - data/raw/repos/librarian/.claude--docs--plans--2026-10-30-frontend-audit-fixes.md
---

# File-Disjoint Agent Waves in One Working Tree

From the plan for fixing a frontend audit of the librarian graph UI: about 35 findings
across graph, courses, chat, backend, CI and styling, executed by parallel subagents. The
plan's shape answers one question: how do several agents edit one codebase at once
without colliding, when none of them may commit?

## The waves

| Wave | Who | What |
|---|---|---|
| 0, foundations | orchestrator, serial | the shared modules every agent depends on, test runner, CI job, type changes for the contracts; gate green, then stage |
| 1, parallel | four subagents | each owns an exclusive file list (graph, courses, chat, backend) |
| 2, integration | orchestrator | wires the new props in the app shell; adds end-to-end smokes |
| 3, refactor | one subagent, alone | styling touches every component, so it runs after everything else, with the Wave 2 smokes and screenshots at three widths as its regression gate |
| 4, review | reviewers | high-effort code review, then an independent reviewer |

## Rules that make it work

- **Contracts are fixed before the fan-out.** Payload shape, the shared colour module and
  the new component props are decided in Wave 0, so the parallel agents agree without
  talking.
- **New props are optional.** Nobody edits the app shell in Wave 1. Because the added
  props are optional, the app type-checks after every agent's change and before Wave 2
  wires them.
- **Exclusive files per wave.** Each agent's brief lists the files it may edit. A shared
  manifest such as `package.json` gets exactly one owner. Any other agent that needs a
  dependency reports it instead of adding it.
- **Main tree, not worktrees.** The file lists are disjoint, so isolation buys nothing.
  Under a stage-only rule, worktrees would also leave uncommitted diffs stranded in
  separate checkouts with no easy way to bring them back. This is the opposite call from
  [[Parallel Across Lanes, Migrations Alone]], where each build ends in its own commit.
- **Defaults for open decisions are written into the plan.** Each of seven decisions has
  a default that agents use if no answer is recorded, so a missing answer cannot stall a
  wave.
- **Review the findings, not the reports.** The independent reviewer gets the diff and
  the plan's finding list, not the agents' own summaries, and checks that each finding is
  actually closed ([[Orchestrator Verifies, Never Relays]]). The success criteria require
  every finding ID to be closed or explicitly deferred with a reason.
- **Hand over a commit split.** The orchestrator stages everything and proposes a
  per-area commit split; the human commits.

## See Also
- [[Parallel Across Lanes, Migrations Alone]] — alternative-to (worktree-per-build when each build commits)
- [[Orchestrator Verifies, Never Relays]] — extends
- [[Librarian Graph Explorer]]
- [[Worktree Agent Dispatch Contract]] — alternative-to
- [[Scoped Phase Dispatch with Pre-Resolved Files]] — extends
- [[Harness Orchestration]] — instance-of
