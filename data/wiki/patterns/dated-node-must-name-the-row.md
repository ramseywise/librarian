---
title: Dated Node Must Name the Row
tags: [patterns, foundations, pattern]
summary: "An attribute borrowed from a sub-node of a page (an exhibition's end date on a museum's row) belongs to the row only when that node is named exactly as the row — containment is deliberately not a match — and a missing or rejected value must fail toward serving, so a bad parse can never empty the supply."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-14-dis265-activity-date-range.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-14-dis265-activity-date-range.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-14-dis265-activity-date-range.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-14-dis265-activity-date-range.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-14-dis265-activity-date-range.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-14-dis265-activity-date-range.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-14-dis265-activity-date-range.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis270-publish-automation.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis270-publish-automation.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis270-publish-automation.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis270-publish-automation.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis270-publish-automation.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-16-dis270-publish-automation.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-16-dis270-publish-automation.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-16-dis270-publish-automation.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-16-dis270-publish-automation.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-16-dis270-publish-automation.md
---

# Dated Node Must Name the Row

Found while planning start/end dates for standing content ("activities": museums,
galleries, running exhibitions) in an event-discovery product (repo akira, 2026-09). The
goal was simple: an exhibition past its end date stops being served and stops counting as
published supply. The trap was in *which* row the date gets written to.

## The defect the plan almost shipped

The extractor picks the **first** JSON-LD node on a page whose type is any of
`ExhibitionEvent · Event · TouristAttraction · Place · LocalBusiness`, and takes title, URL
and dates from it. The planner's risk table said this was safe: "the row's title and URL
come from the same node, so a row built from an exhibition node IS that exhibition."

That claim was false. The row's **name** does not come from the node. It comes from the
registered content source (`name = input.name || extracted.title || sourceName`), and the
only production caller passes the source name unconditionally. So a source registered as
a museum, whose homepage's first JSON-LD node is its current exhibition, produces a row
titled with the museum's name and stamped with **that exhibition's** `ends_on`. When the
show closes, the read path hides the museum and the daily sweep archives it.

It looked safe because the only test on that path passed `name: ''`, so its row *was* named
after the node. The fixture took the one branch production never takes.

## The rule

- **Only nodes that can carry the attribute.** Dates are read only from `ExhibitionEvent`
  or `Event` nodes. `Place`, `TouristAttraction` and `LocalBusiness` have no
  `startDate`/`endDate` in schema.org, so a stray value there is not a run.
- **The node must name the row.** The dated node's run is kept only when its name equals
  the row's name, compared after lowercasing, collapsing whitespace and trimming trailing
  punctuation. Otherwise the run is dropped to `null`.
- **Containment is deliberately not a match.** "Museum X" ⊂ "Museum X: Show Y" is exactly
  the museum-stamped-with-a-show failure. Strict equality costs some recall (an exhibition
  source whose registered name differs from its JSON-LD name gets no dates and behaves as
  before), and that cost is accepted. A value that is not what it claims is worse than
  none.
- **Write the regression test with the production argument shape.** The fix was proven
  RED-first with the museum fixture under the real registered name, not `name: ''`.

## Null fails toward serving

`null` means *ongoing*. A missing, implausible or rejected date leaves the row served, so a
bad parse can never empty the activity supply. The cost: an exhibition whose page carries
no machine-readable end date still needs a human to unpublish it, which is the previous
behaviour, not a regression. Fail direction is chosen per consequence. For an expiry
filter, failing toward hiding is the expensive direction because it silently removes real
supply.

## Supporting decisions from the same plan

- **Guard where every consumer reads.** The importer already extracted the dates and
  handed the raw strings to the enrichment prompt. Only the upsert dropped them
  ([[Parsed Then Dropped at the Insert Mapper]]). The plausibility guard had to sit
  upstream of both consumers, not only in the upsert.
