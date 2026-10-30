---
title: Insert-Only Upserts Strand Normalizer Fixes
tags: [patterns, infra, pattern]
summary: "Once an upsert stops rewriting existing rows, a normalizer fix reaches newly inserted rows only, so every existing row keeps the old wrong values; a fix plan must name its route to old rows: a dry-run-default backfill that overwrites only values still equal to the known-bad defaults, a scoped refresh, or an explicit exception."
updated: 2026-10-30
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-14-dis263-accepted-candidate-bridge.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-14-dis263-accepted-candidate-bridge.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-14-dis263-accepted-candidate-bridge.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-14-dis263-accepted-candidate-bridge.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-14-dis263-accepted-candidate-bridge.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-14-dis263-accepted-candidate-bridge.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-14-dis263-accepted-candidate-bridge.md
---

# Insert-Only Upserts Strand Normalizer Fixes

From the akira venue-to-content bridge plan, via a cross-plan note from a sibling plan.

## The mechanism

The bridge fixed four defects in the single-page normalizer: a constant type value, a
regex-guessed type, a missing venue id, and a dropped description. A sibling plan, landing at the
same time, made the place upserts **insert-only** so that a re-crawl never overwrites editorial or
content columns a human may have touched.

Together those two changes mean the fixes land on new rows only. Every existing row keeps a null
venue id, the constant type, and the regex type indefinitely. Nothing errors and nothing looks
stale. The two plans were each correct on their own; the gap only appears when you read them
together.

## Name the route to old rows

The note required the fix plan to name one of three routes:

| Route | Reach |
|---|---|
| A backfill script in the ops folder | Any column; the default |
| A scoped refresh import of named row ids | Same-URL rows, content columns only, so it cannot reach the venue id or type columns |
| An approved exception to insert-only (for example fill-if-null for the venue id) | Narrow, but changes the write contract |

The plan took the backfill. Its rules are reusable:

- **Pure match function plus a thin apply, dry-run by default.** Only the pure function is
  unit-tested; the human runs `--write`, never the agent.
- **Overwrite only values still equal to the known-bad defaults.** A row whose type is not the old
  constant or the regex output was edited by hand, so the backfill leaves it alone.
- **Apply only confident matches** (exact URL, or normalised name), and report the rest.

## Also crossing the seam

Aligning the two place upserts' conflict keys (one keyed on source URL, the other on slug) moved
the sibling plan's existence-read key in the same line. Two plans editing the same functions
should each carry the build-order note; here only one side had it until a refine pass copied it
back.

## See Also
- [[Done-When the Cheapest Write Can Meet]] — related (same plan)
- [[Mislabelled Column Is Worse Than Missing]] — related (old rows keep a plausible wrong value)
- [[Every Column Names Its Reader]] — related (the same plan's description column was deferred until its reader landed)
- [[Re-Crawl Adds, Never Overwrites]] — extends (the rule that made the upserts insert-only)
- [[Backfill Without the Forward Path]] — alternative-to (backfill only after the writer is fixed)
- [[SQL Schema Design and DDL]] — prerequisite-for (ON CONFLICT … DO UPDATE and `excluded`)
