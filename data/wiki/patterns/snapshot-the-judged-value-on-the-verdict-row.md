---
title: Snapshot the Judged Value on the Verdict Row
tags: [eval, pattern]
summary: "A human review queue whose subjects are pre-canonical or mutable stores an immutable snapshot of exactly what was judged on the verdict row itself, so a later re-extraction or enrichment rerun cannot silently re-point an old verdict at new content. Pair it with an insert-only seeding CLI (`on conflict do nothing`), a clear-not-delete reset, and one table for queues that differ only in payload."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-20-dis352-extraction-handcheck-feed.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-20-dis352-extraction-handcheck-feed.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-20-dis352-extraction-handcheck-feed.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-20-dis352-extraction-handcheck-feed.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-20-dis352-extraction-handcheck-feed.md
---

# Snapshot the Judged Value on the Verdict Row

From an admin review feed in akira (2026-09-20). Two small human queues were added to an
existing review surface. One hand-checked 60 structural-listing extraction candidates to get
a precision number. The other recorded right/wrong verdicts on enrichment labels (vibe tags,
energy level). The label queue was a single-rater human reference for the label judges,
replacing a planned two-rater agreement study.

## Why the existing review table did not fit

The feed already had a verdict table keyed to real content rows, guarded by a trigger that
rejected any verdict whose row was missing. The extraction candidates had **no row
anywhere**. They were computed in memory over an offline HTML cache and never written. Its
`approve`/`reject` vocabulary also did not fit "was this extraction correct". Reusing it
would have meant inventing fake content rows.

## The mechanism

- **The verdict row carries a `payload jsonb not null` snapshot taken at seed time.** For a
  candidate it holds title, start time, source and page URL, snippet and the grouping
  strategy that produced it. For a label it holds content kind, content id, field and the
  label value.
- **The judged value is copied, not re-read live.** If enrichment reruns and changes the
  vibe tags after a verdict, the verdict must stay attached to what the human actually saw.
  This is the same reasoning as recording which UI mode was on screen when a verdict
  button was pressed.
- **A stable `subject_key`.** Candidates use a hash of `page_url|title|start_at`, labels use
  `kind:id:field`. A uniqueness constraint covers `(user, subject_type, subject_key)`.
- **One table, a `subject_type` discriminator.** The two queues were structurally identical
  (snapshot + right/wrong + note) and differed only inside `payload`, which a `jsonb` column
  already isolates. That meant one migration, one store, one route. Two tables were rejected.
- **Seeding is a one-time CLI, not a page-time computation.** The CLI uses a seeded PRNG
  (the tree's existing one, reused) and inserts rows with `decision: null` using
  `on conflict do nothing`, so a re-run can never overwrite a verdict already pressed. The
  page only reads pre-computed rows. It never calls the extractor, which keeps the app layer
  from importing pipeline code.
- **DELETE clears, it does not delete.** Resetting a verdict nulls `decision`/`note` and
  keeps the seeded row, because the row *is* the sample. This deliberately diverges from the
  sibling table's delete-the-row semantics, and the route's module doc says so.

To make the per-strategy precision breakdown possible, the extractor had to start reporting
which grouping strategy produced each result. A tagged variant was added and the old export
became a thin `.map(({ result }) => result)` wrapper, so existing callers and tests were
untouched.

## What it leaves open

The snapshot holds the judged value but not the evidence the human looked at. A later eval
loop exported these verdicts as judge fixtures and had to join live content for evidence,
which can drift from what was on screen ([[Human Verdicts as Judge Fixtures]]).

## See Also
- [[Human Verdicts as Judge Fixtures]] — prerequisite-for (the export that consumes these rows)
- [[HITL Annotation Pipeline]] — instance-of
- [[Publish Automatically, Sample for Review]] — related (sampled human grading without blocking)
- [[Re-Crawl Adds, Never Overwrites]] — related (the same insert-only rule protecting human work)
- [[Taste vs Defect Verdict Split]] — related (verdict vocabulary design on the same review surface)
