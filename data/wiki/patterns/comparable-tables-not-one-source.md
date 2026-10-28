---
title: Comparable Tables, Not One Source
tags: [patterns, llm, pattern]
summary: "When several hand-transcribed vocabulary tables describe the same field at different pipeline stages, keep them separate and pin their agreement with a test instead of deriving them from one source — merging would have resolved a real cross-stage disagreement silently, in one direction, with no record of which stage was right."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-05-dis151-waslosheute-fit-vocabulary.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-05-dis151-waslosheute-fit-vocabulary.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-05-dis151-waslosheute-fit-vocabulary.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-05-dis151-diskoe-fit-vocabulary.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-05-dis151-diskoe-fit-vocabulary.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-05-dis151-diskoe-fit-vocabulary.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-05-dis151-diskoe-fit-vocabulary.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-06-dis151-diskoe-fit-vocabulary.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-06-dis151-diskoe-fit-vocabulary.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-06-dis151-diskoe-fit-vocabulary.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-06-dis151-diskoe-fit-vocabulary.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-06-dis195-prompt-vocabulary.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-06-dis195-prompt-vocabulary.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-06-dis195-prompt-vocabulary.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-06-dis195-prompt-vocabulary.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-06-dis195-prompt-vocabulary.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-06-dis195-prompt-vocabulary.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-06-dis195-prompt-vocabulary.md
---

# Comparable Tables, Not One Source

Found in the diskoe enrichment chain (`sanitize → validate → gate → flatten`), ported from
low-code workflow nodes. One fit-score field for one content type was described by three
tables, each transcribed from a *different* original node:

| Table | Values | Decides |
|---|---|---|
| validator allow-list | `strong, standard, weak, not_recommended` | whether the row is flagged |
| storage map (flatten) | `strong, medium, weak, unclear` | what the column can physically hold |
| sanitize allow-list (added by the preceding fix) | `strong, medium, weak, unclear`, fallback `unclear` | what reaches validate |

They overlapped on two values. The disagreement was authentic — two nodes in the same
original workflow disagreed — not a porting error.

## Two symptoms, opposite directions

- **False invalidation.** A legitimate `medium` was stored correctly but failed validation,
  setting `needs_review` for nothing.
- **Silent corruption.** A validator-legal `standard` passed validation and was then written
  raw into a capitalised column, because the storage map's fallback was a passthrough.

The preceding sanitize fix closed the second symptom and **made the first systematic**: its
fallback, `unclear`, was itself validator-illegal, so every out-of-vocabulary model output
now landed on `needs_review`. The false-positive rate stopped being a function of how often
the model said `medium` and became a function of how often sanitize coerced. The
plan's instruction: measure the invalid rate before and after, and attribute a jump to this
defect, not to the earlier fix.

## Widen the validator, do not narrow the writer

The storage map is authoritative because the column is the constraint: 84 existing rows
already held `Medium`/`Unclear` correctly. Narrowing the map to the validator's set would
have corrupted them on their next enrichment run. So the validator was widened — recorded
as an intentional divergence from its original node, with a comment saying *do not
regenerate this entry from the original without re-deciding*, because the tables were
generated and the next regeneration would silently revert the fix.

## Why not derive all three from one list

The repo's own convention warns against a second hand-maintained list. The plan's answer:
that warning is aimed at lists that are *supposed to be identical*. These are supposed to
be **comparable** — each records what one real stage did — and keeping them apart is what
made the comparison possible. Had they been unified earlier, the disagreement would have
been resolved at merge time with no record of which node was right, and neither symptom
would have surfaced.

Drift protection comes from a test instead:

- the key sets agree for the affected type, and
- the invariant set-equality does not imply: **every sanitize fallback is a key in that
  type's storage map and is validator-legal.** Parameterised over all content types, so the
  sibling types inherit the guard.

The agreement test was required to be shown **red against the pre-fix tree** — written after
the fix, it proves only that the code matches itself.

## What review found the plan missed

