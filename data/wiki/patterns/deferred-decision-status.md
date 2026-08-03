---
title: Deferred Decision Status
tags: [llm, pattern]
summary: A three-value status for design decisions — Resolved / Open / Deferred(trigger) — where a deferral must name the concrete event that reopens it, and a triggerless deferral silently degrades to Open so it still blocks the gate.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/skills/scope-poc/SKILL.md
---

# Deferred Decision Status

A status vocabulary for the Key Decisions table in a design document, designed so that
"we'll decide later" cannot be used to make a gate pass.

| Status | Meaning | Blocks the G1 gate? |
|---|---|---|
| `Resolved` | Decided, with rationale | No |
| `Open` | Unresolved and unparked | **Yes** |
| `Deferred(<trigger>)` | Default choice recorded now, with a named event that reopens it | No |

## The mechanism

A `Deferred` entry must carry two things: the **current default choice** and a **concrete
revisit trigger** — *"resolve before sprint 1"*, *"revisit when the first external consumer
appears"*. With both present, the deferral blocks nothing: not the design write, not
scaffolding, not the gate.

The load-bearing rule:

> *"A Deferred without a real trigger counts as Open."*

That single sentence is what makes the status honest. Without it, `Deferred` is a free
escape hatch — any blocker can be relabelled into passing. With it, the only way out of
blocking is to name the future event that forces the question back open, which is real
information rather than a deferral of thought.

The same shape governs Open Questions, which are recorded as
`[question] — revisit: [trigger or date] — close via: [/research, /parallel-research, or a
named person]`. Every parked item carries both a reopening condition and a route to
closure.

## Why "I don't know" needs a home

The surrounding convention is that *"'I don't know' is a first-class answer"* — any
interview question may be answered *unknown*. But an unknown that simply vanishes into prose
is worse than a blocker, because it looks resolved at review time. The status vocabulary
gives every unknown exactly one of two destinations:

- a Key Decision marked `Deferred(<trigger>)` with the default recorded, or
- an Open Questions entry with a revisit trigger and a closure path.

Because both destinations exist, *"unknowns never block the write"* — the design document
gets written with named gaps, on the reasoning that **a design with named gaps beats no
design**.

## Distinguishing an accepted default from an unknown

A related discipline: a default the user *accepts* is Resolved, not Open. Tier-default
answers for load, latency, and spend are recorded as
`<value> (weekend-sprint tier default, unvalidated)` — a decision with its provenance and
confidence attached, deliberately not parked as an Open Question.

The distinction is consent, not certainty: an unvalidated number the user agreed to is
settled; a number that matters and nobody knows is Open. Both are honest; conflating them
either blocks the gate spuriously or hides a real gap.

## See Also
- [[Scope-POC Design Interview]] — prerequisite-for
- [[Merge Impact and Evidence State]] — alternative-to (also separates confidence from consequence)
- [[SANYI Change-Contract System]] — extends
- [[Claude Workflow System]] — extends
