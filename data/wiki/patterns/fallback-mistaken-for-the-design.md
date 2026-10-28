---
title: Fallback Mistaken for the Design
tags: [patterns, pattern]
summary: When the degraded path is the only one that has ever rendered, reviewers critique the fallback as if it were the design — check what branch produced the surface under review before redesigning it, and look one directory deeper before concluding a feature is unbuilt.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/diskoe/docs/research/2026-09-10-results-surface-design.md
  - data/raw/claude-docs/playground/docs/research/2026-09-10-results-surface-design.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-03-dis141-five-plus-three.md
  - data/raw/claude-docs/playground/docs/research/2026-09-03-dis141-five-plus-three.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-26-b16-venue-coordinates.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-26-b16-venue-coordinates.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-26-b16-venue-coordinates.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-26-b16-venue-coordinates.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-26-b16-venue-coordinates.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-26-b16-venue-coordinates.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-26-b16-venue-coordinates.md
---

# Fallback Mistaken for the Design

The owner of a recommendation product (repo diskoe/akira) reviewed the live results
surface on a phone and proposed a redesign: "right now we return just 5 demo cards, but the
reality should be 3 best matches with 5 similar below". The research doc's first section
was two corrections, before any design.

## The mechanism

The five cards were `DEMO_ITEMS`, rendered only when the ranker returned zero items
(`useDemo = result.items.length === 0`, response flagged `demo: true`). Nine of 451 events
were published; all 18 production result sets had returned zero items against an empty
candidate pool. **The surface under review had never rendered a real ranked set.** Every
design judgment made from it was a judgment about the empty-pool fallback. The
prerequisite for evaluating any shape — 5 primaries, 5+3, 3+5 — was re-measuring the
published/enriched counts, not a UI change.

The second correction: the shape was already decided (5 primaries, 0–3 alternatives each,
never a feed), and the owner chose to keep it once reminded. The rejected alternative was
recorded with its arithmetic (8 cards vs a ceiling of 20) so the choice is legible later.

## The grep that lies

`grep alternatives src/products/feed src/agents/scoring` returned nothing, suggesting
alternatives were unbuilt. They lived one directory deeper: similarity function, selection
of 0–3 per primary, thresholds, attachment to each composed item, and an eval metric were
all BUILT. What was missing was carrying an existing value through three layers (feed →
API response → card) and the serving log. "Not yet built" was true of the surface and
misleading about the work — see [[Write-Only Fields and the Reader Map]] for the general
audit.

## Rules carried out of the review

- **Check which branch produced the thing under review** before redesigning it; a `demo`
  flag in the response is cheap and decisive.
- **Expand in place, per primary.** An alternative is `similarity(primary, candidate)`,
  not a global runner-up; a shared row of alternatives with no visible parent makes the
  "chose the alternative over its primary" signal uninterpretable, and 5×3 always-expanded
  is the feed the requirements forbid.
- **The label states the real count** ("2 similar", not "similar"): zero is a designed
  outcome, and a label promising more than exists is the same defect as a chip offering a
  date it cannot accept.
- **Selection is not saving.** Reusing the save control to build a poll leaves surprise
  rows in the saved list when the poll flow is abandoned.
- **A poll of one is not a poll** — enable the action at two selections.
- **Log the anchor as `anchor_venue_id`, not coordinates.** A "near this venue" query is
  the existing pipeline re-run with one field swapped; recording the venue's coordinates as
  if the user stood there quietly undoes the location-redaction work.
- **Serving is what creates the gating signal.** The alternatives metric was UNGATED
  because its weights were tuned on the fixtures that grade it; which alternative users
  choose over its primary is the independent signal — so the log migration ships with the
  serving change ([[Ship Logging Before Features]]).

## A Built Dimension Starved by a Hardcoded Null (akira, 2026-08)

akira's `locationFit` scoring had full distance math, with tests. In production it was dead:
lat/lon were hardcoded to `null` upstream, so every candidate got the constant fallback of
0.4. The dimension looked implemented and its tests passed, yet it ranked nothing. This was a
gap in data and wiring, not in scoring. The fix geocoded at venue level. Venue coordinates are
off by tens of metres, far below the 1.5 km decision anchor, so finer precision would have
changed no ranking. Name-based geocoding also filled in the address as a byproduct, and
attempt-state columns (`geocode_status`, `geocoded_at`) make reruns incremental.

## See Also
- [[Artifact Is Not Evidence: Push and Probe]] — related (a rendered surface is not evidence of the ranked path having run)
- [[Write-Only Fields and the Reader Map]] — related (built value dropped at the serving seam)
- [[Ship Logging Before Features]] — extends (the log shape for a new slot type lands before the first serve)
- [[UNGATED Metric Convention]] — related (why the similarity metric had no threshold)
- [[Silence Reads as Clean]] — related (zero results rendering as a plausible page)
- [[Mislabelled Column Is Worse Than Missing]] — related (another plausible value that hides a gap)
