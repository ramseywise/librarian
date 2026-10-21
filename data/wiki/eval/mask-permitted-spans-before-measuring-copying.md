---
title: Mask Permitted Spans Before Measuring Copying
tags: [eval, pattern]
summary: "A verbatim-overlap grader (\"no run of more than N words shared with the source\") cannot be tuned to tolerate legitimately kept names, because permitted names — work titles especially — run longer than any candidate threshold; raising N buys silence, not headroom. Mask the spans the prompt allows the model to keep, in both texts, then set N to the prompt's actual contract — and decide the threshold debate from a corpus measurement that needs no model output."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis277-generated-description-verbatim-threshold.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis277-generated-description-verbatim-threshold.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis277-generated-description-verbatim-threshold.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis277-generated-description-verbatim-threshold.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis277-generated-description-verbatim-threshold.md
---

# Mask Permitted Spans Before Measuring Copying

An enrichment prompt (repo akira, 2026-09) asked the model to write a fresh event description
and forbade copying "more than four consecutive words" from the source, except "names of people,
groups, works, venues and organizers". The deterministic grader flagged a description when its
longest shared word run with the source reached a constant, `VERBATIM_RUN_FLAG = 8`. The issue
framed the choice as 5 versus 8: align the constant with the prompt's four-word rule, or keep 8 as
headroom for legitimate proper names.

## The headroom argument is testable without model output

The headroom claim is a statement about *names in sources*, not about model behaviour. It can be
measured today with the grader's own `longestSharedWordRun` over the 391 events that have a
source description:

- **Venue name vs. its event's source description:** runs of 0–3 words only. **Zero** reach 4.
  The largest category of permitted name puts no pressure on either threshold.
- **Event title vs. its own source description:** ≥5 in 21 rows (5.4%), ≥8 in 14 (3.6%), ≥10 in
  7 (1.8%). Moving 8 → 5 newly flags 7 rows in the whole corpus. The long runs were titles that
  are themselves prose: "Two-part sonnet workshop with …" (11), a work title
  *Pentecost. Memories of the end of the world* (10), and one title containing a whole
  paragraph (22, an extraction defect, not a naming question).

## What it settles

**5-versus-8 is a false dichotomy.** A legitimately kept 10-word work title trips 8 exactly as it
trips 5. No threshold can protect permitted names, because the longest permitted names exceed
every candidate value. Raising the constant only makes the grader silent across the board,
including on real copying.

The defect was the instrument, not the number: the grader compared raw text without first
removing what the prompt explicitly allowed. The fix:

1. An optional `permittedNames` input. Before computing the run, replace each name's word span in
   **both** texts with a non-matching sentinel, so a kept name cannot contribute to a shared run.
   The measurement primitive stays exported and unchanged.
2. Populate names from the row's title, venue and organizer. If the field is absent, the array is
   empty and behaviour is unchanged, so the existing 14 fixtures pass as before.
3. A report-only sweep at thresholds 5–8, **with and without masking**, so the masking's effect
   is shown rather than assumed.

**Known blind spot, written in the grader header:** masking can over-forgive. A copied sentence
that contains a name gets that span excused. Venue names never reach 4 words, so they excuse at
most 3. Long work titles are the real exposure, and they are rare (7 of 391 at ≥10).

## Split the plan at the evidence boundary

The first version of the plan was **circular**. Step 1 exported "the first real output sample",
every later step depended on it, and the plan's own Out of Scope forbade the production backfill
that would create one. A probe of all three enrichment tables found **zero** stored generated
descriptions anywhere, including inside the raw model JSON. All 322 rows predated the field. The
field was never lost in flattening; it had never been generated.

The re-plan separated what data on hand can decide from what it cannot:

- **Decidable now:** the masking grader and the threshold sweep, against the existing corpus.
  Both are prerequisites for reading a sample when one arrives.
- **Genuinely blocked:** the model's compliance rate, which is a fact about model output. It was
  isolated into **one** operator-gated step: a bounded real run (~30 events, German and English,
  long and short titles). The threshold becomes the lowest value with zero false positives
  after every boundary hit is labelled by hand. The gate is set at the observed rate, never an
  assumed 1.0.

Meanwhile the constant stays at 8 and the metric stays UNGATED, because lowering it without a
measured compliance rate trades one unevidenced number for another. The targets file states the
exact unblocking condition (N graded real outputs and an observed pass rate) instead of "waiting
for real output" ([[UNGATED Metric Convention]]).

## See Also
- [[UNGATED Metric Convention]] — extends (what the metric reports until the bounded run lands)
- [[Grounding Claim Methodology]] — related (verbatim quotes as evidence; here verbatim runs are the defect)
- [[Write-Only Fields and the Reader Map]] — related (the generated-description field that had no column)
- [[Synthesize the Cheap Half]] — related (measure the side you can verify against reality first)
