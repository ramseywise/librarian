---
title: Recency-Seeded Label Queue Samples the Thin End
tags: [eval, pattern]
summary: A human label queue seeded from the most recently processed rows lands on exactly the rows with the least to judge, and an unguarded seeder asks raters to mark right/wrong on an empty value — seed only rows that carry a subject for the field, stratify over the kind × field matrix with a per-cell cap, and rank by the rater's basis to judge.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-22-dis366-label-queue-real-card.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-22-dis366-label-queue-real-card.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-22-dis366-label-queue-real-card.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-22-dis366-label-queue-real-card.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-22-dis366-label-queue-real-card.md
---

# Recency-Seeded Label Queue Samples the Thin End

## Finding

akira's enrichment label queue (operators mark each model-assigned label right or wrong)
was seeded with the 20 most recently enriched rows per content kind. Measured on
production, 17 of the 20 most recent events had no vibe tags and 16 of 20 had energy
`unknown`. All 20 of the most recent bar/restaurant rows had neither. "Most recent" was
the thin end of the corpus, because enrichment quality had drifted down recently. So the
queue mostly sampled rows with nothing to judge.

The seeder made it worse. It pushed a vibe row and an energy row for every content row
**unconditionally**, while the two newer fields (language, resident audience) already had
`has*Subject` guards. Because of that asymmetry, raters were asked to mark right/wrong on an
empty list. A verdict on an empty value tells you nothing about the label, and it still
counts toward agreement statistics.

## Rule

1. **Seed only judgeable rows.** Every judged field gets a subject guard: a non-empty
   tag list, an energy level other than `null`/`unknown`. Write the guards together so no
   field can be the odd one out.
2. **Stratify over the matrix the metric is reported on.** Enumerate the cells
   (content kind × field: 12 here, because bars and restaurants are only judged on vibe
   and energy). Fill each cell up to a cap (default 20). A row selected for one cell still
   carries all its other applicable fields, so selection is per content row, not per
   field, and a row that fills two cells is not counted twice.
3. **Rank by the rater's basis to judge**: rows the operator saved first, then rows the
   operator already reviewed on another surface, then the rest. Use a stable sort and break
   ties by original order, with no clock or randomness in the sampler, so it can be
   tested as a pure function.
4. **Show coverage on the page.** A decided/total table per cell shows which cells are
   short of rows. The cap is a starting default to raise once that table shows where
   coverage is thin.

## Related decisions from the same change

- **Judge on the real card.** The queue rendered a plain text list. Raters judging a
  label need to see what the model saw, so the queue now reuses the production card,
  including the admin enrichment-input panel. The card's display fields came from a
  helper extracted from the feed's own resolver calls, not from a hand-written fourth
  loader.
- **The label-seeding mechanism stays fixed.** Subject-key format, retest suffix and
  verdict table are unchanged. Only *which* rows get seeded changes, so the downstream
  stage-matrix reader that counts labels did not need a code change, only a regression
  check.
- **Re-enriching the thin rows is a separate problem.** It belongs to enrichment, not to
  the label queue ([[Starved Tag Triage: Edge, Prompt, or Supply]]).

## See Also
- [[HITL Annotation Pipeline]] — instance-of (queue sampling design for a rater workflow)
- [[Starved Tag Triage: Edge, Prompt, or Supply]] — related (why the recent rows were thin in the first place)
- [[Single-Subject End-to-End Trace]] — related (the trace that found the label queue shipped but unused)
- [[Append-Only Human Labels]] — related (where the verdicts land)
- [[Explore Slice for Position Bias]] — alternative-to (a different correction for a biased sampling order)
- [[Snapshot the Judged Value on the Verdict Row]] — extends