- **The prompt was a fourth vocabulary.** The enrichment prompt and its worked example still
  taught the model the old set. `standard` and `not_recommended` were silently rewritten to
  `unclear` before validation, so a middling-fit judgment was stored as "we don't know" —
  and the "legitimately `Unclear`" rows the plan used as headline evidence could not be taken
  at face value. The agreement test covered three of the four tables. The instruction to the
  model is part of the vocabulary set.
- **A fixture eval gated at 1.0 that could not fail.** All eight fixtures used `strong`, the one
  value common to old and new vocabularies, so the metric would pass with the field's
  validation entirely broken. The fix added a *bidirectional* fixture — new value validates
  clean **and** old value is rejected — so a revert fails it twice.
- **The contract doc still listed the old enum**, after a scout claimed it had checked the
  file. Verified by the orchestrator rather than accepted on report.
- **A mirror of an external record is not rewritten.** A local copy of a wiki page still
  listing the old set got a dated inline "superseded" note with the original text kept —
  rewriting a mirror destroys its value as a record.
- **Clearing stale review flags is a separate decision.** `needs_review` can be set by other
  reasons on the same row; a blanket clear would unflag genuine review work.

## Closing the Fourth Table: Generate the Prompt, Then Test It Anyway

The follow-up fix moved the prompt to match storage, and it **generated** the prompt's
value list from the sanitizer's constant instead of hand-editing it. This does not
contradict the "keep tables apart" rule above. The prompt is not an independent record of
what some original stage did. It is an instruction that is *supposed to be identical* to
what sanitize accepts, so deriving it is correct. Choices that generalise:

- **Generate and test together.** Generation makes drift structurally harder. A test that
  regex-extracts the rendered `field:\n- value` block and compares it to the sanitizer is
  what actually fails a build if someone reverts the interpolation "for readability", or
  regenerates the file from the original. Regex-parsing prose is safe here only because
  every enum block renders in one fixed, generated-looking format. The extractor throws a
  named "could not find X block" error instead of returning `[]`, so a formatting change
  points at itself rather than reading as a vocabulary regression.
- **Apply generation to every vertical.** Generating only the one that was broken would
  leave "one generated template, two hand-maintained" as a new inconsistency. The other
  verticals' different value set was recorded as a **permanent, accepted divergence**, not
  a staging step toward unifying them, because nothing there was broken.
- **The worked example is asserted legal, not equal.** It holds one scalar, so the test
  checks that the example's value is in the allowed set.
- **The parity suite never covered the prompt.** The differential parity test diffed only
  the short summary string the original node built. The much larger instruction template,
  with every rule and enum list, was never executed or diffed. "No parity test breaks" was
  true because nothing read that text. The gap was named in the parity record as a
  follow-up instead of being quietly relied on.
- **Token agreement is not semantic agreement.** No template ever defined what any fit
  value *means* to the model, so swapping the taught tokens can move the model's
  judgments for reasons unrelated to the alignment fix. A one-off acceptance check was
  added: the same 20 real rows under the old and new prompt, comparing the **raw
  pre-sanitize** output, since sanitize's fallback would hide the shift. It did not gate
  the merge, because it costs real API calls and has variance at small N. A spike in the
  ambiguous value was the trigger for adding semantic definitions. The agent that executed
  the plan had no credentials, and recorded the step as *not executed*, not as passed.
- **Historical rows cannot be reclassified.** Only the post-sanitize payload was stored,
  so whether an old "unclear" was genuine or a rewritten middling value is unrecoverable.
  The only remedy is re-enrichment (see
  [[Sanitize Never Fails, Validate Never Mutates]]).

## See Also
- [[Sanitize Never Fails, Validate Never Mutates]] — extends (the fallback-not-in-vocabulary trap, one stage later)
- [[Differential Parity Testing Against the Original]] — extends (intentional divergence asserted as divergence, not hidden by a loosened matcher)
- [[Derive the Gate, Don't Copy It]] — alternative-to (generate a list when it must be identical; keep lists apart when they must be comparable)
- [[Always-Red Check Carries No Signal]] — related (the mirror image: a fixture that is always green)
- [[Silent Fallthrough in String-Keyed Discovery]] — related (a passthrough fallback writing an unexpected string)
