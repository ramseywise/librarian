---
title: Multi-Level Implementation Round
tags: [interview, pattern]
summary: "A coding-round format where one problem is revealed in 2–3 levels over 45–90 minutes and each level extends the last; the grade is mostly whether the level-1 data shape absorbs later levels without a rewrite — so design the seam (a record, not a bare value; event time, not wall clock) before it is asked for."
updated: 2026-10-30
sources:
  - data/raw/repos/sisyphus/interviewing--rounds--coding-challenge--questions.md
  - data/raw/repos/sisyphus/interviewing--rounds--coding-challenge--README.md
---

# Multi-Level Implementation Round

A variant of the live coding round reported at frontier AI labs: one problem, revealed in
levels over 45–90 minutes (e.g. SET/GET/DELETE → TTL → persistence). Each level extends the
previous one, and the candidate does not see level 2 until level 1 works. The grade is
mostly **whether the level-1 design absorbs levels 2 and 3 without a rewrite** — which makes
it a design round disguised as a coding round. It sits alongside the formats in
[[Coding Challenge Interview Study Guide]].

## The mechanism: build the seam before the requirement

Level 1 is always easy enough to solve with the naive shape (a dict of bare values, a flat
balance, a list of rows). That shape is what level 2 punishes. The strong move is to pick
the data shape the *likely* next levels need, say why out loud, and keep the level-1 code
thin over it. Clarify concurrency and durability requirements before typing — they decide
which seams matter.

## The four reported problems

| Problem | Level-1 seam that pays off | Named trade-off to say aloud | Typical rewrite trap |
|---|---|---|---|
| **Key-value store** (CRUD → TTL → persistence) | Store a record `{value, expires_at}`, not the bare value | Lazy expiry on read vs active sweep (heap keyed by expiry): memory vs work. WAL replay vs periodic snapshot: durability vs recovery time — real systems combine them | Raw values, so every method is rewritten at TTL; a timer thread as the only expiry; expiry timestamps lost on restart (drop already-expired keys on load) |
| **In-memory SQL-like DB** (insert/select/delete/export → WHERE) | Rows in a dict keyed by id with a per-table monotonic counter | Full scan first, then a secondary index (value → set of ids) — and its consistency obligation on every write path | A list where `del` shifts later ids; reusing freed ids; an index that delete forgets to update; hand-rolled CSV quoting |
| **Credits with expiry** (grant/charge → expiry → out-of-order events) | Each grant is a lot `{remaining, expires_at}` in a min-heap by expiry | Spend soonest-to-expire first (the greedy that wastes least credit); event time drives expiry, never `time.time()`; state as a pure function of timestamped events (buffer-sort-replay or re-derive from the earliest affected timestamp) | A flat balance; a background expiry thread; applying events in arrival order so a late grant can't fund an earlier charge; floats for money |
| **Web crawler** (single-threaded → politeness → concurrent) | Frontier queue + visited set, with URL normalization (resolve relative, strip fragment) *before* dedup | Per-host rate limit honoring `Retry-After` with jittered backoff; I/O-bound so asyncio or a thread pool | A global sleep as "rate limiting"; ending when the queue is momentarily empty while workers are still fetching (count in-flight work); check-then-add race on visited |

## Signals graders look for

- The level-1 record shape appears *before* the level that needs it, with a one-line reason.
- Trade-offs are named by their standard names (lazy vs active expiry, WAL vs snapshot,
  event time vs wall clock) rather than improvised.
- Ambiguous business rules are surfaced as questions, not silently decided — e.g. what an
  unfunded charge does (fail, defer, go negative), idempotency keys for retried events.
- For the concurrent level, a termination condition that does not rely on an empty queue alone.

## See Also
- [[Coding Challenge Interview Study Guide]] — instance-of (one format of the live coding round)
- [[AI Role Interview Loop Map]] — extends (where the coding round sits in each loop)
- [[Polite Crawler Robots Compliance]] — extends (the politeness level in production form)
- [[Timebox-Scaled Deliverable Bar]] — alternative-to (async take-home bar vs a staged live build)
