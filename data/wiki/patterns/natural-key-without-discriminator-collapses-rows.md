---
title: Natural Key Without a Discriminator Collapses Rows
tags: [foundations, pattern]
summary: An ingest upsert that matches on a natural key missing its discriminator (venue + title, but not date) silently merges distinct occurrences. One source would have collapsed ~1,800 dated occurrences into ~1,000 rows, and with no snapshot store the damage is repairable only by re-fetching everything, so the key must be fixed before the catalogue grows.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/playground/docs/ttd.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-14-listing-text-extractor.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-14-listing-text-extractor.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-14-listing-text-extractor.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-14-listing-text-extractor.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-14-listing-text-extractor.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-14-listing-text-extractor.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-14-listing-text-extractor.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis295-edition-boundary-remaining.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis295-edition-boundary-remaining.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis295-edition-boundary-remaining.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis295-edition-boundary-remaining.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis295-edition-boundary-remaining.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-22-dis295-edition-collision-fixture-set.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-22-dis295-edition-collision-fixture-set.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-22-dis295-edition-collision-fixture-set.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-22-dis295-edition-collision-fixture-set.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-22-dis295-edition-collision-fixture-set.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-16-pr306-stacked-issues.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-16-pr306-stacked-issues.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-16-pr306-stacked-issues.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-16-pr306-stacked-issues.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-16-pr306-stacked-issues.md
  - data/raw/repos/librarian/.claude--docs--plans--2026-07-31-LIB-60-session-note-derivation.md
---

# Natural Key Without a Discriminator Collapses Rows

## The defect

On an event-discovery app, the ingest upsert looked for an existing row by venue and
normalised title. **The date was never compared.** For a source averaging 1.84 occurrences
per attraction, every later occurrence matched the first one and updated it in place.
Ingesting that source would have collapsed roughly **1,800 distinct occurrences into ~1,000
rows**, each anchored at whichever date happened to land first.

Nothing fails. The upsert succeeds, the row count looks plausible, and the lost
occurrences leave no trace.

## Why it becomes unrecoverable

The fetched HTML was discarded after parsing, because there was no snapshot store. Once
rows have been collapsed, the only repair is to **re-fetch every page** (13,230 in that
case). The ordering consequence is the real lesson. Fixing the key before the catalogue
grows is a two-session job. Growing the catalogue first turns it into a permanent data
problem. The catalogue, not the code, became the gating item.

## Rules

- A natural key must include **every field that distinguishes two real-world instances**.
  For recurring entities, that is the occurrence date or time.
- This is the opposite failure to an over-strict key. [[Migration Done Means Pushed and Probed]]
  describes a natural key deliberately kept non-unique, so collisions route to review
  instead of failing the write. Both are decisions about what "the same thing" means, and
  both should be written down as a decision, not left implicit in an upsert.
- If you cannot store raw fetches, treat any key change as **irreversible** and sequence it
  before volume.

## Normalisation can erase the discriminator

A listing-page extractor (repo akira, 2026-09) keyed each item on a synthetic
`source_url` built as `normalize(base + "#" + id)`. The URL normaliser strips the
fragment, which is correct for real links. So every item on one listing page collapsed
onto the **same** key, defeating per-item occurrence keying. The fix normalises the base
first, then appends `#` plus the percent-encoded id *after* normalisation. The shared
normaliser is unchanged. Tests assert that two ids give two distinct URLs and the same
input gives the same URL. A read-only production count (no stored `#` keys, no URL shared
by more than one event) bounded the blast radius before merging. The discriminator was
present in the input and removed by a helper written for a different caller.

## When the discriminator doesn't exist yet (annual editions)

