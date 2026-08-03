---
title: Skill Pipeline Dryrun Testing
tags: [eval, pattern]
summary: Regression-testing a chain of conversational skills by simulating a user through fixed scenarios with unambiguous expected outcomes — asserting not only what the pipeline produces but which questions it correctly skips and which it must still ask.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/skills/design-dryrun/SKILL.md
---

# Skill Pipeline Dryrun Testing

A conversational skill pipeline has no test suite in the ordinary sense — its output is a
document produced through dialogue, and its correctness includes *what it chose not to ask*.
`/design-dryrun` is the regression harness for one such pipeline
([[Project Discovery Conversation]] → [[Scope-POC Design Interview]] → `/project-genesis`):
simulate a volunteer walking the whole chain with sample scenarios, and assert at each
handoff.

## Fixed scenarios chosen for unambiguity

Three scenarios, one per archetype, each a realistic nonprofit pain point paired with the
outcome it must produce:

| Scenario | Pain point | Expected archetype | Expected `project_type` |
|---|---|---|---|
| A — Meeting transcripts | *"20 volunteer tutors meet weekly, nobody tracks decisions or follow-ups"* | Workflow Automation | `workflow` |
| B — Tenant rights FAQ | *"Volunteers spend 3 hours per intake looking up applicable housing regulations"* | Information Retrieval | `rag` |
| C — Grant report drafting | *"Apply for 15 grants/year, each report is 8 pages, 60% is the same info"* | Document Generation | `agent` |

The selection criterion is what makes the harness usable:

> *"Expected values are assertions, not suggestions. A scenario that produces the wrong
> archetype is a FAIL — not 'close enough.' The scenarios were chosen because they have
> clear, unambiguous correct answers."*

A pipeline whose output is judgment-shaped can still be regression-tested if the test inputs
are deliberately restricted to cases with no defensible second answer. Ambiguous scenarios
would make every failure arguable and the harness worthless. This is the same discipline as a
golden set that excludes genuinely contested cases — see [[Golden Set Mechanics]].

## Asserting the skips, not just the output

The distinctive checkpoints are the ones about **which questions the second stage asks**.
Consuming an upstream artifact correctly means two symmetric obligations, and both are
asserted:

- **Pre-filled fields are confirm-only, not re-asked** — pain point, archetype,
  must-demonstrate, capacity, and out-of-scope all arrive from the profile and must be
  presented for ratification rather than interviewed again.
- **The remaining questions are still asked normally** — actors and roles, system boundaries,
  data classification, evaluation metrics and the naive baseline, top risks.

The second half is the one a naive implementation breaks. A skill that gets eager about
"the profile already told me" silently skips questions the profile never answered, and the
resulting DESIGN.md looks complete while missing its constraints. Testing only the output
document would not catch it; testing the question set does.

This asserts at the artifact-handoff boundary, which is where a pipeline of independently
edited skills actually drifts.

## Three stages of checkpoint

1. **Discovery** — correct archetype; profile contains every required section (concrete
   pain-point language, org context, 3–5 must-demonstrate items, capacity constraints, ≥1
   explicit out-of-scope item); and **hint self-consistency** — Workflow Automation implies
   `project_type=workflow`, a weekend sprint implies `deployment_target=local`, external
   users imply `primary_users` of `customers` or `public_api`.
2. **Scope** — the profile is found and read; the right fields are confirm-only; the right
   questions survive; DESIGN.md has all its sections.
3. **Copier validation** — every referenced parameter exists in `copier.yaml`, every value is
   within its declared choices, and no pair contradicts (`project_type=prototype` with
   `deployment_target=cloud`).

Stage 3 is deliberately bounded: *"copier validation is syntactic, not semantic. Check that
parameter names and values are valid; don't actually render (that's what CI does."* The
dryrun tests the conversation; CI tests the render. Overlapping them would make the dryrun
slow and dependent on the environment.

## The friction log

Output is a friction log rather than a pass/fail exit code — a per-scenario checkpoint table
(expected / actual / PASS-FAIL) plus friction entries and ranked recommended fixes.

The entry format is constrained to keep it actionable:

> *"Every friction entry names three things: what happened, what should have happened, and
> which file/line to fix. Vague entries ('felt confusing') are not acceptable."*

Without that rule the log degenerates into impressions, which is the default failure mode of
qualitative testing. The three-part form makes each entry a work item.

## Single-session constraint

*"The dryrun must complete in a single session. No multi-turn dependencies, no 'come back
tomorrow.'"* A checkpoint needing external input (API keys, a real copier render) is
**skipped with a note rather than blocking** — the same degrade-don't-block choice that keeps
the harness runnable on every skill change instead of only when the environment is fully
provisioned.

The trigger for running it is any edit to `/project-discovery`, `/scope-poc`,
`/project-genesis`, or the reference cards — those changes *"should not introduce friction
that wasn't there before."*

## See Also
- [[Skill Eval Pipeline (Blind Comparison + Grading)]] <!-- auto-linked -->
- [[Project Discovery Conversation]] — prerequisite-for (stage 1 under test)
- [[Scope-POC Design Interview]] — prerequisite-for (stage 2 under test)
- [[AI Project Archetypes]] — extends (the assertion target for stage 1)
- [[Golden Set Mechanics]] — alternative-to (fixed cases for a deterministic pipeline rather than a model)
- [[Eval-Driven Development (EDD)]] — instance-of (a regression harness gating skill edits)
- [[Asked vs Derived Scaffold Variables]] — extends (stage 3 validates the hint→parameter mapping)
