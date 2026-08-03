---
title: Copier Re-Entry as Capability Path
tags: [infra, pattern]
summary: Treating `.copier-answers.yml` as durable scaffold state so that flipping a template answer and re-rendering is the *only* sanctioned way a component enters a generated repo — which turns "scaffold the MVP now, add later" into a real guarantee rather than advice.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/skills/project-genesis/SKILL.md
---

# Copier Re-Entry as Capability Path

> *"The render is not a one-shot commitment."*

`.copier-answers.yml` in a generated project is the **scaffold state** — it records every
answer given at genesis. The governing rule:

> *"Changing an answer through copier is the only way components enter a repo after genesis
> — never hand-copy template files in."*

## Why the exclusivity matters

Hand-copying a template file into a generated repo produces a component that exists on disk
but not in the answers file. The next `copier update` doesn't know it's there, so it neither
updates nor conflicts with it — the file silently forks from the template forever. Routing
every addition through copier keeps `.copier-answers.yml` a truthful description of the
repo's shape.

That truthfulness is what makes the anti-over-scaffolding advice credible. The skill
requires reporting the add-later story on every render — *"Users who don't know this
over-scaffold 'just in case' — say it explicitly."* A user only accepts a minimal MVP
scaffold if adding the rest later is genuinely cheap and safe.

## The re-entry protocol

1. **Detect** — `.copier-answers.yml` present in the target means re-entry, not first
   render. Read it; recorded answers are the baseline. Interview only what's changing,
   *"usually a parked open question whose trigger fired"* — e.g. *"first external consumer
   appeared" → `include_mcp_server=true`.* This is where a [[Deferred Decision Status]]
   trigger cashes out into an actual code change.
2. **Clean tree first** — `git status` must be clean before re-rendering, because *"copier
   conflicts on top of uncommitted work are unrecoverable."* Hard-stop and ask the user to
   commit or stash otherwise.
3. **Execute** — `copier update -d <changed>=<value>` when the project was rendered from a
   tagged version; from a moving working tree, `copier copy --overwrite --vcs-ref HEAD
   --defaults -d <changed>=<value>` carrying the other answers from `.copier-answers.yml`.
4. **Close the loop** — mark the parked DESIGN.md question `Resolved` and re-run the gate
   check.

**Idempotent gap-filling:** unchanged answers re-render to identical files; *"only the
flipped toggle's files appear."* That property is what makes step 3 safe to run repeatedly.

## Two front doors over one mechanism

| Command | Runs in | For |
|---|---|---|
| `/project-genesis` §Re-entry | The template repo | The template author's cross-repo view |
| `/add-capability <x>` | The generated project | What ships to and runs for the end user |

`/add-capability` (aliases `/add-rag`, `/add-eval-metric`, `/add-integration`) is *"the
capability-named front door over this same mechanism"* — same clean-tree gate, same
`copier update -d`, same close-the-loop. The user names a capability; the skill translates
it to a toggle. Naming the door after the user's intent rather than the mechanism is the
same translation move as asking for eval metrics in the design's terms rather than copier's
(see [[Asked vs Derived Scaffold Variables]]).

Conflict walkthroughs on user-edited files are a separate skill's job (`/template-update`,
see [[Copier Upstream Update Workflow]]) — re-entry hands off rather than improvising.

## Legacy answer mapping

When the interview's shape changes, old planning docs stay actionable because both forms are
honored by `-d`: `include_calendar_integration=true` → `calendar` in `external_systems`;
`include_ml=true` → `ml` in `optional_features`; `scaffold_full_project=false` →
`project_type=existing_repo`. Migrating an interview to new axes without breaking documents
written against the old one is part of the contract.

## See Also
- [[Asked vs Derived Scaffold Variables]] — prerequisite-for
- [[AI Project Template Scaffold]] — extends
- [[Deferred Decision Status]] — extends (triggers reopen into a re-entry)
- [[Scope-POC Design Interview]] — prerequisite-for
- [[Copier Upstream Update Workflow]] — alternative-to (pulling the template's changes vs. changing your answers)
- [[Template Migrations for Structural Moves]] — extends (structural edits the answers file can't express)
