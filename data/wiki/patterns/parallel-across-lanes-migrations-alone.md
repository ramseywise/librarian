---
title: Parallel Across Lanes, Migrations Alone
tags: [infra, llm, pattern]
summary: When running several agent builds concurrently in worktrees, memory is not the constraint — declared dependencies, shared file lanes, and the single shared database are — so parallelise across lanes, serialise within a lane, run migration-adding builds alone, and cap concurrency at 3 for review attention.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/playground/skills/workflow-build/SKILL.md
  - data/raw/claude-docs/akira/skills/workflow-build/SKILL.md
  - data/raw/claude-docs/diskoe/skills/workflow-build/SKILL.md
  - data/raw/claude-docs/kiez-archive/skills/workflow-build/SKILL.md
  - data/raw/claude-docs/akira/skills/git-board/SKILL.md
  - data/raw/claude-docs/diskoe/skills/git-board/SKILL.md
  - data/raw/claude-docs/playground/skills/git-board/SKILL.md
  - data/raw/claude-docs/kiez-archive/skills/git-board/SKILL.md
---

# Parallel Across Lanes, Migrations Alone

akira's `/workflow-build` decides, before a wave of agent builds, which issues may run
concurrently in separate git worktrees.

## Memory is not the constraint

Measured on a 24 GB laptop: three concurrent test+build pairs peaked at 1.42 GB across 26
processes; disk was ~758 MB per worktree. Sequencing for machine resources was solving a
problem that did not exist.

## What actually constrains a wave

1. **Declared dependencies** — read the issue bodies, not the labels. A `ready` label does
   not mean unblocked; grep for `Depends on:` / `Blocks:` and confirm each named issue is
   closed.
2. **A shared lane** — issues editing the same tree serialise whether or not they declare
   it. Compute real overlap from the files each plan edits (`comm -12` on the sorted lists);
   a plan *naming* a file is not the same as editing it. Docs collide by guarantee, so doc
   edits stay additive in their own section.
3. **The database is global** — migrations and the drift check hit one remote. Two
   worktrees pushing migrations concurrently is the same failure class as three recorded
   drift incidents. **Never run two migration-adding builds at once.**

So: **parallel across lanes, sequential within a lane, migrations always alone.**

## Cap concurrency at 3

Not a machine limit — a review-attention and merge-conflict limit. Past three, findings
arrive faster than they can be judged.

## Worktree setup the repo cannot give

Gitignored files are missing in a fresh worktree. Do a real install (symlinking
`node_modules` made the bundler panic on an invalid symlink even though tests and lint
passed); symlink the env file so the drift check does not hard-fail; point agents at plan
docs in the main checkout by absolute path. Handoff is serial — one staged branch in the
main checkout — and each orchestrating session runs one fan-out, then ends; state lives in
the board, plans and telemetry, not the conversation.

## See Also
- [[Re-Scope Over Sequence for Colliding Issues]] — related (what to do when two "parallel" issues share files)
- [[Migration Done Means Pushed and Probed]] — related (the drift class concurrent migrations reproduce)
- [[Scoped Phase Dispatch with Pre-Resolved Files]] — related (the per-phase file list overlap is computed from)
- [[Worktree Agent Dispatch Contract]] — prerequisite-for (git-side rules for dispatching the concurrent agents)
- [[File-Disjoint Agent Waves in One Working Tree]] — alternative-to (disjoint file ownership in one tree instead of lanes)
