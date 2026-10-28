---
title: The Eval Harness Has Its Own Adapter
tags: [patterns, eval, pattern]
summary: "A modifier that reads as dead in an eval trace may be dead only in the harness: the eval harness had its own copy of the row-to-candidate adapter, which read a bucketed field instead of the raw one, so the fix belongs at the harness boundary — and when the frozen corpus itself lacks the field, prove the fix with a small synthetic fixture and say the real number won't move, rather than reporting a still-zero result as success."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-25-dis392-b130-s3.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-25-dis392-b130-s3.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-25-dis392-b130-s3.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-25-dis392-b130-s3.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-25-dis392-b130-s3.md
---

# The Eval Harness Has Its Own Adapter

From repairing "dead modifiers" in a ranking pipeline in an events-discovery product
(repo akira, 2026-09-25). An earlier trace found three scoring modifiers that were
constant across a 200-venue corpus. The repair plan traced each one to its cause before
touching code.

## Two dead modifiers were real absence, one was a bug

- Two modifiers read fields that the pipeline producing the corpus **never emits**.
  Those are enrichment-pipeline fields that the probe schema doesn't produce. There was
  nothing to fix in code. Making them live means deciding whether the probe should emit
  those fields, which is a schema design question. It went to its own ticket.
- The third, a subtype penalty, was a real defect. Telling the two cases apart comes
  first, because only one of them has a code fix.

## The bug lived in a second adapter

The penalty's lookup table was keyed in raw `key:value` form (`amenity:fast_food`), the
same form the real OSM-tag mapper produces. Production was fine: the feed's
`toScoringCandidate()` read the real `place_subtype` column.

The eval harness had **its own** `toScoringCandidate()`, used by the comparison table,
the trace, and the ranker arm. It set `place_subtype` from `venue_kind`, a deliberately
**bucketed** value (`fast_food` is folded into `restaurant` on purpose), so it could
never match. The harness's corpus type had no `place_subtype` field at all, so the
adapter had nothing else to read.

**The fix goes at the harness boundary, not the lookup table.** Changing the table's
spelling to match the harness would have broken the one path that worked. The corpus
type got a real field, populated from data already in the JSONL with no DB read, and the
harness adapter now reads it.

The same confusion explained an odd earlier number: the trace's "4,940 restaurant rows"
was counting the bucketed value under a raw-field label. After the fix, the report reads
the real field and the mislabel disappears.

## When the frozen corpus can't prove the fix

The corpus also carried `place_subtype` as a key on every row, but it was **null on all
200 rows**. The corpus was built before the backfill that populates it. So the code fix
alone could not make the real trace move.

The plan did not report a still-zero number as success, and it did not invent corpus
values:

- A small committed synthetic fixture (two fast-food rows, one restaurant, one bar, one
  null) runs through the **whole** harness path (corpus row → adapter → trace), not just
  the penalty function in isolation.
- The real-corpus gap is written down as an operator follow-up: regenerate or backfill
  the corpus. "Do not backfill the fixture with invented values to fake a real-corpus
  result" is listed under Risks.

## Rules

- When a metric says a modifier is dead, check **every** adapter that builds its input.
  Grep for every constructor of the field, not just the production path.
- Normalise at the boundary that is wrong, not the one that already agrees with the real
  producer.
- A required field on the corpus type makes `tsc` find every construction site (see
  [[Required Field as Exhaustive Site Finder]]).

## See Also
- [[A Fake That Conforms to a Broken Seam]] — related (test-side code faithfully reproducing a wrong shape)
- [[Required Field as Exhaustive Site Finder]] — extends (how the missed construction sites were found)
- [[Starved Tag Triage: Edge, Prompt, or Supply]] — related (same series; absence vs defect triage)
- [[Hydration Gap Silent Input Loss]] — related (an input silently dropped before it reaches the logic)
- [[Kiez Project]] — instance-of
