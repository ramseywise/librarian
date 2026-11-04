---
title: "Idempotent Backfills and Dated Corrections"
tags: [foundations, pattern]
summary: "A repair job that replaces one logical day per transaction is safe to run twice, corrections live in a dated table above untouched raw data, and a late partition needs a trigger: rebuild any mart row older than its input's newest load."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--05-quality-and-observability--notes--03-incident-playbooks.md
  - data/raw/repos/learn-ai-engineering/data-engineering--05-quality-and-observability--notes--02-monitors-and-lineage.md
---

# Idempotent Backfills and Dated Corrections

Under incident pressure jobs get run twice: a timeout leads to a rerun, or someone starts a second attempt unaware of the first. The first property of any repair job is **idempotence**: running it again leaves the same result.

## The failure and the fix

An appending load job doubles the mart on rerun, creating a second incident while repairing the first. In a synthetic example one day's revenue loaded once summed to 34,244 and loaded twice to 68,489. The fix is to replace one logical day inside a transaction, so a reader sees either the old day or the new one:

```sql
BEGIN;
DELETE FROM daily_revenue WHERE dt = :day;
INSERT INTO daily_revenue SELECT dt, sum(fare), count(*), :built_at FROM trips_clean WHERE dt = :day GROUP BY 1;
COMMIT;
```

In a warehouse use `MERGE`, partition overwrite or `INSERT OVERWRITE`. Without the transaction, a failure between the statements leaves the day missing entirely. Test idempotence by running the whole backfill twice: both gave 90 days and the same total, and a day duplicated at the source came back to half the raw figure (67116 raw, 33558 repaired). A mart reporting 90 of 91 days is the honest state while one day has not been re-exported. The same keying by logical date is why [[Same-Weekday Median and MAD Volume Monitor]] metrics replace rather than add.

## Fix forward in a layer you can read

Raw stays as it arrived. Corrections go in a view over it, driven by a small table of `valid_from`, column, factor and a ticket reference. Duplicates drop by key; a unit change is corrected from its effective date. That keeps the evidence, and makes the correction reviewable and reversible. Overlapping correction windows make the lookup ambiguous (an error, or stacked factors), so test the table like any other. Audit the layer that will be published, not raw, or the gate never releases a repaired day (see [[Write-Audit-Publish Gate]]).

## Late data needs its own trigger

A late partition exposes a subtle failure: the mart row for that day was built before the data existed, so the job ran green over nothing, and the arrival changes nothing downstream. The generic rule: **rebuild any mart row older than the newest load of its input**. Joining the load log to the mart's build time lists exactly the stale partitions; in the example one partition, loaded on 18 March, was newer than its mart row built on 16 March, and its rebuild gave 2940 rows. This is watermark thinking applied to batch, and it means load-based triggers rather than clock-based ones. The lineage-derived rebuild list ([[Lineage for Blast Radius and Rebuild Lists]]) supplies which marts to run.

## Pitfalls

- Never fill an unsent day with an average; mark it missing or label an estimate.
- Retrain only after the inputs are fixed, and only if the model trained on bad data.

## See Also
- [[Data Incident Playbook: Contain Before Diagnosing]] — prerequisite-for
- [[Freshness Alerts Need a Date Spine]] — related
- [[Rerunnable Cleaning Loader with Assertions]] — related
- [[Batched Rerunnable Data Backfills]] — related
