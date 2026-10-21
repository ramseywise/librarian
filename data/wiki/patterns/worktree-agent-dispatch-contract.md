---
title: Worktree Agent Dispatch Contract
tags: [llm, pattern]
summary: "Rules for dispatching coding agents into git worktrees: the dispatcher owns the git workflow, the worktree is created in the target repo, agents branch from committed state, and their commits are provisional until a human reviews the diff."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/_user/CLAUDE.md
---

# Worktree Agent Dispatch Contract

A worktree looks like a sandbox, but it only isolates what the agent actually writes inside
it. Each failure below came from treating the worktree as a stronger boundary than it is.
The fix is a split of duties: **the parent session (dispatcher) owns the git workflow; the
agent only does the work.**

## The four rules

1. **Branch from committed state.** A worktree is created from a commit, not from the
   dispatcher's working tree. Uncommitted moves and renames are invisible to it, so the
   agent works against a stale directory layout. Commit structural changes *before*
   spawning worktree agents.
2. **Create the worktree in the target repo.** Agents follow the repo path written in
   their prompt. A worktree in repo A does not sandbox writes to repo B: the agent edits
   B's live checkout. In one recorded incident this committed a staged diff in the wrong
   checkout. Use `git -C <target-repo> worktree add ...`, or dispatch from a session whose
   repo *is* the target.
3. **The dispatcher creates the branch, with `--no-track`.** `git checkout -b NAME
   origin/main` quietly sets upstream tracking to `main`, which breaks the later push
   flow. The dispatcher creates the issue and the branch, then passes into the prompt the
   branch name, the commit-message format, and a `git fetch origin main && git rebase
   origin/main` step before the first commit. If the rebase conflicts, the agent reports
   and stops. It never forces or skips.
4. **Agent commits are provisional.** The worktree is cleaned up when the agent finishes,
   and staged-only changes are destroyed with it. So a worktree agent must commit as its
   last step: never merge, never push. That makes it the *only* exception to a no-agent-
   commit gate. Afterwards the dispatcher by default soft-resets the branch to staged
   (`git reset --soft origin/main`) so a human reviews the whole diff and makes the real
   commits, or keeps the agent's commits after review. The human ships. The agent never
   pushes.

## Why the split matters

Git state (issue, branch, upstream, rebase base) is cross-cutting, and an agent dispatched
with a narrow task has no reason to get it right. Keeping it with the dispatcher makes
mistakes visible in one place. The provisional commit settles the conflict between "the
agent must persist its work" and "a human must author the history" without loosening the
gate for regular sessions.

## See Also
- [[Parallel Across Lanes, Migrations Alone]] — extends (which agents can run concurrently once dispatch is safe)
- [[Re-Scope Over Sequence for Colliding Issues]] — related (cutting the work so concurrent agents share no files)
- [[TDD as Coding-Agent Harness]] — related (same separation-of-powers instinct, applied to tests)
- [[Claude Workflow System]] — part-of
- [[Plan Step Done Requires a Commit]] — related (the gate added after worktree cleanup destroyed uncommitted steps)
