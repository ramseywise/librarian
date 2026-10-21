---
title: Three-Level Duplicate Classification
tags: [foundations, pattern]
summary: A first-pass entity-resolution layer for multi-source ingestion that sorts candidate pairs into not_duplicate / possible_duplicate / confirmed_duplicate from deterministic signals that differ for time-bound and place-like entities, routes the uncertain middle to human review, hides confirmed duplicates through the existing visibility gate, and never deletes or merges automatically.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/diskoe/docs/research/2026-10-09-notion-content-data-contract-pages.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-10-09-notion-content-data-contract-pages.md
---

# Three-Level Duplicate Classification

From the content data contract of an events-and-places discovery product (repo diskoe,
mirrored 2026-10-09 from a June 2026 product spec). Several sources describe the same
real-world event, venue or restaurant. The v0 answer was a **deterministic, explainable
classifier**, not a merge system or an ML matcher.

## Three levels, three routes

| Level | Meaning | Route |
|---|---|---|
| `not_duplicate` | distinct enough to keep | nothing |
| `possible_duplicate` | may be the same item, not certain | human review queue, reason tagged |
| `confirmed_duplicate` | same item with high confidence | marked duplicate, a canonical item kept |

The uncertain middle is the point of the design. A binary classifier forces every
borderline pair to be either merged wrongly or shown twice. A third level makes the
cost of uncertainty a review task instead.

## Signals depend on the entity's identity axis

Time-bound entities (events) and stable entities (places) are identified differently,
so they get separate rule tables.

- **Events: strong** = same normalized source URL, same source/external id, same
  normalized title + venue + exact start, or same organizer + title + exact start.
  **Possible** = similar title + same venue + same date, same title + nearby coordinates
  + overlapping time, similar title + same date + different source. **Weak** (never enough
  alone) = same venue on a different date, same series name on another date, recurring
  occurrences, shared category or vibe.
- **Places: strong** = same source URL or place id, same normalized name + address, same
  website, same name + nearby coordinates. **Possible** = similar name nearby, same name +
  district when the address is missing. **Weak** = same brand at another location.

The weak list matters as much as the strong one. "Same title" is not identity for a
recurring event or a chain.

## Reuse the existing gate, defer the schema

- Duplicates are expressed through the existing review fields (`review_status`,
  `review_reason`). Confirmed duplicates disappear from the app because visibility already
  requires `review_status = published`. No new visibility path.
- **Nothing is deleted or merged automatically.** Canonical preference is ordered: official
  source over secondary, then the most complete required fields, then higher source trust,
  then better display data, keeping useful source references.
- Durable link columns (`duplicate_of`, `canonical_id`, a duplicate group id) were
  **deliberately deferred** until a review workflow needed them.
- Out of scope for v0: fuzzy/embedding matching, merge UI, auto-delete.

## What happened next

The helper library was written and tested but never wired into ingestion. The dedupe that
actually ran was a short group-by in an ops script, and the `duplicate` enum value carried
zero rows (see [[The Untested Copy Wins]]). A later clean-room rebuild planned the
replacement in the same tiered spirit: source id first, then name plus geodistance, then
embeddings.

## See Also
- [[The Untested Copy Wins]] — related (the spec'd resolver that had no callers)
- [[Layered Ingestion Failure Posture]] — related (where a dedupe step sits in an ingestion pipeline)
- [[Hide-Unknown Display Contract]] — extends (the same contract's visibility gate)
- [[Graded-Uncertainty Enrichment Contract]] — related (the same "uncertain middle routes to review" idea, applied to enrichment)
