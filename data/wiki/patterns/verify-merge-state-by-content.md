---
title: Verify Merge State by Content, Not Label
tags: [infra, pattern]
summary: "Issue labels, commit messages, branch names and 'ahead N' counts are caches of repo state that go stale independently of it — a review decides what landed by grepping main for the change itself, and treats a branch stacked on unmerged work, or a behaviour change under a docs-shaped message, as a traceability defect even when the code is fine."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/ai-project-template/docs/reviews/AIT-43-review.md
  - data/raw/repos/ai-project-template/.claude--docs--reviews--AIT-43-review.md
  - data/raw/claude-docs/ai-project-template/docs/reviews/AIT-34-review.md
  - data/raw/repos/ai-project-template/.claude--docs--reviews--AIT-34-review.md
---

# Verify Merge State by Content, Not Label

Two template-repo reviews found that almost every bookkeeping signal disagreed with the
code on main.

## The caches and how each lied

| Signal | What it claimed | What content showed |
|---|---|---|
| Issue labels | five live `in-progress` issues | two merged, one fully discharged by another; one actually live |
| Commit message | a fix to one file (span exporter) | the commit also carried the CI root-cause fix in a config file |
| Commit message | "update README templates…" | a change to a render-wide **default** plus two new gates — all three items of an ungroomed `backlog` issue |
| `git branch -vv` "ahead 1" | one unpushed commit | measured against a remote ref already pruned on merge; the work was local-only and the PR had merged *without* it |
| Branch count | one leftover branch per fix | three branches per fix, byte-identical trees on three different bases |

## The rule

- Decide "did X land?" by **searching main for X's content** — the pinned config key, the
  guard's marker string, the removed assertion — never from labels or messages.
  Record the evidence per item in a table.
- **Before deleting a "merged" branch, check ancestry**, not the PR state. A PR can merge
  while a follow-up commit on its branch never reaches the remote; such commits are
  cherry-picked onto fresh branches off current main, not discarded.
- When several branches carry the same tree, consolidate to one per fix on the current
  base and delete the rest.

## Stacked branches carry other issues' work

A branch cut from another unmerged feature branch (instead of main, despite the plan
saying "branch from a clean state") put four commits under review where only one
belonged to the plan. One of the passengers changed a default for **every future
render** under a docs-shaped message, from an issue that had never been refined. The
code worked; the problem was traceability — consumers on the old shape needed to pin the
old value, which the issue said and the commit did not. The review's verdict was
"comment, not approve," purely for bookkeeping, with the fix being rebase the plan's one
commit onto main or land the passengers separately first. A feature branch with no PR
open keeps accumulating unrelated work; open the PR or retire the branch.

## See Also
- [[CI Tests the Merge Ref, Not the Branch Tip]] — related (the same review's CI finding)
- [[Git Branch Triage]] — extends (merged-vs-unmerged health check, applied at review time)
- [[Issues Live in the Repo They Change]] — related (issue state as part of the record)
- [[Branch Naming Convention Pattern]] — related (convention that makes branch↔issue traceable)
