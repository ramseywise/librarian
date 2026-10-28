---
title: Event–Occurrence Split, Added Behind the Old Column
tags: [foundations, pattern]
summary: "A catalogue that stores each dated row as an \"event\" can't tell a six-week exhibition from a Friday club night, lets one exhibition take three top-5 slots, and enriches it once per date. Split the event from its occurrences by adding a table, backfilling 1:1, and keeping the old date column as a maintained earliest-occurrence copy so ~60 readers keep working. Fix rather than rebuild when existing rows are your only parity evidence."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-b48-schema-remediation.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-b48-schema-remediation.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-b48-schema-remediation.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-b48-schema-remediation.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-b48-schema-remediation.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-b48-schema-remediation.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-b48-schema-remediation.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-05-dis73-occurrence-date-rule.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-05-dis73-occurrence-date-rule.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-05-dis73-occurrence-date-rule.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-05-dis73-occurrence-date-rule.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-05-dis73-occurrence-date-rule.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-05-dis73-occurrence-date-rule.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-05-dis73-occurrence-date-rule.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-10-dis73-occurrence-read-path.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-10-dis73-occurrence-read-path.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-10-dis73-occurrence-read-path.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-10-dis73-occurrence-read-path.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-10-dis73-occurrence-read-path.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-10-dis73-occurrence-read-path.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-10-dis73-occurrence-read-path.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis282-api-events-occurrence-expiry.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis282-api-events-occurrence-expiry.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis282-api-events-occurrence-expiry.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis282-api-events-occurrence-expiry.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis282-api-events-occurrence-expiry.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-15-dis73-occurrence-remaining-step12.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-15-dis73-occurrence-remaining-step12.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-15-dis73-occurrence-remaining-step12.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-15-dis73-occurrence-remaining-step12.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-15-dis73-occurrence-remaining-step12.md
---

# Event–Occurrence Split, Added Behind the Old Column

## The finding

A full data-engineering review of an event-discovery catalogue (repo akira), probed against
the live database, found that `events` did not distinguish an **event** from an
**occurrence**. 97 of 476 rows (20%) belonged to a multi-date run, including one
exhibition stored 49 times. A three-month gallery show was N rows or 1 row, depending only
on how its source paginated. That had three product consequences:

1. **The ranker could not tell a long-running exhibition from a one-night event.** Both are
   "an event tonight", but they mean very different things for "tonight, with friends".
2. **Diversity limits ran on venue or organiser, not identity**, so three of the top five
   slots could be the same exhibition.
3. **Enrichment paid per row.** The 49× exhibition was model-enriched 49 times for one
   underlying thing. Making enrichment per-event was a bigger saving than the content-hash
   skip it sat beside, which saved about $15 a year on its own.

The same split also settled a long-open modelling question: **an activity is an event with
an open-ended recurrence.** Separate `activities` and `bars` tables (2 and 35 rows, read
by nothing in serving) had been costing triplication and buying nothing.

## The additive migration

- **Add, don't replace.** A new `event_occurrences` table (event FK, start/end,
  `source_url` as provenance) is backfilled 1:1 from `events`. Today every event *is*
  one occurrence, so the backfill is lossless and reversible.
- **Keep the old column as a maintained copy.** `events.start_at` / `end_at` stay and
  become the earliest and latest occurrence, maintained by the importer. Every one of the
  ~60 files that read `event.start_at` off an already-fetched row keeps working.
- **Measure the blast radius as *queries*, not references.** 64 files mentioned
  `start_at`, but only about seven *queried* on it (candidate load, publish predicate,
  public listing, admin queue, the visibility filter). Those migrate one at a time.
  Dropping the old column is a separate, later decision, made once the last query has
  moved.
- **Importer identity moves to the natural key.** Identity resolves on (venue,
  normalised title), then the importer upserts the occurrence keyed on
  (event, start, source_url). Upserting on `source_url` alone was right for provenance,
  and it was exactly why URL-shape variation multiplied the catalogue: the same event at
  `/x/20384` and `/x/20384/57823` became two rows.
- **Normalise titles for matching only, and fall back on junk.** 11% of titles were junk
  (venue name as title, leading dashes, fewer than 4 characters). The stored title is never
  overwritten. Where the normalised title is empty or junk, identity falls back to
  `source_url`, because bad extraction merging two unrelated events is **worse than a
  duplicate**.
- **Order the clean-up after the merge.** Routing the 17 existing duplicate pairs to
  `review_status = 'duplicate'` runs *after* occurrence identity, because the merge
  resolves some pairs structurally.

