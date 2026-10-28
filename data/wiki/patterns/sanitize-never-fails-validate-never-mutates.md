---
title: Sanitize Never Fails, Validate Never Mutates
tags: [llm, pattern]
summary: In a model-output pipeline, the sanitize step coerces out-of-vocabulary enum values to a safe fallback and never rejects, while the validate step flags and never rewrites — and the audit of an asymmetry between two content types found the "it is caught later at publish time" containment claim was false because the publish script never read the flag, plus a fallback value that was itself outside the target column's vocabulary.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-05-dis152-activity-enum-gap.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-05-dis152-activity-enum-gap.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-05-dis152-activity-enum-gap.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-05-dis152-activity-enum-gap.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-05-dis152-activity-enum-gap.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-05-dis152-activity-enum-gap.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-05-dis152-activity-enum-gap.md
  - data/raw/claude-docs/akira/docs/research/2026-09-03-dis129-event-enum-escape.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-03-dis129-event-enum-escape.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-03-dis129-event-enum-escape.md
  - data/raw/claude-docs/playground/docs/research/2026-09-03-dis129-event-enum-escape.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis126-ratify-dc2.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis126-ratify-dc2.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis126-ratify-dc2.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-03-dis126-ratify-dc2.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-03-dis126-ratify-dc2.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-03-dis126-ratify-dc2.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis126-ratify-dc2.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis126-ratify-dc2.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis126-ratify-dc2.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis126-ratify-dc2.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-03-dis126-ratify-dc2.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-03-dis126-ratify-dc2.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-03-dis126-ratify-dc2.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-03-dis126-ratify-dc2.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis129-event-enum-escape.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis129-event-enum-escape.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis129-event-enum-escape.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis129-event-enum-escape.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis129-event-enum-escape.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis129-event-enum-escape.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis129-event-enum-escape.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-06-dis196-stale-needs-review.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-06-dis196-stale-needs-review.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-06-dis196-stale-needs-review.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-06-dis196-stale-needs-review.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-06-dis196-stale-needs-review.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-06-dis196-stale-needs-review.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-06-dis196-stale-needs-review.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-06-dis151-waslosheute-fit-vocabulary.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-06-dis151-waslosheute-fit-vocabulary.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-06-dis151-waslosheute-fit-vocabulary.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-06-dis152-activity-enum-gap.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-06-dis152-activity-enum-gap.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-06-dis152-activity-enum-gap.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-06-dis152-activity-enum-gap.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-06-dis152-activity-enum-gap.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-06-dis152-activity-enum-gap.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-06-dis152-activity-enum-gap.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-07-dis195-prompt-vocabulary.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-07-dis195-prompt-vocabulary.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-07-dis195-prompt-vocabulary.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-07-dis195-prompt-vocabulary.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-07-dis195-prompt-vocabulary.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-07-dis195-prompt-vocabulary.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-07-dis195-prompt-vocabulary.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-05-dis129-event-enum-escape.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-05-dis129-event-enum-escape.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-05-dis129-event-enum-escape.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-05-dis129-event-enum-escape.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-05-dis129-event-enum-escape.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-05-dis129-event-enum-escape.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-05-dis129-event-enum-escape.md
---

# Sanitize Never Fails, Validate Never Mutates

An enrichment chain (repo akira) ran model output through `sanitize → validate → gate →
flatten`. The two early stages have opposite contracts:

- **Sanitize never fails.** Every scalar enum is coerced into the allowed vocabulary; an
  unreadable value becomes a fallback (`'unknown'`, or for a fit score `'standard'` —
  "a venue with an unreadable fit signal is treated as ordinary rather than as suspect").
  Output is always writeable.
- **Validate never mutates.** It reads the sanitized row and sets `needs_review` /
  gate status when something is off. It changes no values.

Keeping these separate is what makes each testable by construction: sanitize's tests are
"every output is in-vocabulary", validate's are "input equals output".

## The asymmetry and the false containment claim

Two content types coerced their enums at sanitize time; the third (`event`) coerced
none, on the accepted reasoning that validate would flag a bad value and it would be
"caught later, at publish time, narrower". Reading the publish script in full showed it
**did not read `needs_review` or the gate status at all**. The only thing keeping an
out-of-vocabulary value off the public surface was that the model had never produced
one (0 of 266 rows). Containment that depends on model behaviour rather than code is not
containment. Recommendation: coerce at write time regardless of what publish checks —
and the single fact that would overturn it is publish being fixed to gate on the flag.

## The fallback-not-in-vocabulary trap

Porting the other types' `cleanEnum(value, allowed, 'standard')` to `event` would have
introduced a new bug: `event`'s fit field used a different, capitalised vocabulary with a
*passthrough* fallback in the flatten step, so the literal string `'standard'` — not a
key in the mapping — would have been written verbatim into a column whose values are
`{Strong, Medium, Weak, Unclear}`. A fallback must be checked against the vocabulary of
the column it lands in, after every downstream mapping, not against the vocabulary of the
stage that emits it.

