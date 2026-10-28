---
title: Single-Subject End-to-End Trace
tags: [patterns, eval, pattern]
summary: Walk one real subject (one venue) through every pipeline stage with a PASS/FAIL row per stage, running the real stage functions — it surfaces gates nobody can pass, rows that sit in no queue, and instruments that shipped green but were never armed, which per-stage tests and aggregate dashboards both miss.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/research/2026-09-22-venue-trace-path-metrics.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-22-venue-trace-path-metrics.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-22-venue-trace-path-metrics.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-22-validation-path-metrics-loose-ends.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-22-validation-path-metrics-loose-ends.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-22-validation-path-metrics-loose-ends.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-22-validation-path-metrics-loose-ends.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-22-validation-path-metrics-loose-ends.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-22-dis366-label-queue-real-card.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-22-dis366-label-queue-real-card.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-22-dis366-label-queue-real-card.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-22-dis366-label-queue-real-card.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-22-dis366-label-queue-real-card.md
---

# Single-Subject End-to-End Trace

From an akira trace that took one venue from discovery to the visitor surface. Each stage
function ran for real. The output was a matrix: stage × subject → PASS/FAIL plus the
evidence row, with a funnel at the end.

## What one subject found that the test suite didn't

- **A gate nobody can pass.** Enrichment and QC both passed, then the publish gate failed
  on all five events with `missing_vertical_details`. The gate requires fields (category,
  a decision snippet) that no stage writes. Validation reasons block unconditionally, so a
  freshly ingested event could never be published.
- **Rows in no queue.** Two rows were `draft` with `needs_review=false`: not in the review
  queue (which filters on `needs_review=true`), not on the QC tab, not visible to visitors.
  The preview pages were admin surfaces, not queues. Those rows would never move.
- **Trace evidence never flushed.** The seed harness called the per-source processor
  directly, while only the importer flushes run and outcome rows, so the crawl trace was
  0 rows. A raw-page "store" turned out to be a dev cache, not a snapshot store.
- **Path metrics in three disconnected pieces** with no join from crawl to publish.

## Instruments shipped but never armed

Ten instruments had shipped in the prior week (a grading UI, a label queue, a hand-check,
a hold-out, a QC runner, a sweep...). All were green in CI. On production, 84 seeded label
rows had `decision = null`, there were zero retest pairs and zero judgment rows. **The
gate checks that an instrument works, not that anyone read it.** The fix was to add the
human-rating instruments as rows in the same matrix (`labels`, `judgments`), so they read
FAIL until someone actually uses them.

## The trace as a closing test

The matrix doubles as an acceptance test for operator work. Re-run it after each operator
step and watch specific rows flip (crawl FAIL → PASS once the importer path is used;
"rows on no surface" 3 → 0). An issue is closed when its row flips on a production re-run,
not when the code merges.

## Acting on the Trace: Arm and Read First, Build Second (akira follow-up plan, 2026-09)

The follow-up plan began with the operator's own count: ten validation instruments built
in a week, one measurement taken. So it was ordered **arm and read first, build second**.
Every build step ends with a step that reads its output on the same venue trace, and no
step adds an instrument that is not run in the same phase.

- **Fix the hard blocker first.** Until the impossible publish gate was fixed, the
  funnel's last two rows were zero by construction, and nothing measured downstream meant
  anything.
- **The gate reads enrichment; the model does not write canonical columns.** The
  recommended decision had validation read the enrichment row's `primary_category` in
  place of the empty canonical `events.category`. The rejected alternative had the
  enrichment flatten step write the canonical column, which would make the model a writer
  of canonical data, and its snippet output had never been graded. **A publish rule cannot
  depend on an unbuilt feature**, so the decision-snippet requirement left the rule until
  that feature exists.
- **The arming step is a plan step, not an operator follow-up.** A bounded production QC
  run (`--max-rows 20`) and 20 rated label cards were written into the plan as a step so
  they "cannot be skipped as operator follow-up". The resulting numbers go into the
  targets file even before they are pass rates.
- **Port the notebook's pivot into gated code.** The trace notebook's stage-matrix pivot
  became the spec for a typed stage-matrix reader and CLI. The Python copy of the selection
  blockers was retired in favour of the real function with `now` injected.
- **Every row is on some surface.** A "blocked" review filter shows draft rows with their
  computed blocker reasons, so no traced row sits in no queue.

The label queue's own sampling problem is on
[[Recency-Seeded Label Queue Samples the Thin End]].

## See Also
- [[Parsed Then Dropped at the Insert Mapper]] — related (a per-field trace finds the same class of seam loss)
- [[Silence Reads as Clean]] — related (empty trace tables read as "nothing happened" rather than "nothing recorded")
- [[Migration Done Means Pushed and Probed]] — extends (done means observed in production, applied to a whole pipeline)
- [[Recency-Seeded Label Queue Samples the Thin End]] — related (the label instrument's sampling fix)
- [[Offline Pipeline Seed Harness]] — prerequisite-for (the trace's real-stage walk made repeatable over fixtures)
- [[Quality-Gate Dashboard in Pipeline Order]] — related (the aggregate, stage-by-stage view of the same attribution)
