---
title: AI-Assisted Take-Home Playbook
tags: [interview, pattern]
summary: For a 60–90 minute AI-assisted build or a design-and-present take-home, spend the time as decide → walking skeleton → deepen → narrate, hand-roll the scaffold rather than render a production template, make your judgment visible by rejecting AI output on camera, and give a full slide to what you deliberately did not build.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/sisyphus/docs/research/2026-08-08_ml6-prototyping_loop-and-presentation.md
  - data/raw/claude-docs/sisyphus/docs/research/2026-08-08_ml6-prototyping_consolidation-audit.md
  - data/raw/claude-docs/sisyphus/docs/research/2026-08-08_ml6-prototyping_cloud-architecture.md
  - data/raw/claude-docs/sisyphus/docs/plans/2026-08-08-ml6-genai-prototyping-loop.md
  - data/raw/repos/sisyphus/.claude--docs--plans--2026-08-08-ml6-genai-prototyping-loop.md
---

# AI-Assisted Take-Home Playbook

Distilled from research and a tooling audit done before two take-homes: one untimed
design-and-present case (20 min, max 10 slides, 25 min Q&A with lead engineers) and one
recorded 60–90 minute build with AI agents allowed. Medium-confidence web research about
what evaluators reward; the tooling audit is first-hand. The premise: evaluators no longer
ask "did you use AI?" but "did the human visibly own the decisions?"

## The time budget

| Phase | Share (of 60–90 min) | Output |
|---|---|---|
| Understand + decide | ~17% | Minimal architecture; the three design choices named |
| **Walking skeleton** | ~33% | Thin end-to-end slice through every layer (request → model call → validated output), nothing optimised |
| Deepen the critical path | ~33% | Only what the case grades (e.g. schema validation, fit layer) |
| Verify + narrate | ~17% | Two happy paths run; decisions written down |

The trap is skipping the skeleton: 45 minutes on a component that never wires end-to-end,
then presenting half-working code. A running thin slice beats 70% of an optimised one, and
makes scope talk concrete ("add X to the skeleton, or v2?").

## Hand-roll the scaffold for a spike

A tooling audit before the build found the personal production template (a Copier
template with a ~14-question interview and an all-or-nothing project tier) cost ~12
minutes of interview, render and orientation, and imposed eval, infra and corpus-pipeline
structure a throwaway spike doesn't need. Hand-rolling `main.py` + `pyproject.toml` +
`Makefile` + one test took ~3 minutes. Templates are for projects being shipped. Two side
findings generalise:

- **Audit what a named asset actually contains.** A template directory named like a
  provider-agnostic LLM kit held only a virtualenv — a cargo-cult name that would have been
  cited as a capability.
- **Heavy research → plan → review pipelines are bloat at this timescale**; reuse the
  convention references and capability snippets, skip the gates. Pre-built scaffolding is
  legitimate if disclosed; pre-written core logic presented as live authorship is not.

## Making judgment visible with an agent on camera

| Red flags | Green signals |
|---|---|
| Large blocks appear instantly, unexplained | Problem framed aloud *before* prompting |
| Explanation doesn't match the code | Reads and critiques output aloud |
| Jumps to an optimised solution, no trade-off talk | States why a trade-off was chosen |
| Can't defend the code when probed | Catches a hallucination or limitation |
| | **At least one visible rejection or modification of AI output** |

**Serial agents, not parallel, on a recording.** Parallel agents only save time when tasks
are truly independent and the merge is cheap; on camera the wait is dead air, and serial
turns let you narrate the decision between each.

## The presentation

- **Structure ten slides around trade-offs, not features**: problem, constraints and
  success criteria, two slides of design choices, one architecture diagram, two
  implementation highlights, verification with a real output, **things we did not
  build**, limitations with mitigations.
- **"Did not build" is the clearest seniority signal.** Frame each as a trade-off with the
  effort quantified, the trigger that would change it, and the migration path.
- **Single-slide architecture diagram:** 5–7 boxes; one icon set; unidirectional labelled
  arrows; one label per box (design choice, not config knobs); show the failure path
  (dead-letter); mark async vs sync; one cost callout. Unused services on the diagram read
  as a copied template. (See [[Right-Sizing a Document-to-LLM Pipeline]].)
- **Demo: hybrid** — a 2-minute pre-recorded clip, screenshots in the slides, live Q&A on
  code paths. A live call is 30–60 s of content for full crash risk. Format is secondary:
  a clear deck beats a custom website built at the expense of the talk.

## Q&A defences that land

Have a concrete answer, not "I'd prompt carefully", for: hallucinated facts (ground in
source, cite, validate, omit what isn't there, human gate); unit cost at 1000×; worst-case
layout input (pre-truncate, flag the truncation); model choice (evaluated alternatives,
cost and capability); invalid JSON (constrained output plus schema validation, structured
error not a 500); and "what would you change" (always have three).

Note the research is not internally consistent: the presentation angle suggests framing
"RAG-first" for grounding, while the ingest and architecture angles conclude a two-PDF
corpus needs no vector store — grounding in full context with citation validation is the
defensible version ([[Canonical Document IR for Ingest]]).

## See Also
- [[Timebox-Scaled Deliverable Bar]] — extends (how the bar shifts with the window)
- [[System Design Interview Study Guide]] — extends (the live-round counterpart)
- [[Right-Sizing a Document-to-LLM Pipeline]] — prerequisite-for (the architecture being presented)
- [[Length Limits Are a Fit Layer, Not a Prompt]] — extends (the critical path worth deepening)
