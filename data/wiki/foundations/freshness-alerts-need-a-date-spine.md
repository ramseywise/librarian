---
title: "Freshness Alerts Need a Date Spine"
tags: [foundations, pattern]
summary: "An age check on max(loaded_at) clears the moment a newer partition lands, with the hole still behind it; pairing it with a list of expected dates keeps firing until the gap is repaired."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--05-quality-and-observability--notes--02-monitors-and-lineage.md
  - data/raw/repos/learn-ai-engineering/data-engineering--05-quality-and-observability--notes--03-incident-playbooks.md
---

# Freshness Alerts Need a Date Spine

The usual freshness check compares the newest load time with the clock: if data is promised by 02:00 with a margin, anything older than 26 hours is stale. dbt's `source freshness` is this check, with `warn_after` and `error_after` tiers against a `loaded_at_field` (warning opens a ticket, error pages).

## The blind spot

In a synthetic feed, a day's partition failed to land on 10 March. The age check fired on 11 March, then dropped to 4 hours on 12 March when the next partition arrived, and cleared while the data was still missing. A late partition behaved the same way: the alert fired on 16 March and cleared on 17 March, a day before the data appeared.

`max(loaded_at)` measures whether the feed is alive. A **date spine**, the list of dates that should exist, measures whether it is complete. The first catches a stopped feed in hours; the second keeps firing until someone repairs the hole. Run both, and keep the spine check on until the repair. See [[SQL Date Spine and Window Frames]] for building the spine in SQL.

## Same blind spot in tests

A row-level test that loops over the partitions present never visits the missing one; testing for absence needs the expected dates from outside the data.

## Late arrivals downstream

A mart row built before its late input landed ran green over nothing. The trigger rule: rebuild any mart row whose build time is older than the newest load of its input (see [[Idempotent Backfills and Dated Corrections]]).

## See Also
- [[Data Quality Dimensions and Tests as Failing-Row Queries]] — prerequisite-for
- [[Same-Weekday Median and MAD Volume Monitor]] — related
- [[Data Incident Playbook: Contain Before Diagnosing]] — related
