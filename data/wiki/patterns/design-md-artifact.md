---
title: DESIGN.md Artifact
tags: [llm, reference]
summary: The six-section design record every scaffolded project ships — problem, actors, C4 system context, MVP scope, key decisions, and non-functional constraints — shipped as a placeholder stub when unfilled so the skipped conversation stays visible.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/docs/research/poc-system-design-interview.md
---

# DESIGN.md Artifact

The output of [[Scope-POC Design Interview]] and the input to the scaffold interview.
*"Every project scaffolded from this template should ship with a `DESIGN.md` stub."*

## The Six Sections

| # | Section | Answers |
|---|---------|---------|
| 1 | Problem + success criteria | What does the demo show? |
| 2 | Actors | Who uses this, what do they do today, what does the AI do instead? |
| 3 | System context | C4 Level 1 — one paragraph or lightweight mermaid |
| 4 | MVP scope | In / out / open |
| 5 | Key decisions | Resolved and open |
| 6 | Non-functional constraints | Data classification, multi-tenancy, operator model |

Sections 1–2 and 4–6 correspond directly to interview tiers 1, 5, and 4; section 3 is the
only one that is a *rendering* rather than a transcript — the actor and boundary answers
redrawn as a context diagram.

## The C4 Framing

Tiers 1 and 2 of the interview are explicitly labeled against the C4 model:

| Tier | C4 level | Scope |
|---|---|---|
| 1 — Problem and actors | Level 1 (System Context) | Who is outside the box and why |
| 2 — System boundaries | Level 2 (Containers) | What the box is made of and what it talks to |

Tiers 3–5 have no C4 analogue — they cover AI design, constraints, and scope, which C4
does not model. The borrowing is deliberate and partial: C4 supplies vocabulary for the
boundary questions and stops where the AI-specific questions begin.

Section 3 asks for *"one paragraph or lightweight mermaid"* — the artifact deliberately
does not demand a full C4 diagram set, only Level 1.

## Resolved-and-Open Is the Load-Bearing Column

Section 5 records *both* resolved and open decisions in the same table. Openness is
first-class state, not an omission — see [[Deferred Decision Status]] for the three-value
status (Resolved / Open / Deferred-with-trigger) that makes a deferral auditable rather
than a gap.

## The Blank Stub Is Not a Failure Mode

When the design conversation is skipped, the stub still ships with placeholders — *"better
than nothing, since it forces the conversation to happen explicitly rather than
implicitly."*

A blank section labelled "Multi-tenancy" is a visible unanswered question. A missing file
is an invisible one. That distinction is the whole justification for shipping the stub
unconditionally.

## Multi-Tenancy Has No Copier Equivalent

Most Tier 4 constraint answers map to a scaffold parameter (`data_sensitivity`,
`vector_backend`). Multi-tenancy does not:

> *"Architectural flag — no direct copier equivalent; surfaces in DESIGN.md."*

This is the clearest case for DESIGN.md existing as an artifact separate from
`.copier-answers.yml`: it holds the design decisions that **no template variable can
carry**. See [[Asked vs Derived Scaffold Variables]] for what the answers file does hold.

## See Also
- [[Scope-POC Design Interview]] — part-of (the interview that populates it)
- [[Design-Before-Infrastructure Sequencing]] — prerequisite-for
- [[Deferred Decision Status]] — extends (status semantics for section 5)
- [[Asked vs Derived Scaffold Variables]] — complements (what copier answers carry instead)
- [[Documentation Boundary — Machine vs Human Docs]] — related (which docs are machine- vs human-consumed)
- [[Derived-and-Hidden Design Decisions]] — instance-of (the artifact that passes its gate while Scale: is empty)
- [[Block Attribute Inversion]] — extends (per-block metadata as generated DESIGN.md content)
