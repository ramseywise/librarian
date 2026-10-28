---
title: Quality-Gate Dashboard in Pipeline Order
tags: [eval, pattern]
summary: "Lay out an admin quality dashboard as the pipeline's stages in order (sources, content checks, candidates, enrichment and QC, serving), with a product strip over a technical strip on every stage, every flag or score shown under the component that emits it from the code's own closed vocabularies, labels collected in the work surface and computed offline, and an eval-gate panel saying why each number cannot be trusted yet — a panel that is neither product nor technical is a queue and belongs elsewhere."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-28-admin-dashboard-quality-gate.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-28-admin-dashboard-quality-gate.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-28-admin-dashboard-quality-gate.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-28-admin-dashboard-quality-gate.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-28-admin-dashboard-quality-gate.md
---

# Quality-Gate Dashboard in Pipeline Order

An event and venue catalogue (repo akira, 2026-09-28) had an admin dashboard that had grown
into seven tabs: monitoring panels, labelling sub-pages and work queues, in no particular
order. The rebuild turned it into one page that answers one question per stage: is this stage
producing correct, complete content, and is it running? The design rules below are the
reusable part.

## Stages in pipeline order

The tabs follow the data's path: **Sources → Content checks → Venue candidates → Enrichment
& QC → Serving**, with a header strip on every tab. Old tab ids map to their new home, so
bookmarks still work. Existing panels moved into their stage unchanged before anything new
was added, which kept each slice reviewable.

The **header strip** shows an end-to-end funnel across the item-lifecycle ledger stages for
a chosen item kind and window. Stages that have no writer yet render as "no writer", not as
zero.

## Product strip over technical strip

Every panel declares itself **product** (is the content right, complete, covering the
moments: rates, coverage, precision) or **technical** (did the stage run: runs, latency
p50/p95, failure count, last-run age). Each tab shows both strips. **A panel that is neither
is a queue, and queues belong in the work surface**, not the monitor. Following that rule
removed four labelling sub-pages from the admin nav. The one write the dashboard kept is an
image takedown on the compliance panel, because that panel is where the takedown is acted
on.

## Failure attribution: show every number under the component that emits it

The rule: **every flag, reason or score is displayed under the stage that emits it, and the
funnel's drop count at each stage links to that stage's reason breakdown.** A number shown
without its emitting component is not a diagnosis. The plan built an attribution table, one
row per component with its module, the closed vocabulary it emits, the eval metric grading
it and that metric's gate state, and the panel that shows it. Some of the components:

- source health classifier → health statuses and error types (Sources)
- candidate outcome reasons (`unresolved`, `hash_match`, `fetch_failed`, `not_berlin`, …) →
  dropped-by-reason per source per run (Sources)
- QC pre-check reasons (`missing_start_at`, `start_at_past`, …) → the share of rows that
  never reached a model call (Content checks)
- probe flag rules (27) and facet values with their `source` (model / rule / osm) →
  precision per facet × source (Enrichment)
- human defect chips mapped by a `DEFECT_STAGE` table to extraction / enrichment /
  description / image → **defects attributed per pipeline stage**, the one panel that
  closes the loop from a human verdict back to the component that caused it

**Vocabularies are the closed lists the code already exports.** The dashboard never
re-derives them, because a hand-kept second list is the drift a schema probe exists to
prevent. Building the table exposed two gaps, both recorded as follow-ups. One flag set
lived under a dev folder and had only ever been read by a notebook. The image stage had a
human verdict but no machine flag to compare it with.

## Collect in the work surface, compute offline, display read-only

Acceptance numbers (facet precision, judge-vs-human agreement) follow one route:

- **Collection** happens on the operator feed card: the verdict, defect chips, and a
  per-facet chip.
- **Computation** happens in offline report modules and eval graders, never on a request
  path.
- **Display** is a set of read-only panels under the stage that owns the number.

The tracing tool is not the number of record for any acceptance metric (see [[A Trace Is
Not a Number of Record]]). Deleting a labelling page orphaned one corpus's only writer, a
ranker relevance-judgment table. The plan named the replacement (the feed's slate verdicts,
recorded with slate position) instead of letting the writer disappear silently.

## Tell the reader why a number can't be trusted yet

- **n on every number.** A panel with n < 20 greys out its number and says "not enough
  labels".
- **An eval-gate status panel** in the header, with one row per metric: gated or UNGATED,
  and a *reason class* for UNGATED. The classes are own-oracle (the fixture uses the
  function as its oracle), no-baseline, co-fitted (weights tuned on the same data), and
  judge-ceiling (bounded by human agreement). It lists *why* each number can't yet be
  trusted, not only whether it passed.
- **Disclosed gaps, not silent ones.** Six panels the build could not compute shipped
  labelled NOT AVAILABLE, and a follow-up decided per signal whether to compute it live,
  persist it, or record "stays unmeasured" (see [[Every Column Names Its Reader]]).

## Build notes from the same plan

- **Additive optional terms prove themselves byte-identical when absent.** New priority
  terms (coverage gap, evidence rank, out-of-scope demotion) are optional inputs. A test
  asserts that a candidate without them scores exactly as before. The fixtures were written
  from the rule text first and confirmed red before the build.
- **Reuse the real module's constant over the plan's prose.** The plan said near-duplicates
  were "<50 m". The existing duplicate detector used 150 m, so the build used the detector
  rather than adding a second radius.
- **A guardrail grep runs before and after.** The reviewer-priority module must never be
  imported by the user-facing scoring code. A grep showing no import ran before and after
  each priority change.
- **Out-of-plan work gets recorded.** A commit that widened a shelf city-wide (about 5,300
  rows per render) landed with no step covering it. It was written into the plan's log as
  an unrecorded decision needing a decision row, not left implicit.

## See Also
- [[Monitor the Gate, Not the Stage]] — extends (per-gate fire rate, precision with n, recall proxy and drift for unattended operation)
- [[Single-Subject End-to-End Trace]] — related (the per-subject view of the same stage-by-stage attribution)
- [[A Trace Is Not a Number of Record]] — related (why the tracing tool doesn't hold acceptance numbers)
- [[One-Sided Label Control]] — related (the facet chip that feeds the precision panel)
- [[One Facet Per Fact]] — related (precision per facet × source)
- [[Every Column Names Its Reader]] — extends (compute, persist or "stays unmeasured" for NOT AVAILABLE panels)
- [[Q0–Q5 Quality Ladder]] — related (the own-oracle trap the gate panel names)
- [[Kiez Project]] — instance-of
