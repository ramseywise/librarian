---
title: Trend on Occurrence Date, Not Run Date
tags: [eval, infra, pattern]
summary: Bucket recurring findings by when the cited code was last touched, not by when the review run fired — bursty run dates make every group look "rising" and the trend flag carries no information.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/skills/meta-retro/SKILL.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-12-dashboard-time-buckets.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-08-12-dashboard-time-buckets.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-14-gua-109-occurrence-date.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-08-14-gua-109-occurrence-date.md
---

# Trend on Occurrence Date, Not Run Date

A recurrence report that groups findings by signature and labels each group
`rising` / `falling` / `flat` is only as good as the date axis under it. guacamayo's
tooling retro learned that the obvious axis — the date the review run produced the row —
is wrong.

## The failure

Review sweeps are bursty. In one window **85 of 125 finding rows shared a single run
date**, so every promotable group bucketed into the same recent day and read as
`rising`. A flag that is always true carries no information; the retro had to caveat
"rising" as noise.

## The fix

Each finding carries `occurred`: the **occurrence date — when the cited code was last
touched** — and recurrence buckets on that instead. With it, the trend states become
evidence and drive different actions:

| Trend | Reading | Action |
|---|---|---|
| rising | getting worse now | candidate finding automatically; if not yet promotable, a *cheaper* intervention (warn-hook, not rule) with a shorter metric window |
| falling | being fixed | say so — don't re-propose last window's hook |
| flat + promotable | plateaued | real count, nothing moving |

Rows whose `occurred_source` is `run` had no resolvable checkout and fell back to run
date; they are treated as **undated** for trend purposes rather than silently mixed in.

## Neighbouring rules from the same source

- **Read the durable sink, not the rotating log.** A pass log that rotates on ~5 days
  silently undercounts anything older; the findings JSONL and factstore are the durable
  sinks. Repointing the source at a rotating log reintroduces the bug.
- **A high `unmatched:<category>:<repo>` count is a finding about the signature table,**
  not a promotable friction — the pattern table lacks a signature for that cluster.

## The trend rule as implemented (dashboard time buckets)

- **Rising**: the most recent *complete* period is more than 1.5× the mean of the prior 3
  periods **and** the recent count is ≥3. **Falling**: recent is below prior-mean / 1.5 and
  the prior mean is ≥3. Otherwise flat. The partial trailing period is excluded.
- **Anchor "recent" to today, not to the latest period with data.** The first version used
  the last observed period. Every dead signature then read as *rising* at its final burst,
  because its last non-empty period was its peak. The test
  `test_stopped_signature_is_not_rising` caught it. Inject `today` so these tests stay
  deterministic.
- **One matcher for count and trend.** Both go through one shared key-matching function, so
  the headline count and the trend arrow cannot disagree about which findings belong to a
  signature.
- **Validate the period argument once, before the loop.** Otherwise a caller's typo is
  swallowed as N unparseable dates instead of raising.

## Backfilling occurrence dates without breaking identity (GUA-109)

- **Add a field; don't mutate `date`.** The finding uid hashes `id|date|repo|file|title`, so
  rewriting `date` would orphan every existing store row. Add `occurred` plus
  `occurred_source` alongside it instead.
- **Fallback ladder:** blame the cited line, then the HEAD commit date for the file, then the
  run date. `occurred` is therefore a *last-touch* date, not an introduction date.
- **Gotcha:** `git log -L` exits 0 with empty output for a path outside the index. Check
  stdout as well as the return code.
- **Backfill hygiene:** dry-run by default, idempotent, `.bak` written first, atomic
  `os.replace`.
- **Measured effect:** the largest single-day share fell from 68% to 25%, distinct dates
  rose from 5 to 22, and blame resolved 110 of 125 rows.
- **Lock it in:** the test that asserted the defect was replaced by a test of the opposite
  property: no day above 50% of rows, and at least 6 ISO weeks covered. A future bulk sweep
  that re-concentrates dates then fails loudly.

## See Also
- [[Cross-Sweep Finding Fingerprint]] — extends (the identity key that trend states hang off)
- [[Friction Promotion Ladder]] — prerequisite-for (rising-but-not-promotable gets the cheaper rung)
- [[Silence Reads as Clean]] — extends (a rotating log's missing rows read as zero)
- [[Unit Tests Encode the Checker's Assumption]] — extends (pin the run-date defect, then invert it into a time-diversity test)
