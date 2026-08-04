---
title: Wander — Question-Generating Review Agent
tags: [llm, pattern]
summary: A review agent that produces 3–5 pointed questions instead of findings — surfacing intent, edge cases, walked-past decisions, blast radius, and the conspicuously absent thing — as the "yin" complement to defect scanners.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/guacamayo/agents/wander.md
---

# Wander — Question-Generating Review Agent

`wander` is a dimension agent in the `/akira` review system whose output type is
**questions, not findings**. Where scanners hunt concrete defects, wander surfaces *the
questions the change raises but doesn't answer*. Its self-description: "You are not a bug
finder — you are a thinking partner." It is always dispatched, alongside the scanners.

Prefix `WD-`. Model `haiku`. Read-only.

## The five question categories

1. **Intent** — what is the change trying to achieve, and does the code match?
   *"This adds a retry loop — is the failure it's guarding against transient, or are we
   masking a real error?"*
2. **Edge cases** — inputs/states the change doesn't visibly handle.
   *"What happens when `items` is empty here — is the early return intended, or an
   accident?"*
3. **Missing decisions** — the fork the author walked past without marking.
   *"You picked in-memory caching — was persistence considered and rejected, or just not
   reached yet?"*
4. **Blast radius** — who else touches this, and did they get updated?
   *"Three callers pass the old signature — are they in this diff or a follow-up?"*
5. **The unasked question** — the conspicuously absent thing. Tests? A config default? An
   error path? A doc that now lies?

## The rules that make questions useful

The prompt is mostly a list of ways a question agent degrades, each closed off:

- **"Read before you ask."** A question answerable by reading one more file is a wasted
  question. Check callers with Grep; read the neighbors. This is the load-bearing
  constraint — without it a question agent becomes a way to avoid doing the work.
- **"Specific, not generic."** *"Did you consider edge cases?"* is explicitly **banned**.
  Every question must reference something concrete — a line, a symbol, a path.
- **"Questions, not findings."** Not "bug at line 42" but "line 42 assumes `x` is
  non-null — is that guaranteed upstream?"
- **3–5, ranked**, most-load-bearing first. "Fewer sharp questions beat more dull ones."
- **Don't manufacture doubt.** If the diff is trivial and raises nothing real, say so in
  1–2 questions rather than padding to five.
- **Respect the repo's CLAUDE.md** — don't question a deliberate, documented choice.

## Fixed schema position

Wander output pins both axes of [[Merge Impact and Evidence State]]:
`merge_impact: question` and `evidence_state: question`, always. This keeps questions from
competing with defects in the merge-decision ranking — they are a parallel output stream,
not low-severity findings.

## Why a question agent at all

Defect scanners can only find things that are *wrong in the code as written*. They are
structurally blind to the decision that was never made, the alternative never evaluated,
and the test never written — absences leave no line to flag. Wander covers that gap by
changing the output type rather than the checklist, and the anti-padding rule is what
keeps it from filling the gap with noise.

## See Also
- [[Parallel Dimension Scanner Architecture]] — extends
- [[Merge Impact and Evidence State]] — extends
- [[Claude Workflow System]] — instance-of