A second cost surfaced: the sanitize vocabulary table was *generated by executing the
original workflow nodes*, and the original `event` node cleaned nothing, so the nine
missing entries would have to be hand-authored — which is invention, not a port, and
should be recorded as an intentional divergence in the parity test rather than hidden.

### No allow-list means "always the fallback" (akira, 2026-09-05)

The sibling `activity` type had the same enum gap, plus a sharper trap in the helper itself:
when `allowed` is `undefined` (no vocabulary entry exists for that field yet),
`cleanEnum` returns the fallback **unconditionally**. Copying the `cleanEnum` calls across
before adding the vocabulary entries would therefore have overwritten seven fields on every
row with their fallbacks — a "fix" that silently destroys correct data. Order matters:
vocabulary entries first, then the calls, and a test asserting each fallback is itself a
member of the validator's vocabulary for that field. An absent allow-list should be a loud
error at the call site, not a degenerate "nothing is allowed" set.

## The containment claim was corrected three times (akira fix plan, 2026-09)

Before the publish-script read, the same containment claim was "verified" twice, and each
version was wrong (see [[Free Text With Deterministic Repair Over SDK-Enforced Schema]]):

1. The bad value was "blocked outright".
2. Then: "written, but kept off the public surface by `needs_review`".
3. Then the fix plan read the publish script in full. Its two gates block on the QC verdict
   and on content-quality checks. Neither one reads `needs_review` or the gate status, and
   the publish write **unconditionally sets `needs_review: false`**, overwriting the
   enrichment gate's flag. The real backstop was the QC verdict. Nothing in the repo wired
   QC to real data, so nobody could say where those verdicts came from.

Each correction came from tracing one hop further toward the final consumer. Stop tracing at
the code that decides what the user sees, not at the code that sets a flag.

## The fix and what it declined

- **Coerce at write time.** The losing option was "document the asymmetry as accepted". It
  was zero lines and zero parity cost, but it would leave an unverified QC gate as the only
  thing between a bad model output and a published corrupt enum. That is a behavioural
  guarantee, not a structural one. The 0/266 measurement argued for doing the fix calmly, not
  for skipping it.
- **Pay the parity cost explicitly.** The original workflow node really did pass bogus enums
  through, so the port now diverges from it. The parity test is split into "clean payloads
  still match" and an explicit `INTENTIONAL DIVERGENCE` case that executes the real original
  node. If the assumption about the original's behaviour is wrong, that test fails instead of
  passing silently.
- **No DB CHECK constraint.** No vertical had ever had one, so it would start a new
  single-issue pattern. It would also be a fourth copy of a vocabulary that already had three,
  and it would be maintained by migration against a taxonomy that changes. A stale constraint
  fails *closed*, rejecting newly valid values. Reconsider it only when a second write path
  that bypasses sanitize actually exists.
- **No backfill.** 0 affected rows means nothing to undo, and revert stays clean.

## Parallel vocabulary tables, kept separate on purpose

Once the fix shipped, three copies of one field's vocabulary existed: the validator's, the
sanitizer's, and the flatten map's keys. The flatten map is **authoritative**, because it
decides what the column can hold, so the sanitizer entry was derived from it. The tables
were deliberately *not* merged into one constant. Each one transcribes a different original
workflow node, and merging them would have silently resolved a real cross-node disagreement
in one direction, with no record of which node was right. Keeping separate tables is a named
exception to "one source of truth": it makes divergence visible. The remaining drift risk is
named, not fixed.

A knock-on finding: the new sanitize fallback (`unclear`) was not in the *validator's*
vocabulary for that field. So every coercion now also triggers a false `needs_review`. The
false-invalidation rate tracks how often sanitize coerces, not how often the model emits one
rare value. This was filed as its own issue, with a before/after probe. A fallback has to be
legal in **every** downstream vocabulary that reads it, validator included, not only the
storage column.

## Keep the Pre-Sanitize Output, or Remediation Means Re-Running the Model (akira, 2026-09)

Sanitize built a `raw_enrichment_before_sanitization` value, but the pipeline passed only
the sanitized payload to the writer. No column held the original. A column named
`raw_enrichment`, commented *"what the model said"*, actually stored the **post-sanitize**
payload. That mislabel plausibly explains why a silent rewrite of middling values to
"unclear" went unnoticed for so long. When 20 rows later sat in the review queue with
stale flags, nothing stored could tell a genuine "unclear" from a coerced one. The only
remedy left was to **re-enrich the rows under the corrected prompt**.

Lessons from the remediation run:

- **Gate on the upstream fix.** The run had a hard gate: the prompt fix must be merged to
  main. Re-running against the broken prompt would reproduce the defect.
