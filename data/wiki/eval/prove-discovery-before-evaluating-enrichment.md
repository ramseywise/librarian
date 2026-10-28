---
title: Prove Discovery Before Evaluating Enrichment
tags: [eval, decision]
summary: "Before any enrichment-quality evaluation, prove that the pipeline found the right things and represents them faithfully: discovery precision, negative controls, entity boundaries, cross-source identity, recurrence, venue identity, field provenance and minimum evidence. One labelled sample per discovery route, reported with a Wilson CI, covers three of those proofs. Notebooks call pipeline rules and never re-derive them."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-15-pre-enrichment-proof.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-15-pre-enrichment-proof.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-15-pre-enrichment-proof.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-15-pre-enrichment-proof.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-15-pre-enrichment-proof.md
---

# Prove Discovery Before Evaluating Enrichment

From an akira planning note written after its analysis notebooks were consolidated. One
notebook covered the production view, one folder covered what was found *before*
enrichment, and one notebook covered each pipeline stage. The claim to establish before
any enrichment evaluation is:

> **We have discovered the right things and can represent them faithfully.**

Grading enrichment output on top of a corpus that double-counts events, admits listing
pages as records, or lacks the evidence to enrich measures the wrong layer (see
[[Input-Starved Enrichment]], [[Listing Pages Masquerading as Records]]). The note was
also explicit that the notebooks would *not* become an enrichment evaluation suite.

## The proof ladder

| Proof | Blocked on |
|---|---|
| We discover real things (precision) | a labelled sample |
| We reject non-objects (negative controls) | a labelled sample |
| The event vs activity boundary holds | the labelled sample, plus a minimum-evidence decision |
| One real thing is one row across sources | cross-route identity |
| Recurrence and occurrences are faithful | a series report |
| Venue identity and district are right | matching for multi-venue sources |
| Every shown field has a known origin | per-field provenance |
| There is enough evidence to enrich | a minimum-evidence decision |

## The design choices worth reusing

- **One labelled sample covers three proofs.** It uses six classes: real event · real
  activity · real venue · not an object (listing page, nav, ad) · duplicate · out of scope.
  About 50 items per discovery route are enough to report precision **with a Wilson 95% CI,
  never a bare percentage**. Two additions sit on top. **Seeded negative controls** are
  pages that must yield nothing: a venue's about page, a past-events archive, a newsletter.
  A **boundary set** of 10–20 borderline rows covers exhibitions, courses, residencies and
  weekly markets.
- **Labels live outside the notebooks.** The notebooks were gitignored and had no history,
  so labels go to eval fixtures or a labels table, which shares its shape with
  [[Append-Only Human Labels]].
- **Identity is checked across routes.** Catalogue rows were keyed by a natural key, while
  crawled rows were keyed by source URL. The same concert found by two routes counted twice.
  The report is the number of distinct real-world events per route, plus the near-duplicate
  pairs the natural key missed.
- **The recurrence report counts and does not fix.** Only iCal kept a recurring event as one
  row with occurrences. Every other route turned a weekly night into N events. The report
  groups rows by (venue, normalized title) with three or more starts at a regular interval
  and counts the likely series. It changes no data.
- **Provenance is per field, not per row.** The extractor should record which tier filled
  each field (JSON-LD, OpenGraph, HTML, iCal, imputed). A row-level `extraction_method`
  forced the notebook to reconstruct provenance by re-running every tier. Ten golden pages
  with the expected value and tier per field become a heuristic metric, UNGATED until
  measured (see [[UNGATED Metric Convention]]).
- **Minimum viable evidence is a decision plus a pure validator.** For an activity that
  means name, place, what you do there, and how to go (hours or a booking link). It
  explicitly does not require a start time.

## Notebooks call pipeline rules, they never re-derive them

The house rule is that no pipeline rule is re-implemented in pandas. The note listed the
remaining violations: imputation rules, completeness scoring, bucket functions, the set of
fields a card shows (which should come from the read path's own column constants, not a
hand-kept dict), and the "servable" filter that mirrored the app's visibility predicate.
The fix for each is an exported, tested function that the notebook calls through a
TypeScript bridge. A notebook re-derivation is a second definition that drifts silently
from the one production uses. Findings should also come from pipeline run records, not
from notebook computation. That needs run records the pipeline did not yet write: QC runs,
enrichment cost per run, probe and corpus runs.

## See Also
- [[Input-Starved Enrichment]] — prerequisite-for (the evidence floor this ladder checks)
- [[Listing Pages Masquerading as Records]] — related (the not-an-object class)
- [[Append-Only Human Labels]] — related (where the labelled sample should live)
- [[Eval Falsifiability]] — extends (negative controls make discovery precision falsifiable)
- [[Golden Set Mechanics]] — related (the per-field golden pages)