A later case on the same codebase (akira #295) was the harder version. Two annual
editions of a festival with the same normalised title at the same venue were merged into
one parent event. The occurrence date had been added by then. What was missing was an
**edition** boundary. The refine pass blocked the fix rather than guessing, for four
reasons:

- **The semantic discriminators were empty.** `event_series` and `organizer_id` existed
  as columns but were filled on 0 of 486 rows. A rule keyed on them would never fire.
- **A date-gap rule would split things that should stay together.** The longest
  same-key groups were generic programme and calendar pages ("Exhibition", "Kalender"),
  not annual editions. A rule like "more than 180 days apart means a new event" would
  wrongly split them, and no labelled data existed to calibrate any cutoff.
- **Stored rows can't rebuild the lost evidence.** Occurrence rows keep dates and URLs,
  not the title or description of each listing. Past false merges can't be labelled from
  the database alone.
- **A shipped partial fix is not the identity fix.** An earlier change let later
  listings refresh a draft parent's descriptive fields. That reduced stale copy, but
  distinct editions were still one identity.

The plan replaced build steps with an **unblock contract**. All four items must be
attached before a build plan is written:

1. A reviewed fixture table with source URLs and `same parent` / `new parent` labels. It
   needs annual-edition positives and recurrence/programme negatives.
2. The discriminator that is available at ingest time for every positive, and what
   happens when it is null.
3. Explicit acceptance thresholds for both errors: false merge (editions fused) and
   false split (duplicate identities).
4. A decision on whether the first delivery is prospective-only or also repairs rows
   already merged. Repair needs its own reversible mapping.

Identity corruption is irreversible in both directions. So the eventual change lands
behind a dry-run comparison, and the blocker is recorded as missing *decision evidence*,
not missing implementation capacity.

## Delivering unblock items 1, 3 and 4 (akira, 2026-09-22)

A follow-up slice built only the fixture table. The operator answered two of the
contract's questions:

- **Error budget: tolerate false merges over false splits.** A false split puts a visible
  duplicate into a 5-item slate, which is the worse user-facing failure. The existing
  parent-refresh already partly mitigates a false merge (stale copy on one row).
- **Prospective-only:** no repair of already-merged rows in the first delivery.

The collector only queries the database and emits **candidate pointers**, never labels:
groups by event, date spread, and a loose match against a curated annual-festival list.
The operator labels each pair by reading the live pages. The committed fixture shipped
empty, with a parse test that is green at zero rows (see
[[Own-Oracle Fixtures and the Blind Relabel Path]]). Cross-year festival positives are
sourced by hand from archive pages. If fewer than 10 real positives exist even then, that
is itself evidence that false-split risk is smaller than assumed.

## Deliberate repeats need an occurrence identity (akira, 2026-09-16)

A rater-assignment generator emitted a second row with the same (rater, item, batch) for each
deliberate repeat used to measure intra-rater consistency, but the table declared exactly that
triple unique, so any run with repeats failed the bulk insert and wrote no batch. Fix: give each
assignment **occurrence** its own stable identity, or add an occurrence discriminator to the key,
and test repeat insertion against a real database. The same review found the repeats appended
after the corpus and flagged `is_repeated` in the API response; repeats must be shuffled
deterministically per rater and their status kept server-side, or the rater can recognise them
and reproduce earlier answers.

## Date as the dedupe key (librarian session notes, 2026-07)

A session-note sync deduplicated on the filename date prefix (`p.stem[:10]`). Two
sessions on the same day share it, so every session after the first each day was
silently dropped. The derivation plan re-keyed dedupe on the session id, the actual
discriminator, which the date only approximated.

## See Also
- [[Migration Done Means Pushed and Probed]] — alternative-to (the over-strict key; this is the under-specified one)
- [[Ship Logging Before Features]] — related (another class of data recoverable only by waiting or re-fetching)
- [[Silence Reads as Clean]] — related (a successful upsert that destroyed data reads as healthy)
- [[Event–Occurrence Split, Added Behind the Old Column]] — related (the opposite failure: one event multiplied into many rows)
- [[Widen a Capped Vocabulary Without Displacing]] — related (found in the same listing-extractor build)
- [[Count What the Merge Already Folded]] — prerequisite-for (the merge's groups reused as a corroboration count)
- [[Own-Oracle Fixtures and the Blind Relabel Path]] — related (the fixture slice's check-vs-target split)
