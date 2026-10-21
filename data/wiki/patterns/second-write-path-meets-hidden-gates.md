---
title: A Second Write Path Meets the First Path's Hidden Gates
tags: [infra, pattern]
summary: "A new ingestion path that skips the established dispatcher and calls the write primitive directly runs into constraints the old path met by construction: CHECK values that assume the old transport, NOT NULL columns the new source cannot fill, and a downstream allowlist where any other legal enum value silently drops every write. Re-derive each constraint from the schema, not from module comments, and turn silent drops into a hard validation before the first write."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-22-dis250-kulturdaten-pilot-write-path.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-22-dis250-kulturdaten-pilot-write-path.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-22-dis250-kulturdaten-pilot-write-path.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-22-dis250-kulturdaten-pilot-write-path.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-22-dis250-kulturdaten-pilot-write-path.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-30-slice-g-venueless-event-sources.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-30-slice-g-venueless-event-sources.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-30-slice-g-venueless-event-sources.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-30-slice-g-venueless-event-sources.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-30-slice-g-venueless-event-sources.md
---

# A Second Write Path Meets the First Path's Hidden Gates

An event catalogue had one ingestion shape: crawl an HTML index, optionally follow
detail pages, then call a shared `writeEvent` primitive. The akira plan (#250) added a
second shape: a public open-data JSON API for a district's cultural events, written
directly through the same primitive and bypassing the crawl dispatcher. The module's
header gave three reasons it had been left read-only. A schema read found three more
constraints the header did not list, or listed wrongly.

## What surfaced

| Constraint | Why the old path never hit it | Resolution |
|---|---|---|
| `sources.mode` is CHECK-constrained to `INDEX_ONLY` / `DETAIL_PAGES`. The module header said it was "unconstrained text". | Every old source *was* an HTML crawl. | Reuse `INDEX_ONLY` as an inert placeholder. The row ships `enabled = false`, so the crawl sweep never selects it. No migration. |
| `venue_candidates.lat/lon` NOT NULL | The old candidate sources (map discovery) always had coordinates. | Additive migration making them nullable, plus a null guard in the one admin row component that read them unguarded. The map view silently omits such rows, a gap the plan accepted and named. |
| A legal-source allowlist (`ALLOWED_SOURCE_TYPES`) on the write path | Old registry rows had all been hand-set to an allowed type. | Any other *legal* `source_type` value **silently dropped every event write**. The plan called this its highest-risk finding and made it a hard CLI validation that throws before any write, not help text. |

## Rules

- **Re-derive constraints from the schema, not from comments.** The header's
  "unconstrained" claim was doc-vs-code drift. The plan tags it `origin: upstream-wrong`
  and fixes the comment in the same branch.
- **A silent drop downstream becomes a loud check upstream.** When a gate the new path
  passes through can discard rows without an error, validate the triggering value at the
  entry point. See [[Parsed Then Dropped at the Insert Mapper]] for the same loss in the
  insert mapper.
- **Registry rows that need judgement are operator-supplied, never defaulted in code.**
  `content_sources` values come from CLI flags or a JSON file. The code checks only what
  the DB's own NOT NULL/CHECK constraints check.
- **Unmatched entities go to a review queue, never auto-created.** A location with no
  exact venue match becomes a `venue_candidates` row, matching the existing discipline
  that accepting a candidate creates a venue but never a crawl source. Matching stays
  exact-normalised, because fuzzy matching had scored two unrelated venues at 0.90.
- **Idempotent ids for foreign keys without a numeric id.** The feed's location id was an
  opaque string, and the target column was a bigint. The plan used a deterministic 32-bit
  hash, negated so it looks different from real positive ids, instead of a DB sequence. A
  sequence would insert a new row on every re-run instead of upserting. Collision risk at
  N≈424 was judged negligible, and a collision was recoverable by hand.
- **Dry-run by default and a production-confirm guard,** because one run writes four
  tables.

## When the matched-only path writes nothing (akira slice G, 2026-09-30)

The pilot was built on one rule: write events only for locations with an exact venue match,
and send everything else to the candidate queue. Then the number came in. **0 of 424**
distinct feed locations matched any venue, so the write path would produce **0 events** and
about 424 candidates. The rule had been decided before that measurement existed in this
form. The follow-on plan, which covered festivals as well, made these changes:

- **The parent becomes nullable, and the source FK stays required.** `events.venue_id` and
  `sources.venue_id` became nullable, following a sibling table (`activities`) that already
  had a nullable venue. An unmatched event is now written venue-less, and its location still
  becomes a candidate row. This supersedes the matched-only rule. The plan's biggest risk
  was the 19 non-test readers of the embedded venue, none of them checked for null, where a
  miss shows up as a 500 on the recommendations API.
- **Every new column names its reader.** `location_text` is read by the venue-less card,
  which still has to say where, and by a fallback dedup key. `venue_candidate_id` is a
  nullable FK read by attach-on-accept. When an operator accepts the candidate, every
  venue-less event carrying its id gets the new venue. The id gives an exact attach, which
  re-matching on text would not.
- **The natural key returns null without a venue,** so venue-less events fall back to title
  + start date + normalised location text. This is a key shape the duplicate detector
  already built.
- **"Not a venue" is curated, not inferred.** About half the festival locations that were
  named were street stages or "the city". A per-festival flag, `stages_are_venues: false`,
  means no candidate is created, with no heuristic. Locations outside the market are dropped
  with a named reason (`out_of_market`).
- **A latent defect dropped every write.** The legal filter required exact hostname
  equality between an event's URL and its source's `source_url`. The rights review seeded
  `source_url` as the API root (`api-v2.<host>/api`), while event URLs used the public host.
  So a config that followed the rights review would filter out every event as
  `disallowed_source`. A config that worked would upsert a second, unreviewed source row,
  because `source_url` is the upsert identity. The unit test passed only because its fixture
  used the working hostname. The same function would also have stored the API root as an
  event's fallback image URL.
- **Correct the draft's own claim, too.** A first draft said flipping the MVP flag would
  hand the API root to the generic crawler. Tracing the importer showed it only crawls
  sources bridged to a venue, and otherwise records `missing_legacy_source_bridge`. The flag
  was harmless but useless, adding one failure row per run until each source got a route.

## See Also
- [[Parsed Then Dropped at the Insert Mapper]] — related (silent loss at a typed boundary)
- [[Readiness Is Pinned to a Tree State]] — related (stale claims in issue and module text)
- [[Every Column Names Its Reader]] — related
- [[Natural Key Without a Discriminator Collapses Rows]] — related (the natural key that returns null without a venue)
