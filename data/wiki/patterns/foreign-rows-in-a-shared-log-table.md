---
title: Foreign Rows in a Shared Log Table
tags: [patterns, eval, pattern]
summary: "When a new surface logs into a table built for another one (similarity lists into the ranker's result-set log), give the foreign rows a discriminator and distinct version stamp. Then scope every reader by it, including child tables that lack the discriminator and must be filtered through parent ids. A failed parent read makes the child metric unknown, not zero. 'Excluded by construction' is a claim to test, not to write in a README."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-21-dsk-355-a1-detail-places-similar.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-21-dsk-355-a1-detail-places-similar.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-21-dsk-355-a1-detail-places-similar.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-21-dsk-355-a1-detail-places-similar.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-21-dsk-355-a1-detail-places-similar.md
---

# Foreign Rows in a Shared Log Table

From an akira plan that added a "Similar vibe" list to detail pages. The decision was to
log each similarity list as a full result-set row in the ranker's existing log table, with
`surface = 'similar'`. The schema already allowed the value, the items column was JSON
(so no migration), and the interaction sink already verified that table's signed tokens.
The cost: every reader of the ranker log now held rows that were not ranker output.

## Make foreign rows self-identifying

The similarity rows stamp `ranker_version = 'similarity_v0.1'`, put the similarity score in
`final_score`, and zero the score components. A decision row recorded the rule: **every
ranker-metric reader must filter on `surface`**. The plan's risk list also had a step
check the dashboard's metrics query for a surface filter, and add one if it was missing.

## The child table is where it leaked

The result-set sections already grouped by `surface`. The interactions table (card opens
and similar events) carries **no `surface` column of its own**. Review found that the
interaction-rate section counted card opens on similarity lists as ranker traffic. The
observability README claimed the exclusion happened "by construction". It did not. The
fix scopes interactions to the `result_set_id`s of already-fetched non-similar sets, and
switches the per-set denominator to the non-similar count. A test asserts that a
similarity set's card opens are excluded. The README was rewritten to describe the actual
filter.

Rule: when a discriminator lives only on the parent, every child-table metric is a join
through parent ids, and a test should pin it.

## Unknown is not zero

A second review round made each of the dashboard's four parallel metric reads check its
own error, log it, and render a per-section "unavailable" notice plus a page-level alert.
The interaction section is blanked if **either** the parent read or the child read fails.
Its numbers come from filtering children through parent ids, so a failed parent read makes
the count unknown even though the child read succeeded. The "no recommendation data" empty
state is also suppressed whenever any read failed, so a failure never renders the same copy
as genuine zero traffic. See [[Degrade the Render, Surface the Failure]].

## Two smaller lessons from the same build

- **A recorder failure must propagate.** If writing the log row rejects, the door function
  rejects too. A list is never served unlogged, which is the replay guarantee of
  [[Replayable Slate Ranker]].
- **A one-row fixture cannot exercise a similarity section.** The shared e2e seed held one
  event, so nothing could clear the similarity threshold and the section always rendered
  null. The fix round recorded a deviation instead of writing a test that could never
  assert anything. Growing the shared seed would have forced re-baselining every
  screenshot spec that used it.

## See Also
- [[Replayable Slate Ranker]] — extends (the result-set log these rows share)
- [[Rate Metrics Measure the Logger]] — related (a rate is only as clean as what the logger admits)
- [[Degrade the Render, Surface the Failure]] — related
- [[Silence Reads as Clean]] — related (failed reads rendered as empty traffic)
- [[Data Clusters by Writer and Trust]] — related (a second writer into an existing table)
