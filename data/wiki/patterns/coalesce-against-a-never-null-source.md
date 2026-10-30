---
title: Coalesce Against a Never-Null Source
tags: [patterns, infra, pattern]
summary: "`coalesce(incoming, existing)` only protects a field when the incoming side can actually be null. A field whose upstream resolver always returns a value (an image with an event > venue > fallback chain) overwrites on every merge, silently downgrading good data — so give it a rank rule instead (refresh only when the incoming provenance is at least as good)."
updated: 2026-10-30
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis295-event-edition-identity.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis295-event-edition-identity.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis295-event-edition-identity.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis295-event-edition-identity.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis295-event-edition-identity.md
---

# Coalesce Against a Never-Null Source

From an akira plan that made a merged event row refresh its descriptive fields when a second
listing collapsed onto it under the natural key. Before the fix, `description`, `price_text`,
`ticket_url`, `image_url` and `category` stayed at whatever the **oldest** crawl said,
indefinitely. The losing listing's payload was computed and then discarded.

## The rule as first drafted

Refresh field by field, newest crawl wins, null-coalescing: `coalesce(incoming, existing)`,
so an incoming `null` never blanks a value already there. The refresh runs inside the same
transaction that already locks the parent row. It is guarded by
`review_status ∈ {draft, needs_review}`, the same guard the lifecycle code uses, so an
approved, published, rejected, duplicate or archived row is never silently rewritten.

## The trap found at refine

The draft applied the same coalesce to `image_url` and `image_source_type`. But upstream
of the write, an image-provenance resolver runs for **every** record, both the first insert
and each later merging listing. It always returns a truthy image through an
`event` > `venue` > `fallback` chain, so the incoming image is never `null`.

A coalesce against a never-null value is an unconditional overwrite. Every merge from a
listing with no picture of its own would have replaced an event-sourced image with the
venue's image or the site fallback. The image would have been silently downgraded on every
such merge. No test of the coalesce rule would catch this, because the rule worked exactly
as written.

**Fix: a rank rule for that field pair.** Replace the parent's image only when the incoming
`image_source_type = 'event'`. Otherwise leave it alone. The general form: when a resolver
fills gaps with lower-quality defaults, compare provenance rank, not nullness.

**Check before applying coalesce to a field:** trace every writer upstream of the merge and
ask whether that field can actually arrive as `null`. Defaults, fallbacks and
sanitizers all change the answer. A sanitizer that nulls over-length text *does* produce
nulls. For that field coalesce is correct, and the parent keeps its old description.

## Related findings from the same build

- **Coalesce needs an explicit `null`, not an omitted key.** The generated RPC argument types
  rendered every text parameter as `string | undefined` because the type generator cannot see
  the SQL `default null`. The call site had to widen the type with a commented cast so it
  could send `null` deliberately.
- **A plan test contradicted the plan's own invariant.** One integration case expected a
  sanitized-to-null merge to leave the parent `null`. Coalesce correctly kept the existing
  value. The fixture was changed to start from a parent with no description, so the case
  tested what it meant to test: that the raw over-length string never lands.
- **Content gates, dates do not.** Occurrence dates are re-derived on every merge whatever
  the review status. Descriptive content is gated. A live probe confirmed the split: after
  the row was flipped to `published`, a second merge added an occurrence row but left the
  description untouched.
- **Named cost, not resolved.** Any real content change alters the content hash, so it
  triggers paid re-enrichment. The decision row names this as accepted and leaves sizing to
  a separate issue.
- **No edition boundary yet.** A weekly club night and a festival edition a year apart look
  identical to the natural key. The plan declined to build a boundary because the fields to
  key it on (`event_series`, `organizer_id`) were populated in 0 of 486 rows. The widest date
  spreads (up to 366 days) were generic listing-page titles, which are extraction defects,
  not editions. A date-gap threshold was rejected as uncalibrated. The decision is deferred
  until real data or a measured collision exists. It is not rejected for good.
- **Adjacent ungated path, recorded not fixed.** Re-crawling the winning row's *own* URL went
  through a plain `upsert … onConflict: source_url` with no review-status guard. A published
  row whose source page changed was already being overwritten.

## See Also
- [[Re-Crawl Adds, Never Overwrites]] — contradicts (the later rule says a natural-key sibling never writes content; this refresh was kept as an open tension)
- [[Natural Key Without a Discriminator Collapses Rows]] — extends (what happens to the losing listing's content after the collapse)
- [[Event–Occurrence Split, Added Behind the Old Column]] — extends (occurrences carry the dates; this decides who owns the descriptive fields)
- [[Advance-Only Machine Writes on a Shared Lifecycle]] — related (the review-status guard keeps machine writes off human-approved rows)
- [[Migration Done Means Pushed and Probed]] — related (the RPC change shipped as a drop-then-create migration, probed live)
- [[SQL NULL and Three-Valued Logic]] — prerequisite-for (COALESCE semantics)
