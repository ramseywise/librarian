---
title: Dropped Filter Flips the Truncation Direction
tags: [patterns, foundations, pattern]
summary: "Moving a filter from SQL into application code while keeping `ORDER BY x ASC LIMIT n` changes which rows a full pool drops — before, the filter removed past rows and the cap cut the far-future tail; after, past rows sort first and the cap keeps stale rows and drops the near-term ones — so a cap-hit log that used to mean 'thinning' now means 'results go empty'."
updated: 2026-10-30
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-05-dis156-candidate-pool-truncation.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-05-dis156-candidate-pool-truncation.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-05-dis156-candidate-pool-truncation.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-05-dis156-candidate-pool-truncation.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-05-dis156-candidate-pool-truncation.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-05-dis156-candidate-pool-truncation.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-05-dis156-candidate-pool-truncation.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-10-dis73-occurrence-read-path.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-10-dis73-occurrence-read-path.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-10-dis73-occurrence-read-path.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-10-dis73-occurrence-read-path.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-10-dis73-occurrence-read-path.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-10-dis73-occurrence-read-path.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-10-dis73-occurrence-read-path.md
---

# Dropped Filter Flips the Truncation Direction

## The mechanism

A recommendation candidate loader (repo akira, 2026-09) queried events with an SQL
expiry filter (`end_at >= now OR (end_at IS NULL AND start_at >= now)`), then
`ORDER BY start_at ASC LIMIT 1000`. The expiry rule had to become occurrence-aware: an
event's collapsed `start_at` can be months stale while it still has a future occurrence.
That logic can't be expressed in the SQL predicate, so the fix moved expiry into memory
and dropped the SQL filter.

The sort and the cap stayed the same, and the meaning of the cap changed:

| | Rows reaching the LIMIT | What a full pool drops |
|---|---|---|
| SQL filter present | future rows only | the furthest-future tail (harmless) |
| SQL filter removed | past and future, past sorted first | **near-term future rows**, while keeping already-expired ones |

The catalogue held 346 already-past events, so once the unfiltered count passed the cap,
the in-memory expiry check would throw away the stale rows that had filled the pool. The
user would see recommendations go empty, not just get thinner.

## What the plan did with it

- **Did not build the join-based alternative yet.** At ~486 rows against a 1,000 cap the
  risk was bounded.
- **Used the existing instrument as the trigger instead of inventing a row count.** The
  loader already logged `candidate pool hit MAX_POOL` when it returned exactly the cap.
  That log firing once in production became the condition to revisit. It replaced a bare
  "revisit past ~5k events" guess in the data-model doc's open-decision entry.
- **Recorded that the log's severity had changed.** The message said "may be truncated".
  After the change it meant "may be serving stale rows instead of tomorrow's".

## Prequel: the unordered LIMIT that was correct by accident

Five days earlier the same loader had a different cap bug. It ran `LIMIT 1000` with **no
`ORDER BY`** and applied every eligibility filter in memory *after* truncation. With 476 rows
it was correct by accident — the cap never bound — but 346 of those rows were already expired,
so once the table outgrew the cap, the database would have returned an arbitrary 1,000 and the
in-memory filters would have thinned that arbitrary slice. The fix (the state this page starts
from):

- **Push eligibility predicates into SQL** so the cap applies to eligible rows only.
- **Order deterministically** — `start_at` then `id` as a tiebreak — so that when the cap binds
  it drops the furthest-future rows, never a random subset.
- **Log at error level when the cap binds** (result length equals `MAX_POOL`) — the instrument
  later reused as the revisit trigger above.
- **Note that exclusion counters go quiet.** Per-reason "excluded N expired" counts drop to zero
  once SQL filters those rows; that silence is expected, not a sign the filter broke.

A related retention-sweep issue was deferred with its revisit trigger rewritten, not closed
(see [[Named-Trigger Deferral]]). The lesson pair: a `LIMIT` without `ORDER BY` is a latent
nondeterminism bug, and a `LIMIT` *with* one encodes a policy about which rows to lose — both
need re-reading whenever the filters around them move.

## The general check

Whenever a filter moves from the query to the caller, re-read every `ORDER BY` / `LIMIT`
/ pagination clause on that query. Ask what the cap drops **after** the move. A filter that
ran before a limit was also deciding which rows the limit dropped. Taking it out silently
hands that decision to the sort order.

## See Also
- [[Event–Occurrence Split, Added Behind the Old Column]] — extends (the read-path follow-through where this was found)
- [[Named-Trigger Deferral]] — instance-of (an existing log line used as the revisit trigger)
- [[A Capped Run Is Not a Clean Run]] — related (a cap that binds changes what the output means)
- [[SQL Query Fundamentals]] — prerequisite-for (ORDER BY … LIMIT semantics and keyset paging)
- [[SQL from Python]] — related (dividing filter work between SQL and Python)
