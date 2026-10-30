---
title: Re-Scope Over Sequence for Colliding Issues
tags: [patterns, llm, pattern]
summary: When two "parallel-safe" issues turn out to touch the same files, split them by file ownership instead of serialising them — and supersede a dated audit with a new document rather than editing it.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/akira/docs/research/2026-09-03-frontend-quality-wave1-reverify.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-03-frontend-quality-wave1-reverify.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-03-frontend-quality-wave1-reverify.md
  - data/raw/claude-docs/playground/docs/research/2026-09-03-frontend-quality-wave1-reverify.md
  - data/raw/claude-docs/akira/skills/git-board/SKILL.md
  - data/raw/claude-docs/diskoe/skills/git-board/SKILL.md
  - data/raw/claude-docs/playground/skills/git-board/SKILL.md
  - data/raw/claude-docs/kiez-archive/skills/git-board/SKILL.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-19-dis330-spec-staleness-pass.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-19-dis330-spec-staleness-pass.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-19-dis330-spec-staleness-pass.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-19-dis330-spec-staleness-pass.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-19-dis330-spec-staleness-pass.md
---

# Re-Scope Over Sequence for Colliding Issues

A re-verification pass over a frontend quality audit (akira) found that two issues filed as
independent, same-lane, parallel-safe work — "migrate forms to server actions" and "fix
form accessibility" — would both rewrite the same seven form pages. Run in parallel they
would conflict on every file; run in sequence the second waits on the first.

## The move

**Re-scope rather than sequence.** Move the seven colliding pages wholesale into one issue;
the other keeps the remainder. Both are now parallel-safe with zero shared files, and
neither waits. The partition key is *file ownership*, not topic: an issue owns a set of
paths, and two issues with overlapping paths are one issue or two differently-cut issues,
never two parallel ones.

This matters most when the two issues will be worked by concurrent agents. Topic-based
scoping ("a11y" vs "forms") looks clean in a tracker and dissolves at the diff.

## Two companion rules from the same pass

- **Supersede dated audits; do not edit them.** The re-verification corrected two counts
  in an earlier audit. It did so in a new document that states exactly which sections it
  supersedes, leaving the original as the source for everything else. Editing a dated
  audit in place destroys the record of what was believed when.
- **Name drift risk separately from shipped defects.** Two implementations of the same
  component were found to be equivalent today; the finding was filed as "drift risk, not a
  shipped defect". Collapsing the two categories inflates bug counts and buries the actual
  bugs.

## Method note

The pass itself used three parallel read-only scouts, each report re-checked against the
tree by grep before being recorded — the same "tool output, not prose" standard as
[[Deterministic Review Substrate]].

## When re-scoping is too late: simulate the landing order

Sometimes the colliding branches already exist as finished, uncommitted worktrees, and
re-cutting them is no longer an option. Then **test the merge orders mechanically**: apply
each branch as a commit in a scratch clone and merge them in each sequence. Don't reason
about it. In one akira case, three worktrees on the same base all touched the Makefile and
CLAUDE.md. One never collided. The other two collided **in one direction only**. The branch
that *edited* the gate-target line conflicted if it landed first. The branch that only
inserted a new target directly above that line, leaving it as unchanged context, merged
cleanly if it landed first. The output is a landing order ("land A before B; C anywhere")
plus the one-line manual resolution if the order is broken, written down for whoever lands
B.

## See Also
- [[Deadline-Scope Isolation]] — related (scope tokens by deadline; this page scopes by file)
- [[Claude Workflow System]] — extends (issue cutting as part of the plan stage)
- [[Deterministic Review Substrate]] — related (verification method of the pass)
- [[Parallel Across Lanes, Migrations Alone]] — related (the wave policy for concurrent builds)
- [[Path-Verified Build State Markers]] — related (the same plan found "landed" claims that were not on main)