- **Re-derive the target set at run time.** The count stayed at 20, but its composition
  had drifted, and no id list had been recorded to diff against. Four rows that a human
  had already reviewed were excluded, even though the lifecycle write was guarded anyway.
  A model call on a row a human has already disposed of fixes nothing.
- **A CLI's narrow return shape can hide what classification needs.** The single-row CLI
  reported only `validation: invalid`, never *which* field failed. "Still the old defect"
  and "a different defect" could not be told apart from its output. The throwaway script
  called the same two exported pipeline functions directly to get the full error array,
  with no change to `src/`.
- **Don't route remediation through an experiment arm.** An environment override pointed
  enrichment at a cheaper-model experiment endpoint. Writing current rows through it would
  have mixed model provenance across the catalogue. The run cleared the override for its
  own process only, and hit [[Empty-String Env Override Defeats Nullish Coalescing]].
- **Close the side effects of writing outside ingest.** Rows written by the CLI had a null
  content hash, which disables the skip gate permanently (see
  [[Cached Derivation Without a Recompute Path]]). A scoped backfill followed the write.
- **Result.** 16/16 re-enriched rows validated clean. The 4 excluded rows were the only
  ones still flagged afterwards.

## The prompt is a fourth vocabulary (akira reviews, 2026-09-06/07)

Reviewing the fit-vocabulary fix found a fourth copy of the vocabulary that nobody had counted:
the **prompt**. Its instructions and its worked example JSON still taught the old set:

    prompt tells model : [strong, standard, weak, not_recommended]
    sanitize accepts   : [strong, medium,   weak, unclear]   fallback: unclear
    validator accepts  : [strong, medium,   weak, unclear]
    storage map keys   : [strong, medium,   weak, unclear]

Sanitize silently rewrote `standard` and `not_recommended` to `unclear` before validate ran, so
only `strong` and `weak` survived. Lessons from this and the sibling reviews:

- **Count the prompt as a vocabulary table.** A schema change in the code has to be matched by a
  change to what the model is taught. Otherwise the sanitizer coerces the gap away, and a
  silent coercion is a defect nothing reports.
- **Fixtures on the shared value prove nothing.** Tests that only fed `strong` or `weak`, the
  values the old and new sets have in common, could not detect the change in either direction.
- **The fallback contaminates a population.** Once coerced values land on `unclear`, a genuine
  "unclear" can no longer be told apart from a coerced one. That is the remediation cost
  described in the next section.
- **A sanitize metric gated at 1.0 that does not exercise coercion** reports PASS while scalar
  coercion breaks. A `cleanEnum` that coerces with no log, flag or audit row makes the
  coercion rate unmeasurable.
- **A material prompt change left the version constant unchanged.** Rows written under the old
  and new prompts carried the same `enrichment_version`, so later remediation could not use it
  to select the affected rows ([[Frozen Version Stamps on Logged Results]]).
- **The acceptance step is a decision, not a fix.** The plan required a before/after live-model
  distribution check, or an explicit decision to accept the risk without one. Neither had
  happened. Review escalated this to the owner rather than dispatching a fixer, because a fixer
  can only fabricate the acceptance or do nothing
  ([[Orchestrator Verifies, Never Relays]]).

## The defect class stays open after the fix (akira enum-escape review, 2026-09-05)

A review of the enum-escape fix confirmed the reported leak was closed, then recorded
what stays open. One vertical's vocabulary was enforced on only 7 of its 9 enum fields.
The per-vertical table shape does nothing to stop a vertical leaving a field out, so the
*class* of defect survives the instance. Finding every stale spec site took three passes
before all five were located. The follow-ups lived only in a gitignored plan, where the
tracker could not see them. **Promote follow-ups to tracked issues before closing the
review.** Better still, add a completeness check (every enum field × every vertical) that
turns an omission into a failure.

## See Also
- [[Empty-String Env Override Defeats Nullish Coalescing]] — related (the defect the remediation run hit)
- [[Evidence-Labelled Generation with Deterministic QC]] — extends (the QC stage this chain feeds)
- [[Every Column Names Its Reader]] — related (the gate flag nothing read is the same trap)
- [[Spend Gate Before the Model Call]] — related (same enrichment chain, the stage before the model)
- [[Silent Fallthrough in String-Keyed Discovery]] — related (a fallback string nobody expected in the column)
- [[Structured Output]] — related
- [[Validator That Proves by Cast]] — instance-of (a validator that passes input through as T)
- [[Input Guardrails Pipeline]] — extends
- [[Comparable Tables, Not One Source]] — extends (the sanitize fallback must also be a validator-legal storage key)
- [[Guard at the Funnel, Fix at the Cause]] — related (the bound returns null and the importer decides)
- [[Free Text With Deterministic Repair Over SDK-Enforced Schema]] — related (the spec-wording decision whose trust claim this chain had to back)
- [[Single-Call LLM Gate Weakness Audit]] — prerequisite-for (silent repairs surfaced as a non-blocking gate reason)