A retroactive review of the plan still found that the natural-key lookup ignored
`start_at`. That is the under-specified-key failure described in
[[Natural Key Without a Discriminator Collapses Rows]]. Splitting occurrences out does not
remove the need to decide what "the same event" means. It moves that decision into the
event key.

## When the maintained copy lies to its readers

A follow-up issue asked *"how far apart do two rows have to be to count as two
occurrences?"* Tracing the code showed the question was wrong: occurrences were already
modelled. The occurrence table had been built and was written on every ingest, but **no
serving query read it**. Only the importer touched it. The "every column names its reader"
rule (see [[Every Column Names Its Reader]]) applied one level up, to a whole table.

The maintained-copy column is what made this a live defect rather than dead weight:

- The importer collapsed a run onto its oldest row and rewrote `start_at` to the
  **earliest** occurrence. It updated `end_at` only if some occurrence had one.
- Both expiry readers computed `end_at ?? start_at < now` on those collapsed columns.
- A weekly club night with no end time became one row anchored at the first Friday. It
  **read as expired from that Saturday on**, while the occurrence table still held every
  future date.

"Keep the old column so ~60 readers keep working" holds for readers that want *a* date.
It fails for readers whose meaning depends on *which* date, such as expiry, next showing,
or repetition caps. Those readers have to move to the new table first.

The decision split the issue into three sub-questions, each mapped to a consequence the
schema review had already named:

1. **Liveness.** An event expires only when no occurrence has `end_at ?? start_at` in the
   future. Both expiry readers move together.
2. **Display identity.** Show the next occurrence everywhere for now. "Open until 20 Dec"
   framing for continuous runs was **deferred until a series classifier exists**, because
   every row's series type read "Unknown", so there was nothing to branch the display on.
3. **Repetition limits.** The top-5 cap keys on event identity (venue + normalised title),
   not on venue. Six showtimes of one film then count once, and three different films at
   one cinema are not wrongly suppressed.

The threshold the issue was filed for **did not survive**. Occurrence identity is exact,
so there is no distance to tune. Cross-source near-duplicates belong to duplicate
detection. Saying so explicitly matters, because the issue title would otherwise keep
implying there was a threshold to design.

A cost was named and left for the implementation plan: the content hash covered
`start_at`, so a schedule-only change (a corrected showtime, a newly seen date) would
trigger a full paid re-enrichment.

## Fix, not rebuild

The review's headline decision was to fix the schema rather than rebuild it, and the
reasoning holds generally:

- **Size the damage honestly.** It was three things: four status columns where one was
  read, no index on the hot filter, and uniqueness on the wrong key. Date prefixes on
  migration *files* were convention, not a defect.
- **The hard parts were already right**, and a rebuild would have had to reproduce them:
  the versioned-supersede enrichment model (which took three migrations to get right), the
  RLS policies, and the deliberately denormalised telemetry schema.
- **Existing rows were the only parity evidence.** 303 enrichment rows and 117 QC verdicts
  from the original pipeline were the only proof the ported chain matched its predecessor.
  A rebuild either migrates them (all the work, none of the freshness) or throws the
  evidence away.
- **Name what the fix does *not* buy.** The catalogue was 94% unknown price, 45% missing
  image, 26% null start and 11% junk titles. A perfect schema over that data still demos
  badly. The plan said so and pointed to extraction quality as the real demo blocker.

## Retention decided before volume

Bytes per row were measured, not estimated. 54% of enrichment bytes were write-once,
read-never `raw_*` audit payloads, and history ran at 3.17× current rows with no pruning.
Money was not the constraint (about $30–40 a month at projected volume). The policy (past
events archived after 90 days, current plus 2 superseded enrichments, raw payloads dropped
after 30 days) was **decided now and built later**, so the shape is fixed before millions
of rows arrive rather than retrofitted under them.

## The read-path follow-through

