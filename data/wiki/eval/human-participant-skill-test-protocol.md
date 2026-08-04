---
title: Human-Participant Skill Test Protocol
tags: [eval, llm, pattern]
summary: Usability-testing a conversational skill with real first-time users — pre-registered facilitator expectations, scripted plus real scenarios, non-intervention rules, and a severity-sorted friction log that feeds fixes back before the next session.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/docs/test-protocols/discovery-pipeline-test.md
---

# Human-Participant Skill Test Protocol

A simulated-user harness ([[Skill Pipeline Dryrun Testing]]) can regression-test a
conversational skill against fixed scenarios with known-correct answers. It cannot tell
you whether a real person understands the questions. This protocol is the other
instrument: 2–3 volunteers who have **never used the template before**, 30 minutes each
(20 active, 10 debrief), with a facilitator who is *"ideally not the author."*

The participant mix is specified, not incidental: one with an engineering background,
one without, one bringing a real project. Skill prose written by an engineer reads fine
to engineers; the non-engineer is the actual measurement.

## The real scenario is the valuable one

Two participants get scripted scenarios (a benefits-eligibility clinic; a youth mentoring
program). The third is asked for something real:

> A scripted scenario **can't surface confusion that only arises from real-world
> ambiguity.**

Scripted cases are authored by someone who already knows which archetype is correct, so
they are unconsciously written to be classifiable. A real situation arrives without that
courtesy — it straddles archetypes, has three pain points instead of one, and includes
constraints the skill never anticipated.

## Pre-registering the expected answer

The strongest methodological choice sits inside a success criterion:

> The profile's archetype matches the facilitator's independent assessment — **the
> facilitator writes their expected archetype BEFORE the session.**

Judging archetype correctness after watching the conversation is unreliable; the
facilitator has by then absorbed the skill's own framing and will tend to ratify
whatever it produced. Committing to the answer in advance turns a subjective call into a
falsifiable one. This is the same discipline as declaring a hypothesis before looking at
the data.

## Observation as a signal table, not impressions

The facilitator watches for enumerated behaviours, each pre-assigned a meaning and a
severity — so classification happens during the session rather than in recall afterward:

| Signal | What it means | Severity |
|---|---|---|
| *"What do you mean?"* | Jargon or unclear prompt | Medium |
| *"I don't know"* to a question | Question assumes expertise they lack | **High** |
| Long, unfocused answer | Question too broad; needs narrowing | Low |
| Picks the wrong archetype | Archetype descriptions unclear | **High** |
| Hesitates at "must-demonstrate" | Needs more prompting/examples | Medium |
| Final profile has blank sections | Skill didn't elicit the information | **High** |
| Copier hints don't match intent | Mapping logic is wrong | **High** |
| *"This is what I thought"* at confirm | Working as intended | positive |

The last row matters: a protocol that only records problems produces a document in which
the skill appears uniformly broken. Naming the positive signal keeps the log calibrated.

## Non-intervention rules

Facilitator behaviour is constrained in both directions, because both over- and
under-helping destroy the measurement:

- **Do intervene** — stuck > 60 seconds (note *what* they're stuck on first, then help);
  about to answer with clearly wrong information (note the confusion, then correct).
- **Don't intervene** — they're thinking or reading; silence is fine.
- **Don't intervene** when they pick a "wrong" answer — *"that's a test finding, not a
  mistake."*

That last rule is the one that requires discipline. The author's instinct is to correct a
participant heading toward the wrong archetype, and doing so deletes exactly the finding
the session exists to produce.

## Tiered success criteria

Nine criteria in three bands, each with a defined consequence:

- **Must-pass** (any failure blocks shipping) — valid profile with no section blank and
  no more than **two** *"what does that mean?"* moments across the session; archetype
  matches the pre-registered expectation; the profile → `/scope-poc` handoff pre-fills at
  least 3 of 5 mapped fields; **under 20 minutes** end to end.
- **Should-pass** (fix, don't block) — participant never needs to read the reference
  cards themselves; every copier hint is valid; the profile *"sounds right"* on first
  presentation.
- **Nice-to-have** — unprompted positive feedback; the real scenario yields a profile the
  facilitator finds reasonable.

Two of the must-pass criteria are quantified thresholds on *confusion* rather than on
output — a count of clarification requests and a wall-clock ceiling. Correctness alone
would pass a skill that takes 45 minutes and confuses people six times.

## Friction log and fix priority

The same three-part entry discipline as the automated harness — step, what happened
(verbatim where possible), what they expected, severity, suggested fix — with severities
defined by their effect on progress:

| Severity | Definition | Action | Timeline |
|---|---|---|---|
| `blocks-progress` | Cannot continue without help | Fix immediately, re-test | Before next volunteer session |
| `confusing` | Uncertain but continues (may produce wrong output) | Fix next sprint | Within 1 week |
| `cosmetic` | Notices something odd; outcome unaffected | Backlog | When convenient |

The `confusing` tier carries the parenthetical that justifies it existing separately:
the participant continues, so the session *completes*, but the output may be wrong. A
binary pass/fail scheme files these as passes.

Post-test the entries are sorted by severity, **grouped by skill step** (which step
attracts the most friction), and checked for patterns across participants — one person's
confusion is anecdote; three people confused at the same step is a defect. Every
`blocks-progress` item is fixed before the next round, then `/design-dryrun` re-runs to
confirm no regression.

## The debrief is the part automation cannot replace

Five verbatim-recorded questions, ending with *"Would you use this again for your next
project? Why or why not?"* — and the note that *"these are the design insights that
automated testing can't surface."* The two instruments are complementary by construction:
the dryrun catches regressions cheaply on every skill edit; the human protocol catches
the comprehension failures the dryrun's known-correct scenarios are blind to.

## See Also
- [[Skill Pipeline Dryrun Testing]] — alternative-to (simulated user vs. real first-time user)
- [[Project Discovery Conversation]] — instance-of (the skill under test)
- [[Conversational Test Fixture Design]] — complements (authored scenarios vs. live participants)
- [[AI Project Archetypes]] — extends (the pre-registered assertion target)
- [[NYC-DSSG Project]] — instance-of (the volunteer population tested)
