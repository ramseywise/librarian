---
title: Changing a Derived Default Is a Migration
tags: [infra, pattern]
summary: "In Copier, a `when: false` derived variable is recomputed on every `copier update` rather than read from the answers file, so changing its default silently re-lays-out every existing consumer (a new tree rendered beside the old one) — ship it with a pin-the-old-value release note, and remember defaults can only see questions declared above them."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/ai-project-template/docs/plans/AIT-33-plan.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--AIT-33-plan.md
---

# Changing a Derived Default Is a Migration

A render-bloat follow-up changed the template's Python root to default to a flat layout
(`src/` at the project root rather than `backend/src/`) for Python-only projects without a
frontend. The mechanism already worked with an explicit `-d py_project_root=.`; the change
only touched the *default*. That turned out to be the riskiest line in the plan.

## Derived variables are re-derived on every update

`py_project_root` is a `when: false` variable. It is never asked, and it is computed from
other answers ([[Asked vs Derived Scaffold Variables]]). Copier recomputes such variables
on **every** `copier update` instead of replaying a stored answer. So every existing
Python-only, no-frontend consumer would flip from `backend/src/` to `src/` on its next
update. Copier renders the new tree and **does not delete the old one**, which leaves a
duplicated backend.

The change is therefore a migration for consumers, even though no consumer asked for it.
The mitigation was a release note in the PR body telling existing projects to pin
`-d py_project_root=backend` in `.copier-answers.yml` before their next update. Reverting
does not undo it: consumers who already updated need the pin either way. The stronger fix
was left as a design question for review: derive from the *answered* value when one
exists.

## A default sees only the questions above it

Copier renders each question's default with only the answers collected *so far*. The
signals the new default needed (whether a frontend is included, the frontend/backend
topology) were declared about 300 lines *below* `py_project_root`. Referencing them would
render as undefined.

- **Re-derive inline instead of reordering.** The frontend condition was re-derived from
  the same external design data the later question reads, using a python-only signal
  available above the variable.
- Moving the block up was rejected because later questions' help strings interpolate the
  root variables, so a reorder would break them silently.

## Static checks cannot see derived-default regressions

The template's static path sweep hardcoded each variable's default (`VAR_DEFAULTS`), so it
was insensitive to a *derived* default. A green `make test` said nothing about the flat
layout. Only a render-smoke matrix that rendered each shape, plus a byte-identity diff of
the fully-on shape against a `main` render, covered it. See
[[Test Derived Defaults Without Overrides]].

## A smaller trap in the same change

Gating a staged directory away (an empty notebooks dir) broke an unconditional
`mkdir -p … && cp -R <staged>/nbks/. …` clause. `cp -R` on a missing source fails and
**aborts the whole `&&` chain**, silently dropping every merge after it. The fix was to
pull the clause into its own task, behavior-neutral and separate from the gating step,
and verify it with the byte-identity diff.

## See Also
- [[Asked vs Derived Scaffold Variables]] — extends (what happens to the derived tier on update)
- [[Test Derived Defaults Without Overrides]] — extends (render the derivation, not the override)
- [[Copier Upstream Update Workflow]] — prerequisite-for (the consumer side that absorbs the change)
- [[Execute Every Toggle Configuration]] — related (the static sweep that cannot see it)
- [[AI Project Template Scaffold]] — instance-of
