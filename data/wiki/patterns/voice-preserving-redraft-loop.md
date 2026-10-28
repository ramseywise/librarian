---
title: Voice-Preserving Redraft Loop
tags: [interview, prompting, pattern]
summary: When an LLM co-writes text that a person must later speak or sign as their own, name the phrases to keep before critiquing, flag every sentence the model invented, let the person rewrite last, record their words verbatim, and promote a style observation to a standing voice file only on its second occurrence — otherwise each redraft sands the text toward the model's register.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/sisyphus/skills/interview-drill/SKILL.md
  - data/raw/claude-docs/sisyphus/skills/env-drill/SKILL.md
---

# Voice-Preserving Redraft Loop

The sisyphus `interview-drill` skill exists because model-redrafted answers kept reading as
"better but not like me." The fix is not a better prompt for tone; it is a loop whose
ordering and recording rules make drift toward the model's register structurally hard.
`env-drill` reuses the same loop for spoken explanations of code.

## The loop

1. **Ask cold** — no preamble, no hint about the trap.
2. **Take the raw answer** — often disfluent transcribed speech. Work with content, never
   comment on delivery mechanics.
3. **Critique in a fixed order:**
   - **Strongest first, quoted exactly.** This is said to matter *more* than the criticism:
     the person needs to know which of their own words to protect, "because the next
     redraft will otherwise sand them off."
   - What's missing (checked against a recurring-gaps list).
   - What's weak or risky — contradictions with other recorded answers, claims not in the
     evidence store, anything that reads as arguing or hedging.
   - Structure — usually placement, not content: the good material is present but
     sequenced so the answer gets vaguer toward the end.
   No praise-as-cushion; adversarial was explicitly requested.
4. **Redraft using their clauses verbatim** where possible — change sequence, cut
   duplication — and **flag every sentence the model invented**. A smooth inference reads
   as a claim to someone fact-checking against their own record.
5. **They rewrite.** Expect their version to beat the model's on content; when it does, say
   so and name which choices were better, then fix only what is genuinely still wrong.
6. **Record when settled** — their final version **verbatim**, fixing only transcript
   artifacts. "Never polish at write time — polishing is what makes the docs stop sounding
   like the speaker."

## Recording shape

The recorded block carries the answer plus three things that keep it honest later:

- **Why this works** — structural reasons tied to what the questioner is actually testing.
- **Held back — deploy only if asked "…"** — precise material kept in reserve. Detail
  deployed too early leaves the follow-up with nowhere to go; anything cut for length
  usually belongs here, not in the bin.
- **Open** — only real uncertainty (an unverified number, an attribution). "Never invent an
  open item to look thorough."

## The voice file, promoted on the second occurrence

A standing `voice-notes.md` holds register traits to preserve, recurring content gaps, and
pressure-specific failure modes (e.g. doubt-implying questions trigger arguing). A pattern
is added **only when it shows up twice** — "one instance is an accident, two is a habit."
It is read at the start of every session so redrafts stop drifting.

The annotations that recur most in the source are worth naming because they generalise to
any technical explanation:

- **Downgraded strong ideas** — "probably less important" attached to the best point in
  the answer. Flag every time.
- **Hedges that concede the case just made** — delete the concession, don't argue it.
- **Algebra where arithmetic would land** — "n minus one" where "2 cells counted against 3"
  is clearer; coordinates over axis words.
- **Described-not-named** — "it's stored on the board" instead of the identifier.
- **Stopped at recognition** — found the problem, never stated the fix.

## Recall can overwrite the record

In cold-recall mode the person answers from memory, scored on four deterministic checks
(facts survived, close landed, under 90 s, register held). If the from-memory version is
*better*, it replaces the recorded one — "memory drops what didn't matter." The replacement
is a new log row, never an edit to an old one.

## See Also
- [[Graded Rehearsal Drill Harness]] — instance-of (the skill family this loop lives in)
- [[Evidence-Gated Skill Pipeline]] — extends (every recorded claim must trace to the same evidence store)
- [[Hint Ladder With Logged Aid Rung]] — alternative-to (help policy for typed attempts rather than spoken ones)
- [[Grounding Claim Methodology]] — extends (flag invented sentences as ungrounded claims)
