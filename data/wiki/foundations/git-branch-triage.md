---
title: Git Branch Triage
tags: [foundations, reference]
summary: "Deciding what to do with in-flight work before switching context — the branch health check that separates merged from unmerged commits, the WIP-branch-versus-stash choice, and reading a stash diff before trusting it."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/programming--git.md
---

# Git Branch Triage

The recurring question is not "how do I use git" but **"what is actually on this branch,
and is it safe to leave?"** — asked when switching context, cleaning up, or inheriting
someone else's work-in-progress.

## The branch health check

The single most useful command for triaging an unfamiliar branch:

```
git log --oneline origin/their-branch ^main
```

This lists commits on the branch that are **not** reachable from `main`. Empty output means
the branch is fully merged and safe to delete. Non-empty output is the exact set of work
that would be lost.

The reason this beats `git log origin/their-branch` is that the latter shows the branch's
whole history, most of which is shared with `main` — you cannot tell at a glance which
commits are unique. The `^main` exclusion is what makes the answer actionable.

`git branch --merged` answers a similar question more coarsely, but it only reports tip
reachability. A branch whose commits were **cherry-picked or squash-merged** into `main`
shows as unmerged because the commit SHAs differ, even though nothing would be lost. The
`--oneline ... ^main` form at least shows you *what* the unmerged commits are, so you can
recognise a squash-merge by its content.

## WIP branch vs. stash

Both park uncommitted work. The decision is about **how long and how visible**:

| | WIP branch | Stash |
|---|---|---|
| Visibility | Named, appears in `git branch` | Hidden in a stack |
| Lifetime | Days or longer | Hours |
| Survives | Everything | Easy to forget or drop |
| Cost | A commit you will amend or drop | None |

**The failure mode of stash is silence.** A stash does not appear in any status output you
routinely look at, is identified only by an index that shifts as you push more, and is
trivially lost by `git stash drop` or `git stash pop` into a conflicting tree. Work you
intend to return to *tomorrow* should be a branch with a real name.

The corollary: if you find yourself running `git stash list` to remember what you were
doing, that work should have been a branch.

## Read the stash before you trust it

```
git stash show -p stash@{0}
```

Show the patch before popping. Two things this catches:

- **The stash is not what you remember.** Stashes accumulate; the one you want may not be at index 0.
- **The stash conflicts with what you have since done.** Popping into a changed tree can
  produce conflicts inside a stash apply, which is a worse place to resolve them than a
  normal merge — the stash is partially applied and the entry may or may not be dropped.

By default `git stash` does **not** include untracked files. Work that consists of new files
— a new module, a new test file — stashes as *nothing*, and the stash appears to have
worked. Use `-u` when the work includes new files.

## Files that predict conflict

Some paths conflict on nearly every parallel branch because they are append-heavy and
machine-ordered:

- Lockfiles (`package-lock.json`, `uv.lock`, `poetry.lock`)
- Migration directories with sequential numbering
- Generated indexes and barrel files
- Changelogs

The general shape: **a file conflicts when its content is ordered by time rather than by
meaning.** Two branches both appending to the end will always collide. The resolution is
usually not to merge the text but to regenerate the artefact from its source — re-lock, or
renumber the migration — which is why textual conflict resolution on a lockfile is nearly
always wrong.

## See Also
- [[Data Science Curriculum Layers]] — complements (the programming-tooling layer beneath the curriculum)
- [[TypeScript any Escapes]] — complements (the other half of the day-to-day tooling reference)
