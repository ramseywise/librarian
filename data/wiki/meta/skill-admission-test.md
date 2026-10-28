---
title: "Skill Admission Test: Workflow With a Gate"
tags: [meta, llm, pattern]
summary: A Claude Code skill earns its existence only if it is a workflow with a gate — facts go to refs, durable descriptions to docs, deterministic operations to Makefile/scripts, and judgment passes to agents — and its `description` is its entire discovery surface.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/playground/skills/create-skill/SKILL.md
  - data/raw/claude-docs/akira/skills/create-skill/SKILL.md
  - data/raw/claude-docs/diskoe/skills/create-skill/SKILL.md
  - data/raw/claude-docs/kiez-archive/skills/create-skill/SKILL.md
---

# Skill Admission Test: Workflow With a Gate

The `create-skill` skill in akira (and its diskoe / kiez-archive copies) opens with a test
before any file is written: **a skill is a workflow with a gate.** Anything else belongs
somewhere cheaper.

## Routing table

| What you have | Where it goes |
|---|---|
| A fact or convention | a ref file (`~/.claude/refs/*.md`) |
| A durable description of the system | a doc |
| A deterministic operation | a Makefile target or script |
| A judgment pass dispatched by a skill | an agent |
| A multi-step workflow with a human or check gate | a skill |

## Authoring rules

- **`description` is the whole discovery surface.** The model sees nothing else when
  deciding whether to load the skill; write it as trigger conditions.
- Set `disable-model-invocation: true` unless the skill is meant to be auto-dispatched.
- `allowed-tools` is a real boundary, not documentation. **A judging agent gets no edit
  tools** — it can only report.
- Every step that can fail names its stop condition.
- Keep `SKILL.md` under ~250 lines; move detail to `references/`.
- **Never aggregate a family of skills into one wrapper** — a wrapper collapses the
  separate gates into one, and the gates were the point.
- Test discovery in a fresh session; the authoring session already knows the skill exists.

## Interview details (playground copy)

The playground copy of the skill adds a few rules to the interview:

- **A skill with no gate is a script.** Every skill stops at a verdict, a sign-off on
  assumptions, or a status transition.
- **Name where the output lands.** That is either working plans, which are git-ignored,
  or durable tracked docs. A skill whose output has no home drifts.
- The stage-and-role line becomes the first sentence of the description.
- Validate mechanically: `name:` must equal the directory name, or the skill never loads.
- Never write the skill's first real artifact as a demonstration, and never edit sibling
  skills to make a new one fit.

## See Also
- [[Capability vs Phase Skills]] — extends (the admission test decides whether something is a skill at all)
- [[Documentation Boundary — Machine vs Human Docs]] — related (where the non-skill content lands)
- [[Retro Open-Hypotheses Loop]] — related (the retro proposes new skills only through this test)
- [[Four-Stage Design Pipeline with Backflow]] — related (the staged family that must not be wrapped)
- [[Claude Workflow System]] — extends