- **One predicate, several callers.** A single pure `isEndedActivity` rule (Berlin-local
  "today", inclusive, so a show is still served on its last day) feeds the hard filter, the
  archive sweep and a pandas mirror in the supply notebook. The mirror's cell comment names
  the TypeScript function it copies. Same shape as [[Deadline Transition Computed on Read]].
- **Expiry stays out of RLS.** A time-dependent row policy changes visibility with no write,
  so the public-read policy stays `review_status = 'published'` and hiding is a read-path
  filter.
- **No second lifecycle column.** An existing `availability_status = 'expired'` value and a
  jsonb field were both rejected. The first would be a second visibility workflow; the
  second gets no SQL filter and no CHECK constraint. Archiving writes the existing
  `archived` status.
- **The sweep is not self-reversing.** Events have a re-publish script; activities are
  published by a human. An archived activity whose run is later extended stays hidden
  until someone republishes it. This was accepted explicitly at sign-off, not discovered
  later ([[Advance-Only Machine Writes on a Shared Lifecycle]]).
- **Future starts follow the event rule.** An activity that opens next month is outside a
  requested date range but served on the no-range path, exactly like a future event. That
  avoids a new exclusion reason, copy change or tally change.
- **Insert-only upserts strand new columns.** A sibling plan made the activity upsert
  insert-only on re-crawl ([[Re-Crawl Adds, Never Overwrites]]). Dates written only into
  the insert payload therefore reach new rows only. Two plans touching the same writer need
  their assumptions about overwrite behaviour reconciled.

## The caller the predicate still missed: the publish gate

A day after the shared predicate shipped, the activity vertical of a new automated publish
engine merged **without reading the run-date columns at all**. Its column list, candidate type
and blocker function had no knowledge of them, and `now` was not even in scope inside the gate.
The predicate had three readers (the serving read path, scoring eligibility, the archive sweep),
and the publish gate was the fourth place it belonged. The consequence was a **publish/archive
flap**: an activity in `draft`/`approved` whose run had ended cleared every gate, was marked
`published`, and was then swept to `archived` by the next step of the *same* workflow run.

- **Fix at the gate, not with step ordering.** Running publish before archive was chosen for
  cadence (import → enrich → QC → publish → archive, as already documented) and for same-day
  archival of rows that ended after publishing. It is not what makes "never publish an ended
  activity" true. A distinct `run_ended` blocking reason in the activity validator does that,
  whatever the step order or the row's current status.
- **Reuse the predicate, do not re-derive it.** The validator imports the same
  `isEndedActivity`, so the gate and the sweep cannot drift on what "ended" means. Review called
  this the structural reason the fix lives at the gate: it stays inclusive on the last day, and a
  null end date is never "ended".
- **A new reason, not an overloaded one.** An existing `expired` reason already meant a
  source-set availability status. A computed date-range check is a different fact, so it got its
  own name.
- **`now` is an injected, defaulted parameter**, matching the event validator, so tests pin a
  fixed date. Three targeted tests failed against the unfixed gate and passed after.
- **Query-level narrowing was deferred on purpose.** Loading an already-ended activity only to
  report it `BLOCKED` is correct, not a bug. The SQL optimisation waits for real row volume.

## See Also
- [[Mislabelled Column Is Worse Than Missing]] — related (the same "a wrong value is worse than none" stance)
- [[Guard at the Funnel, Fix at the Cause]] — related (plausibility guard returns null, never a guess)
- [[Artifact Is Not Evidence: Push and Probe]] — related (the plan's read path selects the new columns, so the migration must be pushed and probed first)
- [[Deadline Transition Computed on Read]] — instance-of (one shared expiry predicate across readers)
- [[Natural Key Without a Discriminator Collapses Rows]] — related (another identity mistake that leaves no trace)
- [[Arm Unattended Writers by Risk Type]] — related (the publish step this gate protects ships disarmed)
- [[Event–Occurrence Split, Added Behind the Old Column]] — extends
