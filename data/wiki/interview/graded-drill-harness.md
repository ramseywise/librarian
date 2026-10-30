---
title: Graded Rehearsal Drill Harness
tags: [interview, meta, pattern]
summary: Three sibling Claude Code skills (spoken answers, coding questions, assessment environments) that share one harness design — explicit coach/mock stance, a spoiler gate on worked solutions, the learner types every character, a process rubric graded strictly, and an append-only content-free history log keyed by stable question ids that the question generator must preserve.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/sisyphus/skills/coding-drill/SKILL.md
  - data/raw/claude-docs/sisyphus/skills/env-drill/SKILL.md
  - data/raw/claude-docs/sisyphus/skills/interview-drill/SKILL.md
  - data/raw/claude-docs/sisyphus/skills/interview-prep/SKILL.md
  - data/raw/claude-docs/sisyphus/docs/plans/2026-08-06-interview-companion.md
  - data/raw/repos/sisyphus/.claude--docs--plans--2026-08-06-interview-companion.md
  - data/raw/repos/sisyphus/CLAUDE.md
  - data/raw/repos/sisyphus/drills--README.md
---

# Graded Rehearsal Drill Harness

The sisyphus repo separates *preparation* (a skill that writes a question bank) from
*rehearsal* (skills that drill it). Three rehearsal skills — `interview-drill` (spoken
answers), `coding-drill` (code typed in the editor against a fixed bank) and `env-drill`
(the clock and rubric of a specific assessment environment) — converged on the same harness.
None of them authors questions; each is explicitly "a harness".

## Stance is explicit and binary

| | **coach** (default) | **mock** |
|---|---|---|
| Help | On request, via the [[Hint Ladder With Logged Aid Rung]] | Clarifications only, in character as the interviewer |
| Clock | Advisory, reported | Enforced; stops at the buzzer — unfinished is a result |
| Use | Learning a pattern, or after repeated misses | Measuring readiness close to a real loop |

An item starts in coach if new or flagged open, and moves to mock only once solved at Aid
≤1. "Coach passes prove understanding, not performance." A log with no mock rows is called
out plainly: coach is comfortable and measures nothing.

## Guardrails that protect the measurement

- **Spoiler gate.** Worked solutions are never read into context before the attempt ends —
  "not to check the expected answer, not to phrase the prompt better" — because there is no
  second first attempt. The prompt comes from a file that states what is tested without the
  answer; the solution is read only after scoring, for comparison.
- **The learner types every character.** Placing a starter file before the clock is the
  only write. Watching correct code appear produces recognition, not recall.
- **Starters are stubs, not skeletons**: prompt as docstring, the clarifications an
  interviewer would give, given signatures raising `NotImplementedError`, one happy-path
  assert. No edge-case tests — finding those *is* the T grade.
- **Never soften the grade; never extend the mock clock.**
- **Verify by running.** Claims about what code does come from executing it. This caught a
  "dead" fallback that was load-bearing and an optimisation that silently broke a standard
  case (cf. [[Fallback Mistaken for the Design]]).

## Process rubrics, graded strictly

Each skill scores the process the evaluator watches, with a fixed letter set so rows are
comparable across sessions:

- **Coding:** C clarified · P planned (structure + complexity before code) · N narrated
  (decisions, not keystrokes; never silent >60 s) · T tested (traced or tested empty and
  single-element before "done"). C and T are graded strictly — "a correct solution with
  C✗ T✗ is a worse interview performance than a half-finished one with C✓ P✓ N✓."
- **No-AI comprehension/bug-hunt:** Diagnosed (defect, not symptom) · Traced (concrete
  values) · Structures (real identifiers and types) · Why · **Fix stated** · Security scan.
- **AI-allowed feature build:** Plan before first prompt · I/O contract per prompt ·
  Verified after each generation · Reviewed (caught a wrong-fit, verbosity,
  over-abstraction or correctness shortcut) · Shipped a slice by the 2/3 mark · Cuts stated.
- **Spoken recall:** facts survived · close landed · length · register.

The rubric source is the question bank's own "key signals" and "common pitfalls"; the
harness must not invent signals, only flag that the bank may be missing one.

## Talk → type escalation

Pass 1 is cheap and wide (5–8 min per question, spoken approach, interviewer-style indirect
probes — "this needs to serve millions of requests a day", not "tell me about SQLite's
write lock"). No redrafting in this pass. Anything that failed C or P, hit a pitfall or
needed a hint becomes Pass 2, typed in the editor. A talk-only pass "is not evidence".

## Seeded bugs must be silent

When authoring bug-hunt material, the bugs that teach are those that **pass the existing
tests**: identical if/else branches, offsets that appear to cancel, slices that skip an
element, order dependence, mutation before validation, early returns that skip bookkeeping.
"A bug that throws on the happy path teaches nothing." Problems already seen are never
reused; untouched bank problems get bugs seeded into them.

## The history log carries no content

Each skill keeps an **append-only** markdown table — date (suffixed `?` if inferred), qid,
stance/mode, time, Aid, score, an open-item flag, one-phrase note. It carries **no answer
or solution text**: "Two records of the same answer would drift; one record plus a history
file cannot." Replacing an answer is a new row, never an edit. Clean recall scores are
logged too — "a run of passing rows is what makes a later regression legible."

**Stable qids span two skills.** A qid is stamped as an HTML comment under a question
heading the first time it is drilled and never changes. The *generator* skill
(`interview-prep`) is obliged to carry qids through regeneration: same test, reworded →
keeps its qid; rewritten to test something else → no qid, old id retired, its log rows
remain valid history. A bootstrap rule backfills qids and rows from existing rehearsed
blocks with approximate dates that "self-correct after one recall pass".

## Selection is computed from the log

Least-recently-drilled, weighted: open items first; last-solved-at-Aid≥2 outranks
never-seen; talk-passed-but-never-typed outranks never-seen; untested environments and
zero-coverage topics (security, OOD) outrank the rest. Position is reported in one line
before asking. Trend reads matter more than the scores: recurring T✗ (tests-first not yet
reflex), talk✓/type✗ (a fluency gap, not a concept gap), the same pitfall across different
questions ("one concept gap, not two question gaps").

## Porting the harness to a new companion

A plan to reuse this harness for a different interview loop concluded: **port the pattern,
not the code** — an append-only ledger derived from sessions, not the skill files. It also
found that the "pick what is due" selection rule was unexecutable as written because **no
timestamp was recorded anywhere**; a selection rule is only as real as the fields the log
actually stores (a Stop-hook writer was proposed to timestamp rows).

## See Also
- [[Hint Ladder With Logged Aid Rung]] — extends (the coach-stance help policy)
- [[Voice-Preserving Redraft Loop]] — extends (the spoken-answer drill loop)
- [[Evidence-Gated Skill Pipeline]] — extends (the preparation pipeline whose output this harness drills)
- [[Append-Only Log Writer Invariants]] — prerequisite-for (the writer contract the drill logs rely on)
- [[Durable vs Performative Knowledge Split]] — extends (rehearsal targets performative knowledge)
- [[Code Review Drill — SANYI]] — alternative-to (a single worked drill rather than a harness)
- [[Drill Gym Tracks and Schema]] — complements (the drill content format the harness grades)
- [[AI Engineering Field Question Bank]] — complements (questions-only bank for cold recall)
