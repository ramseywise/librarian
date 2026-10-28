---
title: Guard at the Funnel, Fix at the Cause
tags: [patterns, rag, pattern]
summary: "When a parser emits garbage values, fix it at three layers. Put a plausibility bound at the single function every branch returns through, so nothing escapes. Fix the extractor at the cause, so real values are recovered rather than nulled. Keep the drop-or-flag decision at the importer, so policy stays in one place. Both bounds share constants."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-08-26-b3b-date-sanity.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-26-b3b-date-sanity.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-26-b3b-date-sanity.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-26-b3b-date-sanity.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-26-b3b-date-sanity.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-26-b3b-date-sanity.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-26-b3b-date-sanity.md
  - data/raw/claude-docs/akira/docs/reviews/2026-08-26-b3b-date-sanity.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-08-26-b3b-date-sanity.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-08-26-b3b-date-sanity.md
  - data/raw/claude-docs/playground/docs/reviews/2026-08-26-b3b-date-sanity.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-08-26-b3b-date-sanity.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-08-26-b3b-date-sanity.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-08-26-b3b-date-sanity.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-14-listing-text-extractor.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-14-listing-text-extractor.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-14-listing-text-extractor.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-14-listing-text-extractor.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-14-listing-text-extractor.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-14-listing-text-extractor.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-14-listing-text-extractor.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-14-dis265-activity-date-range.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-14-dis265-activity-date-range.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-14-dis265-activity-date-range.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-14-dis265-activity-date-range.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-14-dis265-activity-date-range.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-14-dis265-activity-date-range.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-14-dis265-activity-date-range.md
---

# Guard at the Funnel, Fix at the Cause

This comes from a date-sanity plan and its review in the akira event pipeline. Parsed event dates
showed years from 1011 to 2619. The cause was an unanchored first-match regex, `/(\d{4})/`. Its
variable name, `trailingYearMatch`, claimed the year came from the end of the string, but the
regex took any four-digit group anywhere. It caught house numbers and URL slugs, including in
the page URL, which was passed in as fallback text.

## Asymmetric damage

The two directions of garbage did different harm, so a review should not treat them as one bug:

- **Past garbage** (year 1011) was absorbed by the existing "event already ended" expiry filter.
  It was invisible and harmless.
- **Future garbage** (year 2619) passed every filter and was **served**.

## Three layers, each with one job

| Layer | Where | Job |
|---|---|---|
| Plausibility bound | The single date-builder that all 10 parser branches return through | Return `null` outside the window. The null flows into the existing `missing_start_at` review path, so no new handling is needed |
| Fix at the cause | The regex | Anchor the year match near the day/month, so real dates are *recovered* rather than nulled by the bound |
| Policy | Importer-level invalid-date guard (kept) | Owns the decision to drop the row or flag it for review |

The bound goes at the funnel because a check in each branch would miss the next branch
someone adds. Fixing the regex is still needed, because the bound on its own turns a recoverable
date into a missing one. The importer guard stays because the decision between dropping and
flagging is policy, and policy should live in one place, not inside a parser.

## Details that matter

- **Shared constants.** The parser bound and the importer guard read the same window
  (2025-01-01 to now + 24 months). If the two drift apart, rows can pass one and fail the other.
- **Pin the edge with a test.** A regression test covers a legitimate event 18 months out, so a
  later tightening of the window does not silently drop real far-future listings.
- **Wire the dormant path too.** A second importer path that was unused at the time got the same
  guard, so it would not reintroduce the bug when re-enabled.
- **Cleanup nulls and flags; it does not delete.** Existing bad rows get `start_at = null` and
  go into the review queue. The event may well be real; only the date is wrong.

## Follow-up: greedy digit capture and fabricated days

A later fix to the same shared German date parser (repo akira, 2026-09) found a related
cause. The parser had no branch for "day + German month name, no year" (`15. September`),
so such text fell through to an English-month branch. That branch's `\d{1,2}` day capture
greedily took an adjacent token, either the clock hour in `20:00` or the first two digits
of `2026` in "until early November 2026". The fixes:

- **Add the missing branch before the permissive one,** with an explicit year rule: a
  yearless date is the current year, unless its month is before the current month (then
  next year).
- **Bound the digit capture** (`(?![\d:])`, whitespace before it) so it cannot take a time
  or part of a year.
- **A month with no day returns `null`,** never a fabricated day.
- **Make `now` injectable** (`parseGermanDate(text, now = new Date())`) so the year
  inference is deterministic in tests.

The corpus-level "zero regressed sites" check came back byte-identical before and after
the fix. That was expected and uninformative, because the "kept" metric never reads
`start_at`. A fabricated day 20 instead of a correct day 22 still reaches the stored row.
Check that a regression metric can see the defect before treating its silence as evidence.

## See Also
- [[Sanitize Never Fails, Validate Never Mutates]] — related (the bound returns null and the importer decides)
- [[Layered Ingestion Failure Posture]] — instance-of (row-grain flag rather than drop)
- [[Fallback Mistaken for the Design]] — related (the page URL fallback was the source of fake years)
- [[Silence Reads as Clean]] — related (past garbage was hidden by the expiry filter)
- [[Dated Node Must Name the Row]] — related (a plausibility guard on activity run dates, failing toward serving)
- [[Widen a Capped Vocabulary Without Displacing]] — related (the metric that could not see the date fix)
