---
title: Plan Step Done Requires a Commit
tags: [eval, pattern]
summary: "An agent's 'Status: DONE' on a plan step is a claim, not evidence. Before the plan is closed, a deterministic gate parses the plan's steps and declared files and checks git log for a commit touching each step's files (verified / partial / missing). This was the fix after a plan was marked DONE with 7 of 9 steps never committed."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-23-GUA-23-review-backbone.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-23-GUA-23-review-backbone.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-23-review-agent-system-research.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-23-review-agent-system-research.md
---

# Plan Step Done Requires a Commit

## The incident

An execute skill set a plan's `Status: DONE` after dispatching steps to worktree agents.
On review of the resulting PR, **7 of 9 steps had never been committed**. Each worktree
agent's work had been destroyed when its worktree was cleaned up. Nothing in the pipeline
checked that a step marked done had left any trace in git. The status line was produced by
the same LLM context that believed the work had happened. The reviewer was a separate
reader, and it caught the gap only because it read the diff.

## The gate

A deterministic subcommand (`verify-commits`) in the review CLI runs before execute
may mark a plan DONE:

1. Parse the plan markdown for steps: the `#### Step N:` heading, the `**Files**:` list,
   and the `✓ DONE` marker.
2. For each step marked done, run `git log --oneline --all --diff-filter=ACDMR -- <files>`.
3. Emit one row per step with status **verified** (every file touched by some commit),
   **partial** (some files have no commit), or **missing** (none do), plus the matching
   commits and missing files.

Execute calls it as a post-execution gate. Review calls it as a plan-fidelity check. It is
the part of plan fidelity that can be moved out of the prompt. "Did a commit touch the
files this step promised?" is a git question, not a judgment call, which is why it belongs
in a [[Deterministic Review Substrate]] rather than in prose instructions.

## Limits

- **It checks presence, not correctness.** A commit touching the right file proves
  something happened there. It does not prove the step was done right.
- **Fragile to plan-format drift.** The parser depends on the exact heading and marker
  syntax. The mitigation is to keep that format in the plan skill's template and point the
  parser at the spec. A plan written freehand silently yields zero steps, and a zero-step
  result must not read as "all verified".
- `--all` searches every ref, so a commit on an unrelated branch can satisfy a step.
  Scope the search to the branch's range when that matters.

## Why it matters beyond one incident

The same incident became **eval fixture zero** for the review system. A PR with a full
manual review and known ground truth (4 blockers) is used to measure whether automated
review would have caught it. The general rule: **completion claims from agents get a
mechanical check against the system of record before they change state.** The deployment
version of this rule is [[Migration Done Means Pushed and Probed]].

## See Also
- [[Worktree Agent Dispatch Contract]] — extends (worktree cleanup destroying uncommitted work was the root cause)
- [[Deterministic Review Substrate]] — instance-of (verify-commits is one of its deterministic stages)
- [[Migration Done Means Pushed and Probed]] — related (done-means-verified for deploys)
- [[Plan-Doc Status Enum]] — related (the status field this gate guards)
