---
title: Asked vs Derived Scaffold Variables
tags: [infra, pattern]
summary: A scaffold interview that splits ~20 template variables into six asked out loud, eight derived-then-confirmed, and the rest left silently defaulted — with the split decided by blast radius of a wrong guess, not by how many variables exist.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/skills/project-genesis/SKILL.md
---

# Asked vs Derived Scaffold Variables

`/project-genesis` is *"a project-scoping-to-copier-answers translator"* — a thin
conversational front door over a copier template, existing so a user answers six real
questions *"instead of answering ~20 raw copier prompts blind."*

The pattern is the **three-tier split** of the variable space:

| Tier | Handling | Examples |
|---|---|---|
| **Asked** (6) | Open questions in conversation | `project_name`, `project_type`, `primary_users`, `external_systems`, `human_approval` |
| **Derived** (8) | Proposed with derivation shown; user corrects | `project_slug`, `deployment_target`, `data_sensitivity`, `agent_tools`, `agent_memory`, `primary_backend_language` |
| **Inferred** (rest) | Never mentioned unless raised | `source_root`, `eval_root`, `python_version`, `aws_region` |

## The derivation root

`project_type` is *"the derivation root — 54 vars key off it."* One answer collapses most
of the space, which is why the asked tier can be small at all. `primary_users` is the second
root: it seeds both `deployment_target` (`internal` → docker, `customers`/`public_api` →
cloud, `developers` → local) and `data_sensitivity`.

## Confirm the derivation, don't hide it

The derived tier is marked `when: false` in `copier.yaml`, so copier resolves it from
defaults and never prompts. The skill's stated job is *"to confirm them in conversation, not
to leave them as invisible guesses"* — presented as *"Given your answers, I'm setting these
— correct anything wrong."*

**Surface the derivation, not a blank prompt.** A user shown *"you said customers, so I'm
setting deployment_target=cloud"* can correct it in one word; a user shown an empty field
must reconstruct the reasoning first. This is the same asymmetry behind presenting archetype
choices as [[AI Project Archetypes|cards with trade-offs]] — evaluating a proposal is far
cheaper than generating one.

## Blast radius decides the tier

The split is not by importance but by **cost of a wrong silent default**:

- `deployment_target` is explicitly called a *"cheap wrong guess — one CD workflow +
  DESIGN.md row"* → derived.
- `human_approval` is *"the one variable where a silent default has an irreversible failure
  mode. Always ask it out loud"* — and it is deliberately noted as *"independent of every
  other answer"*, so it cannot be derived even in principle.
- `data_sensitivity` is derived but with a mandatory escalation probe, because it drives a
  hard rule in the generated `CLAUDE.md` and a Terraform tag: *"You said customers — I'm
  setting data sensitivity to `restricted`. Anything regulated (health, financial, minors)
  that should make this `secret`?"*

The general rule: **a default is safe to apply silently in proportion to how cheaply it can
be reversed.** The same reasoning governs the mandatory redaction question in
[[Scope-POC Design Interview]] when classification is restricted.

## Naming is asked even when defaulted

`agent_slug` has a working default (`assistant`) but is still always proposed from the
project's domain — *"an intake assistant → `intake_triage`, a grants helpdesk →
`grants_qa`, never leave the generic `assistant` default without offering a better name."*
It names both the source directory and the Makefile targets, so the generic default is
cheap to accept and expensive to live with.

## Ask in the design's terms, not the template's

Eval metrics are elicited by translating copier's vocabulary into the user's: *"when should
this assistant hand off to a human?"* → `escalation`; *"does it route queries to the right
place?"* → `intent`. Retrieval eval ships regardless and *"is not offered as a choice"* —
a non-decision is not presented as one.

## Unknowns don't block the render

*"'I don't know' never blocks the render."* An unknown leaves the variable unset (the seeded
default fills it), parks the question in DESIGN.md with a revisit trigger — or records it as
`Deferred(<trigger>)` per [[Deferred Decision Status]] — and the capability lands later via
[[Copier Re-Entry as Capability Path]]. *"Genesis never blocks on a deferred decision."*

## The answers file is the deliverable

Step 4 writes `/tmp/genesis-answers.yml` and **stops** — *"Do not run copier here — the file
is the deliverable of this step, and it is reviewable before anything hits disk."* The user
runs the render after review. The scaffold interview's output is an inspectable artifact,
not a side effect.

Rendering into an existing repo *"needs a protocol, not hope"*: snapshot untracked files the
template will touch (git cannot restore those), render with `OVERWRITE=1`, then restore
user-owned files and report exactly which pre-existing files were overwritten vs preserved.

## Scope discipline

The skill opens by naming what it is not: *"no multi-phase engagement ritual, no identity
files... If you're tempted to add phases, growth logs, or reflection steps here, that's
scope creep back toward the thing that was explicitly ruled out — don't."* An explicit
anti-scope pointing at the plan doc that decided it.

## See Also
- [[Copier Re-Entry as Capability Path]] — extends
- [[Scope-POC Design Interview]] — prerequisite-for (DESIGN.md pre-answers the interview)
- [[AI Project Template Scaffold]] — extends
- [[Deferred Decision Status]] — extends
- [[Project Discovery Conversation]] — prerequisite-for
- [[Copier Upstream Update Workflow]] — extends (the answers file as the update baseline)
- [[Integration Pattern Selection]] — extends (integration answers become render-time toggles)
- [[Deployment Topology Ladder]] — extends (topology choice writes five coupled parameters)
- [[Derived-and-Hidden Design Decisions]] — extends (when derivation crosses into hiding a design decision)
- [[Block Attribute Inversion]] — complements (the derive-then-confirm asymmetry applied to design metadata)
