---
title: Hint Ladder With Logged Aid Rung
tags: [interview, pattern]
summary: A five-rung help ladder (clarifying question → area → concept → signature → work it together) climbed one announced rung at a time, where the highest rung used is logged as an Aid column — help changes what is offered during an attempt, never what is recorded after it, and the Aid trend on a repeated question is the actual learning curve.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/sisyphus/skills/coding-drill/SKILL.md
  - data/raw/claude-docs/sisyphus/skills/env-drill/SKILL.md
---

# Hint Ladder With Logged Aid Rung

The sisyphus drill skills had to reconcile two needs that pull against each other: getting
stuck with help is *practice*, getting stuck without help is *measurement*, and a drill
that blurs them "neither teaches nor measures". The ladder is how help gets offered without
destroying the measurement.

## The rungs

| Rung | What is given | Example (token-auth question) |
|---|---|---|
| **0** | The clarifying question an interviewer would ask — reframes, reveals nothing | "What are you comparing when you verify the signature?" |
| **1** | Name the *area*, not the answer | "The comparison itself has a security property worth checking." |
| **2** | Name the concept, no code | "You want a constant-time comparison — timing-attack surface." |
| **3** | The stdlib tool or signature, no body | "`hmac.compare_digest(a, b)` — where does it go?" |
| **4** | Work it together line by line; the learner still types | Walk the verify-before-parse ordering |

Rules that make it work:

- **One rung at a time, announced** ("that's a rung 2") so the cost is visible. Wait for the
  learner to work with each rung before the next — *the rung they needed is the
  diagnostic*, and jumping to 4 destroys it.
- **Syntax stalls are exempt.** Forgetting how `defaultdict` nests is not a concept gap;
  give the pattern immediately, note it, and don't charge the ladder. Burning a timebox on
  remembered syntax teaches nothing about the problem.
- **Cap the ladder in cheap passes.** In a talk-through pass, stop at rung 2 — an approach
  handed over at rung 3+ turns the later typed pass into transcription.
- **Rung 4 is teaching, not failure** — but the item goes back in the queue flagged open and
  is re-drilled cold within a few sessions. Learned at rung 4 is not yet demonstrated.

## The record is not softened

> Help changes what's *offered during* the attempt, never what's *recorded after* it.

A question solved at rung 3 is logged `Aid 3` and re-queued however smoothly it went.
Scoring it as a clean solve "is the one outcome with negative value, because it retires a
question the learner can't yet do alone." In a measurement stance (mock) the column is `—`
because no help is offered at all.

## Reading the Aid column

The Aid column is called "the most informative column in the log":

- **Falling on a repeated item (3 → 1 → 0)** — the thing actually learned, invisible
  without reading rows together.
- **Flat across re-drills** — the rung isn't landing; usually the gap is one level lower
  than assumed (a concept hint keeps failing because the underlying syntax isn't
  automatic).
- **Anything last solved at Aid ≥2 outranks a never-seen item** in selection: understood
  with help, not yet produced without it.

The same idea generalises beyond interviews: any assisted workflow that wants to *measure*
capability must record the assistance level as a first-class field, or assisted successes
silently count as independent ones.

## See Also
- [[Graded Rehearsal Drill Harness]] — instance-of (the drill skills that use the ladder)
- [[Gate Pass Rate Measures Effort, Not Readiness]] — extends (a pass that was helped measures the help, not the capability)
- [[Voice-Preserving Redraft Loop]] — alternative-to (the spoken-answer drill's help policy: critique and redraft rather than ladder)
