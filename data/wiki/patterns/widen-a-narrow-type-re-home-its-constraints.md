---
title: Widen a Narrow Type, Re-Home Its Constraints
tags: [foundations, pattern]
summary: "A row type documented as 'deliberately narrow' is enforcing rules implicitly (every candidate has a start date; a title equal to the venue name is junk); widening it to admit a new kind of row is cheaper than parallel types, but each implicit rule must be re-homed as an explicit per-kind branch — and re-derived against what your own backfill wrote, because one heuristic rejected 100% of the new rows by construction."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-09-dis221-venue-model.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-09-dis221-venue-model.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-09-dis221-venue-model.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-09-dis221-venue-model.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-09-dis221-venue-model.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-09-dis221-venue-model.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-09-dis221-venue-model.md
---

# Widen a Narrow Type, Re-Home Its Constraints

From the akira venue-model plan: serving standing places (bars, restaurants, activities)
through a ranker built for dated events.

## The decision

Two shapes were presented rather than silently picked:

- **Widen** — the event row and scoring candidate gain a `content_kind` discriminant;
  only the hard-filter function and the pool query branch on it.
- **Parallel types** — new row interfaces, a discriminated-union candidate source, sibling
  filter functions; the event row untouched.

Widening won because the layer the ranker and diversity ledger actually operate on was
already vertical-agnostic (`start_at` already typed nullable). The divergence lived in one
DB-row-shaped type and one function. Widening one type and one function is smaller than
threading two new row shapes through every composition call site.

## The cost, stated rather than hidden

The type's own comment said *"deliberately narrow — extra columns are not our concern."*
Widening removes a constraint that was doing real work, so the plan had to replace it with
an equivalent:

- **Don't drop a clause, make it kind-aware.** The `missing_display_data` check (no
  `start_at` → junk) still applies to events; only standing content is exempt. A dated
  event with no start date must still be filtered.
- **Define expiry for rows with no dates.** Expiry was `end_at ?? start_at`. Standing
  content has neither, so visibility is gated by publish status alone — and a test asserts
  an undated row is never treated as expired *and* never treated as permanently fresh by a
  date-range filter.
- **Default the discriminant** to `'event'` at every existing call site, so every existing
  test runs unchanged as the regression guard.

## The constraint nobody listed

Implementation found one more implicit rule the plan had not scoped: a junk-title filter
rejecting any event whose title equals its venue's name (a common scrape failure). The
venue backfill had either matched an existing venue by exact normalized name or **created
one reusing the bar's own name** — so `title === venue.name` was true *by construction*
for every bar, restaurant and activity. The filter would have excluded 100% of the new
kind the moment it reached the pool. Fix: scope that clause to `content_kind === 'event'`.

The lesson generalises: when widening, enumerate every filter and heuristic that reads the
type, and re-derive each against **what your own migration or backfill wrote** — a backfill
can manufacture a heuristic's trigger condition.

## Null keys silently disable diversity caps

The diversity ledger's venue-repetition axis returned "no limit" when the key was null —
correct no-op behaviour, since events always had a venue. For hospitality rows, which had
no venue link until the backfill, the cap would silently pass three bars from one physical
place. This is a sequencing risk, not a code bug: the widening phase was gated on the
venue backfill being written *and* the forward ingestion path setting the key
([[Backfill Without the Forward Path]]), and an end-to-end test pins that three bars sharing
one venue admit exactly the repetition limit.

## See Also
- [[Event–Occurrence Split, Added Behind the Old Column]] — related (same catalogue; additive schema change that keeps old readers working)
- [[Backfill Without the Forward Path]] — related (the phase gate this widening depended on)
- [[Admit at Low Prior, Don't Exclude]] — related (standing content correctly has no start time)
- [[Natural Key Without a Discriminator Collapses Rows]] — related (a discriminant added to a shape that assumed one kind)
