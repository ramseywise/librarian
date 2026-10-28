---
title: Prompt Re-Asks What the Gate Proved
tags: [prompting, eval, pattern]
summary: "When a deterministic precheck short-circuits failing inputs before the model call, any prompt question restating a precheck rule asks the model to re-verify a fact that is already certain on every input it sees — remove those bullets, render the remaining checklist from one prose map keyed by the precheck's reason union, and add a substring test so the duplication cannot return."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-24-dis384-measurement-loop.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-24-dis384-measurement-loop.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-24-dis384-measurement-loop.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-24-dis384-measurement-loop.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-24-dis384-measurement-loop.md
---

# Prompt Re-Asks What the Gate Proved

A QC agent in akira ran a deterministic precheck first and called the model only on
inputs that passed it. The model prompt's `Check:` list still asked four questions the
precheck had already answered: "is this an event?", "is it not a listing page?", "does
it have an event-specific URL?", "are title, date and venue plausible?". Each one mapped to
a precheck reason code (`missing_title`, `start_at_past`, `source_url_is_listing_root`,
`title_matches_venue`, and so on).

## Why it is a defect, not redundancy

The precheck short-circuits to a zero-model-call verdict the moment it fails. So **every
prompt that reaches the model is one where those four facts are already established
true.** The bullets cost tokens on every call and invite the model to contradict a
certain result. Worse, they are a hand-copied rendering of rules that live in code. When a
precheck rule changes, the prompt silently keeps asking the old question. This is the
prompt-side case of [[Derive the Gate, Don't Copy It]].

## The fix

1. Next to the precheck's reason union, export a `REASON_PROSE: Record<Reason, string>`
   map: the human question each reason answers. Because it is keyed by the union, a new
   reason cannot be added without prose (the type checker enforces it).
2. The prompt renders its `Check:` list from a constant of **model-owned questions only**:
   "is there enough information for a user?", "is the enrichment plausible?", "are there
   signs of duplicates or source-quality problems?". These are judgements no deterministic
   rule can make.
3. Two tests: every reason has non-empty prose, and the rendered prompt contains none of
   the prose values as a substring. Prove the second test bites by reverting the fix
   locally and watching it fail.
4. Bump the prompt version (`ai_qc_v1` → `ai_qc_v2`), so old and new stored verdicts stay
   distinguishable. Record the removed bullets in a dated header comment as an intentional
   divergence from the original workflow export.

A review later flagged one limit: the substring test catches only *verbatim*
re-duplication. A paraphrase of a precheck question would pass. The header comment should
not claim a stronger guarantee than the test gives.

## When it is *not* the same defect

The same plan audited a second pair: an enrichment prompt asking the model for an
`information_completeness` self-report, and a deterministic `inputCompleteness` module
counting evidence (description length, venue, date, price). That pair is **not**
duplication. The deterministic check exists *because* the gate used to trust the model's
self-report with no independent check. A subjective self-report and an objective evidence
count are two different questions, and comparing them is the point. The audit recorded "no
drift" as a dated note, because the requirement was an outcome either way, not silence.

The test to tell them apart: is the model being asked to **re-derive a fact a gate already
computed with certainty** (remove it), or to **give a judgement that a deterministic check
cross-examines** (keep both)?

## See Also
- [[Derive the Gate, Don't Copy It]] — extends (the prompt as one more hand-copied rendering)
- [[Evidence-Labelled Generation with Deterministic QC]] — related (rules own facts, the model owns judgement)
- [[Confidence That Is Not a Probability]] — related (the self-report a deterministic check cross-examines)
- [[UNGATED Metric Convention]] — related
