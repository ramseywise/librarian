---
title: Deadline Transition Computed on Read
tags: [infra, pattern]
summary: With no scheduler, a time-triggered state change (a poll closing at its deadline) is derived by every read path from one shared predicate and persisted opportunistically on the next write, so correctness never depends on a job firing at the deadline instant. The companion decision is that a "swappable store" seam means interface versus direct DB calls, not in-memory versus database, because in-memory state fails a two-device acceptance test.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-b42-poll-surfaces.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-b42-poll-surfaces.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-b42-poll-surfaces.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-b42-poll-surfaces.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-b42-poll-surfaces.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-b42-poll-surfaces.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-b42-poll-surfaces.md
---

# Deadline Transition Computed on Read

## Context

An account-free group poll (repo akira) needed polls to close automatically at an optional
deadline. The repo had no cron, no queue and no background job infrastructure. Building a
scheduler for one demo-scoped feature was the expensive option.

## Mechanism

- **The stored status is a hint, not the truth.** A poll whose `deadline` has passed is
  `closed` on every read path (vote, summary), even if its stored `status` still says
  `open`. The store's `getPoll` normalises this on every call.
- **Convergence is opportunistic.** A manual "close voting", or a vote submitted after the
  deadline, also persists the transition, so the stored value catches up eventually.
  Nothing depends on a write happening *at* the deadline.
- **One predicate, used everywhere.** The plan's own risk table named the failure: "is the
  deadline passed" is computed in two places (read normalisation and the vote-submit
  guard). If they drift, a poll accepts votes past its deadline on one path and not the
  other. The fix is a single `isPollOpen(poll, now)` helper, tested once. The clock is
  passed in, so the test is deterministic.
- **Transitions are enforced in the store, not the UI.** Closing an already-confirmed poll
  is an error, not a silent overwrite. The UI-only state (`draft`, before the create form
  is submitted) is never persisted, so the state machine's persisted states start at
  `open`.

The same applies to any time-triggered state: expiries, trial ends, embargo lifts. If no
job runner exists, derive the state from `(stored fields, now)` on read and let writes
converge the stored value. Add a scheduler only when something *outside* the read path,
such as a notification, has to happen at the instant.

## Companion decision: what the store seam is for

The brief asked for a "swappable store" and leaned toward in-memory for a demo. The plan
rejected in-memory on the acceptance test itself. The phase gate was "a shared link lets a
**second phone** vote". Module state in a serverless route handler is not guaranteed to
survive between invocations, and even dev-server hot reload resets it. So in-memory
satisfies only "two requests in the same warm process, if you're lucky".

The seam that matters is **a store interface versus routes calling the database
directly**. It mirrors the existing candidate-source swap point. A later schema rework
changes the implementation behind `getPollStore()`, and no route or component notices.
The database was already the persistence layer for every other write, so three tables cost
nothing extra.

## Related rules from the same plan

- **New product logic missing from the design is written down as an assumption.** The
  designs showed "Plan A / Plan B" ranked panels without a formula. The plan fixed
  `score = (2·yes + 1·maybe) / total_voters`. Dividing by *all* voters, not by those who
  answered that option, makes "unanswered" and "No" contribute equally. The formula is
  monotonic (an extra Yes can never lower a rank), unlike a naive yes-minus-no rule. It has
  a deterministic tie-break, and with zero votes it falls back to creation order and
  suppresses the "strongest option" sentence. All of this was flagged for sign-off rather
  than buried in code.
- **"N people voted" is `COUNT(DISTINCT participant)`**, and only submitted ballots are
  persisted, so half-filled forms are invisible to the count by construction.

## See Also
- [[State Writer Never Owns Its Side Effects]] — related (another way to keep time-driven side effects out of the state store)
- [[Realtime Is UI Sync, Not the Event Bus]] — related (this poll deliberately shipped with refetch-on-navigation and no live subscription)
- [[Capability Token in a Serialized Row]] — related (the security defect a review later found in the same poll surfaces)
- [[Fallback Mistaken for the Design]] — related (here the fallback-looking choice *is* the design, chosen on purpose)
- [[Dated Node Must Name the Row]] — related (one expiry predicate shared by the hard filter, a sweep and a notebook mirror)