Keeping `events.start_at` as the earliest occurrence left a known bug. A merged event
whose earliest occurrence was in the past had a stale `start_at`, so every expiry check
reading that column hid it, even with future occurrences still to come. The follow-up
issue (#73, closed 2026-09-15 after four PRs were merged into two) found:

- **The same predicate had more consumers than the decision plan listed.** It was baked
  into the candidate loader's SQL, the shared visibility helper, the detail page's
  single-row fetch (a stale event 404'd there rather than showing a wrong card), and a
  poll-creation query that layered its own `start_at` window on top. That last one was an
  eligibility bug, not a display bug. Two of these were found only in later refine passes
  over a moving tree. That is the case for [[Audit the Class, Not the Instance]].
- **A PR cut that fixes eligibility without fixing display is a louder regression.**
  Re-admitting a merged event to the pool without changing what its card shows would have
  served today's recommendation with a months-old date. The split was corrected so the
  expiry fix and the next-occurrence display landed together.
- **Test each hop of a prop-threading chain.** Next-occurrence data passes through five
  files (loader, item, wire, card, detail). If one hop is left out, the old date keeps
  showing and nothing errors. So each hop got its own test, not a single end-to-end
  assertion.
- **Moving the filter out of SQL changed what the cap drops.** See
  [[Dropped Filter Flips the Truncation Direction]].
- **Staff surfaces were scoped out by name, not dropped silently.** Three admin queues
  read the raw column. That is correct for their job (they show pending rows whatever the
  expiry), but they display a stale date. The plan named this as a follow-up rather than
  leaving it undiscovered.
- **Reuse the threshold two implementations already agree on.** The natural-key title
  minimum (4 characters) was already declared twice. The plan made one shared constant
  with three readers rather than adding a third copy. See [[The Untested Copy Wins]].
- **Irreversibility raised the bar for testing.** With no raw snapshot store, occurrence
  rows were the only record. The plan did pure reads only, with RED-before-GREEN tests.

## Delete the dead caller rather than fix it (akira DIS-282)

The last callers still reading the collapsed date were the `/api/events` routes. They looked
like the start of a partner API, so the first instinct was to give them occurrence-aware
expiry. The plan deleted them instead:

- **They bypassed both rights gates.** The routes served catalogue rows without the
  licensing and visibility checks the recommendation path enforces. Fixing their expiry
  would have made a rights leak more correct.
- **In-memory expiry breaks SQL pagination.** Filtering occurrences after the query means
  `count` and `offset` describe rows the client never sees, so pages come back short and
  totals are wrong. Occurrence expiry has to be in the query, or the endpoint should not
  paginate.
- **The partner surface gets built on the gated path.** A future partner REST API starts
  from the recommendations read path, which already carries the rights gates and the
  occurrence-aware expiry, not from the dead routes.

## What review found on the read path (akira reviews, 2026-09-14/15)

- **Removing a filter from a shared helper widens every caller.** PR 1 dropped the SQL expiry
  disjunction from the shared app-visibility helper. Four callers outside the diff, including
  the detail page and the events API, loaded no occurrences and did no in-memory expiry check,
  so they would have served expired events. The fix kept the disjunction in the helper and
  scheduled its removal per surface, in the PR that gives that surface an in-memory check.
- **The range filter still keyed on the collapsed anchor.** A ranged request ("this weekend")
  narrowed in SQL on `start_at` and then compared the collapsed anchor in memory. An exhibition
  with a Saturday occurrence was dropped on the main path, so only the unranged path benefited.
  Range membership has to ask whether any un-ended occurrence's local start day is in the range.
  Take the day from `start_at ?? end_at`, so an end-only occurrence is not dropped.
- **The fallback contract was documented backwards.** The module doc said `[]` reads as
  expired. Both callers treated `[]` like `undefined` and fell back to the legacy formula. The
  code was right, because most events have no occurrence rows. The doc was corrected and one
  test pins `[]`.
- **A "widened by a day" comment that widened nothing.** Both SQL range bounds used `T00:00:00Z`
  to `T23:59:59Z`, so an occurrence at 00:30 local time on the range's first day was excluded.
- **An anon-client read of a no-policy table returned nothing.** See
  [[Written-but-Inert RLS Policies]]. Unbounded joins under the row cap are covered in
  [[Bounded Slice After In-Memory Eligibility]].
- **A rejected suggestion, with its reason.** A reporter proposed sorting next occurrences on
  `end_at ?? start_at`. That was rejected: an exhibition that is already running is the soonest
  thing a visitor can attend, so it should sort by start.

## See Also
- [[Dropped Filter Flips the Truncation Direction]] — extends (found in the read-path follow-through)
- [[Natural Key Without a Discriminator Collapses Rows]] — related (the opposite failure: occurrences merged into one row)
- [[Migration Done Means Pushed and Probed]] — related (the same review produced the schema conventions on that page)
- [[Two AI Cost Economies: Durable Once, Contextual On Demand]] — related (churn and per-row enrichment beat any model swap on cost)
- [[Data Clusters by Writer and Trust]] — related (the follow-on schema convention for the same catalogue)
- [[Every Column Names Its Reader]] — extends (the occurrence table itself had no serving reader)
- [[Re-Crawl Adds, Never Overwrites]] — related (how the hash-covers-dates re-enrichment cost was closed)
- [[Widen a Narrow Type, Re-Home Its Constraints]] — related (widening a model type and moving its invariants)
- [[Env Inventory Gate Enforced in One Direction]] — related (the same change hit the index-vs-disk gate crash)
