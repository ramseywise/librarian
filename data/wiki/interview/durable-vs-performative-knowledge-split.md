---
title: Durable vs Performative Knowledge Split
tags: [interview, llm, pattern]
summary: One test — "is this true regardless of whether I'm being interviewed?" — sorts study material into durable technical knowledge and interview-performance technique, which decay at different rates and need different revision cadences.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/learn-ai-engineering/docs/plans/2026-07-30-LAE-112-interview-notes-reorg.md
---

# Durable vs Performative Knowledge Split

A corpus of interview-prep notes had accumulated into flat folders where technical
substance and round-specific technique were interleaved. The reorg turned on a single
question applied to every file:

> *"Is this true regardless of whether I'm being interviewed?"*
> Yes → `guides/`. No → `rounds/`.

The worked examples make the boundary sharp:

- *"Separate read and write tools"* — true at work → **guide**
- *"Draw the architecture in under 3 minutes"* — only true in an interview → **round**

**This is the single decision that drives the whole reorg.** Every placement follows
from it; nothing needed a second criterion.

## Why the axis is worth the churn

The two bodies of material have different half-lives and different revision triggers.
Durable knowledge changes when the technology changes — a new orchestration pattern, a
shifted cost curve. Performance technique changes when the format changes, or when a
mock reveals that a rehearsed line lands badly. Filing them together means every pass
over the notes touches both, and neither gets revised on its own schedule.

There is a second effect: durable content written *for* an interview acquires a
distortion. It is compressed toward what is sayable in three minutes rather than what is
true, and it accumulates hedges and framing aimed at an examiner. Separating the folders
removes the pressure to write knowledge in performance voice.

## The missing middle

The split alone left a gap. The round's method file was a **5-step process** — too
abstract — and the guides were the full technical treatment — too deep. Nothing sat
between them at the grain an actual question demands. That gap is what
[[Situation-Indexed Decision Tree]] fills: a round-side artifact that indexes *into* the
guides rather than duplicating them.

So the structure is three layers, not two: process (how to run the round) → decision
tree (which way to go, given the question) → guides (what is actually true).

## Reversal: do not merge the compiled version back into raw

The same reorg produced a decision worth recording, because the instinct ran the other
way first. A raw `notes/security.md` was slated to merge into the security guide. The
diff killed it:

> The guide is *already the compiled version* — source→sink, `<untrusted_content>`
> markers, and memory poisoning all appear in guide §2–4, tightened. The note is the raw
> Notion export. Merging would **push raw material back into a finished artifact and undo
> the compile.**

Only genuinely unextracted content moved across — long code blocks (restricted shell,
circuit breaker, memory validation) that the compile had never absorbed. And the
operative instruction: **verify unextracted-ness during the phase, don't assume it.**

A related unresolved case: a `notes/foundations.md` marked `origin: synthesized` is a
*derived* artifact sitting in a raw-input folder. It either belongs in the guides or
`notes/` needs a `synthesized/` subfolder. Deferred, because it requires a call on what
`notes/` means — the split rule sorts durable from performative, but says nothing about
raw versus compiled. See [[Karpathy LLM Wiki Pattern]] for the same source/output
boundary held explicitly.

## Conventions the split establishes

1. **Provenance frontmatter on every file** — `origin`, `confidence`, `sources`,
   `cleaned`. This gives *"from a YouTube transcript, medium confidence"* a structured
   home **so it stops leaking into prose.** Uncertainty stated in a field is checkable;
   uncertainty hedged into sentences is unremovable.
2. **Strip preamble on ingest** — content starts at the `#`. Anything the model said
   *about* the notes ("These are excellent resources…", "Here are condensed interview
   notes…") goes into `sources:`, not the body.

## See Also
- [[Situation-Indexed Decision Tree]] — extends (the layer between process and guides)
- [[System Design Interview Study Guide]] — instance-of (the round-side method file)
- [[Karpathy LLM Wiki Pattern]] — complements (raw vs compiled, the other filing axis)
- [[Agents Interview Study Guide]] — complements (durable-side content this rule files)
- [[Timebox-Scaled Deliverable Bar]] — instance-of (round-technique material, format-specific and therefore performative)
