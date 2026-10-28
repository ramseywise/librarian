---
title: Archived Skills Convention
tags: [meta, pattern]
summary: Retired skills move one directory level below the loader with an ARCHIVED.md stating date, reason and destination; fold when two skills are "one skill run twice", when a skill targets a command that no longer exists, or when it needs an artifact the repo that owns the stage already provides — and salvage the rules worth keeping into the successor or a note before the skill goes dark.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/playground/skills/design-initiative/SKILL.md
  - data/raw/claude-docs/galactus/skills/archived/README.md
  - data/raw/claude-docs/galactus/skills/archived/design-initiative/ARCHIVED.md
  - data/raw/claude-docs/galactus/skills/archived/design-initiative/SKILL.md
  - data/raw/claude-docs/galactus/skills/archived/design-prototype/ARCHIVED.md
  - data/raw/claude-docs/galactus/skills/archived/design-prototype/SKILL.md
  - data/raw/claude-docs/galactus/skills/archived/design-sprint/ARCHIVED.md
  - data/raw/claude-docs/galactus/skills/archived/design-sprint/SKILL.md
  - data/raw/claude-docs/galactus/skills/archived/docs-check/ARCHIVED.md
  - data/raw/claude-docs/galactus/skills/archived/docs-check/SKILL.md
  - data/raw/claude-docs/galactus/skills/archived/project-discovery/ARCHIVED.md
  - data/raw/claude-docs/galactus/skills/archived/project-discovery/SKILL.md
  - data/raw/claude-docs/galactus/skills/archived/project-genesis/ARCHIVED.md
---

# Archived Skills Convention

## Mechanics

- `skills/archived/<name>/` — one level below the loader's glob, so the skill is no longer
  discoverable by the runtime but its text is still greppable and reviewable.
- `ARCHIVED.md` beside the original `SKILL.md`: **date, reason, destination** (the skill or
  mode that now covers the job). The README carries a one-row-per-skill table of the same.
- Nothing is deleted; the fold is reversible by a `git mv`.

## Fold criteria the table actually used

| Reason | Example |
|---|---|
| **One skill run twice, not two skills** | a discovery skill and the scoping skill's `discovery` mode asked the same questions of the same inputs — folded into a mode plus a `reference/` file |
| **Targets a command that no longer exists** | an initiative-planning skill whose last step called a ticket-export command that had been removed; it had been silently failing at the end of every run |
| **Needs an artifact the owning repo provides** | a genesis skill that required a `copier.yaml` this repo never had — *the repo that owns the stage is canonical*; do not re-implement scaffolding where the template lives elsewhere |
| **A lens without a role** | a sprint skill written from a product-manager viewpoint with no reporter, no verdict and no artifact — see [[When a Lens Earns Agenthood]] |
| **Superseded by always-on detection** | a docs-drift check folded into the architecture review dimension, which now reports `pre_existing: true` drift on every review — *"the standalone skill required an operator to suspect drift before it could find any"* |

## Salvage before archiving

The ARCHIVED notes carry rules that outlived the skills — the point of writing them down
at fold time is that they otherwise go dark with the skill:

- **Milestone rules:** a milestone is a verifiable system state, not a bundle of work;
  exactly one done-condition; only externally-driven milestones get dates; defer rather
  than stretch; every task traces to a failure mode it closes.
- **Routing asymmetry:** fitting a model is the tell; calling a model is not — now in
  [[Auditable Track Router]].
- **Prototype honesty:** show the red first; *an implausibly good first score is a finding,
  not a result*; build the checker before the generator.
- **Test selection:** a role-separation bug survived a 259-test green suite — pick tests by
  architectural seam, not by count (take-home retrospective, 2026-08-08).
- **Voice is a separate workstream** from the general AI roadmap, with its own constraints
  — see [[Duplex Voice Breaks Discrete-Turn Assumptions]].
- **Ratify inherited decisions out loud:** a scaffold's defaults are decisions someone else
  made; name them in the new repo's first ADR rather than inheriting silently.

## See Also
- [[Claude Workflow System]] — instance-of
- [[Capability Parity Audit]] — extends (the audit that finds the fold candidates)
- [[When a Lens Earns Agenthood]] — extends
- [[Auditable Track Router]] — extends (salvaged routing rule)
- [[Job Verb Taxonomy for Skills]] — extends (the duplicate-verb check that catches "one skill run twice")
- [[Build the Checker Before the Generator]] — extends (the prototype-honesty rule in full)
- [[Skill Admission Test: Workflow With a Gate]] — extends
