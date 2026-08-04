---
title: Copier Upstream Update Workflow
tags: [infra, pattern]
summary: Pulling template changes into an already-scaffolded project — a clean-tree gate, a mandatory `--pretend --diff` preview, impact-categorized change review, and conflict resolution that preserves local intent over template defaults.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/skills/template-update/SKILL.md
---

# Copier Upstream Update Workflow

The inverse direction from [[Copier Re-Entry as Capability Path]]. Re-entry changes *this
project's answers* to add a component; an upstream update pulls in *changes the template
made* since this project was rendered. Both run through `copier`, but they resolve different
kinds of drift and carry different risks.

## Two hard gates before anything runs

1. **A clean working tree.** `git status` must be clean; a dirty tree is a refuse-and-stop
   condition, not a warning. *"Never run `copier update` on a dirty working tree — data loss
   risk."* Same gate as re-entry, for the same reason: copier conflicts layered on top of
   uncommitted work are unrecoverable.
2. **A preview first.** *"Always `--pretend --diff` first — no surprises."* If it reports
   nothing, the answer is "you're up to date" and the workflow ends there.

`.copier-answers.yml` supplies the baseline: `_src_path` (where the template lives),
`_commit` (the version last updated from), and every answered parameter.

## Categorizing the diff by impact

The review is not file-by-file — the diff is sorted into five buckets whose impact differs
by an order of magnitude:

| Category | Impact | Action |
|---|---|---|
| New files | Low — adds functionality | Review; delete if unwanted |
| Modified templates | Medium — may collide with local edits | Review conflicts |
| New/changed parameters | Medium — may need answers | Answer new questions |
| **Removed files** | **High** — may remove code you depend on | Check before accepting |
| **Infrastructure changes** | **High** — CI, Docker, configs | Test after update |

Removals and infra changes are the high-impact rows because both fail *after* the update
appears to succeed: a deleted file breaks an import at runtime, and a changed CI config
breaks the next push rather than this command. Each file gets explained in plain language —
what the template change does and why — rather than shown as a raw diff.

## Conflict resolution preserves local intent

Potential conflicts are identified by intersecting the incoming diff with the project's own
modification history (`git log --follow`), plus new parameters that interact with existing
answers and removed features the project currently uses.

Each conflict resolves one of three ways: **accept template** (the template version is better,
or the local change was a workaround the template has now fixed properly), **keep local** (the
change is intentional), or **merge** (both are needed).

The tie-breaking rule is directional:

> *"Conflict resolution preserves local intent over template defaults."*

And when intent can't be read off the diff, *"if a conflict is ambiguous, ask the user rather
than guessing."* A template default is a guess about a generic project; a local edit is
evidence about this one.

## Migrations do what file-merge can't

Copier's merge operates per file, so it cannot express a *structural* move — a file
relocating from `core/*.py` to `core/pipelines/corpus/*.py` looks like an unrelated deletion
and addition. The template's `_migrations` close that gap, and their output must be read
rather than scrolled past:

- `[migration] removed stale …` — informational; the old location was cleaned up.
- `[migration] WARN …` — **a file you hand-edited was left in place.** The local edits now
  live at a path nothing imports. This is surfaced to the user with an offer to port the
  edits into the new location and repoint the imports the warning names.

The WARN line exists precisely because the migration refuses to destroy hand-edited work —
it degrades to a loud no-op instead of a silent overwrite.

## Verification is part of the update

The update isn't complete when the command exits. Post-update checks: run the test suite,
confirm the dev server starts, and verify `.copier-answers.yml` records the new commit. The
standing requirement is that *"after update, the project must still pass its existing
tests"* — the update is not a state you accept and debug later.

For complex updates (>5 conflicts) the session is written to
`.claude/docs/template-update-log.md` with the commit range, changes applied, each conflict
resolution *with rationale*, and a manual-verification checklist. Below that threshold the
update leaves no artifact — the output is the updated project.

## Adjacent scenarios that are not updates

- **"I answered a parameter wrong at scaffold time"** — not an update. That's
  `copier recopy --trust` with corrected `-d` flags.
- **"The update adds a feature I don't want"** — delete the files and either add them to
  `.copier-exclude` or set the feature flag false in `.copier-answers.yml`, then recopy —
  so the answers file keeps describing the repo truthfully.
- **"I'm many versions behind"** — update incrementally through breaking changes, reading the
  template's CHANGELOG or commit history for migration notes.

## See Also
- [[Copier Re-Entry as Capability Path]] — alternative-to (changing your answers vs. pulling the template's changes)
- [[AI Project Template Scaffold]] — extends (the upstream side of the template contract)
- [[Asked vs Derived Scaffold Variables]] — prerequisite-for (answers file is the update's baseline)
- [[Silent Fallthrough in String-Keyed Discovery]] — extends (structural renames that don't announce themselves)
- [[Sync as Render, Not Copy]] — alternative-to (reservoir→template render vs template→project update)
