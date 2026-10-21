---
title: Template Migrations for Structural Moves
tags: [infra, pattern]
summary: A file-level merge cannot express "this module moved" — template `_migrations` supply the missing structural edit, and degrade to a loud WARN rather than a silent overwrite when the file being moved was hand-edited.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/ai-project-template/skills/template-update/SKILL.md
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-19-genesis-lifecycle-architecture.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-19-genesis-lifecycle-architecture.md
---

# Template Migrations for Structural Moves

## The gap a file-level merge leaves

Copier reconciles a generated project with its template file by file. That model has no
vocabulary for a *move*: when the template relocates `core/*.py` to
`core/pipelines/corpus/*.py`, the merge sees an unrelated deletion at one path and an
addition at another. Accepting both leaves the project with two copies — the new one the
template ships, and the old one still sitting where imports point at it.

Nothing errors. The project keeps running against the stale copy until something
independently touches the import path, which makes this the same failure shape as
[[Silent Fallthrough in String-Keyed Discovery]]: a rename that selects a wrong-but-valid
target instead of failing.

`_migrations` are the template's escape hatch — declarative structural edits that run as
part of the update and do the thing the merge cannot.

## The two output lines and why the second exists

Migration output is read, not scrolled past. It emits exactly two kinds of line:

| Line | Means | Response |
|---|---|---|
| `[migration] removed stale …` | The old location was cleaned up | Informational — nothing to do |
| `[migration] WARN …` | **A hand-edited file was left in place** | Port the edits; repoint the named imports |

The WARN is the load-bearing half. A migration that unconditionally deleted the old path
would destroy local work, so when it detects the file diverged from what the template
originally generated, it **refuses to act and reports instead**. The result is a file whose
edits are real but now orphaned at a path nothing imports.

That is a deliberate degradation to a loud no-op. The migration cannot merge the local edits
into the new location — it doesn't know what they mean — so the only honest options are
destroy or report, and it reports. Resolution is manual and named for the user: move the
local edits into the new location, then repoint the specific imports the warning identifies.

## Why this belongs to the template, not the project

The move is knowledge the template author has and the generated project doesn't. A project
being updated has no way to infer that two unrelated-looking path changes are one relocation.
Encoding it upstream, once, is what lets every downstream project take the change without
each one independently discovering the duplication.

This is the same asymmetry that makes `.copier-answers.yml` authoritative in
[[Copier Re-Entry as Capability Path]] — structural facts about the scaffold live with the
scaffold.

## Variable renames silently lose answers

Renaming a copier variable drops the old answer on `copier update`: unknown keys in
`.copier-answers.yml` are stripped before render (observed on copier 9.17.0), so an
`{% if old_name is defined %}` fallback in the new default never fires. The only reliable
fix is a pre-render migration that rewrites the answers file. Cheaper still: keep a
derived seed under the old name rather than renaming. Whether a human ever supplied the
value is what makes a variable answer-carrying — derived-only variables can be renamed
freely. Pin and tag template versions so `--vcs-ref` targets a known migration set.

## See Also
- [[Copier Upstream Update Workflow]] — prerequisite-for (migrations run during the update)
- [[Silent Fallthrough in String-Keyed Discovery]] — extends (the same rename-doesn't-crash failure shape)
- [[AI Project Template Scaffold]] — extends (structural changes shipped downstream)
- [[Sync as Render, Not Copy]] — complements (transforming content on the way into the template)
- [[Read-Every-Consumer Migration]] — related (enumerating every reader before a structural move)
