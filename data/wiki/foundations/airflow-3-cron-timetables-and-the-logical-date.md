---
title: "Airflow 3 Cron Timetables and the Logical Date"
tags: [foundations, pattern]
summary: "From Airflow 3 a bare cron string means a trigger timetable whose logical date is the fire time, so ds names the day in progress; name CronDataIntervalTimetable to process the completed day."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--03-transform-and-orchestrate--notes--05-dagster-and-airflow.md
---

# Airflow 3 Cron Timetables and the Logical Date

The default changed silently between major versions. Through 2.x a cron string meant run at the end of each interval and call the run by the interval's start. In 3.0 `create_cron_data_intervals` is `False` by default, so cron means the trigger timetable: the logical date is the moment it fires.

| Timetable, cron `0 3 * * *` | Fires | Logical date |
|---|---|---|
| CronTriggerTimetable (3.x default) | 14 Jan 03:00 | 14 Jan 03:00 |
| CronDataIntervalTimetable | 15 Jan 03:00 | 14 Jan 03:00 |

Under the default, the run firing at 03:00 on the 14th has `ds` of the 14th, a day with three hours of trips in it. A task processing `ds` reprocesses an incomplete day every morning and never revisits it. With the interval timetable the same `ds` appears a day later, once the day is complete, matching what a partition-derived Dagster schedule does.

## Fixes
- Name the timetable explicitly with the interval class.
- Set the `create_cron_data_intervals` option back to true.
- Subtracting a day from `ds` works but hides the rule.

Inheriting a 2.x Dag with a bare cron string that reads `ds`: after upgrade it processes the 14th on the morning of the 14th, where 2.x processed the 13th. Asset-triggered runs have no logical date at all, so the tasks must derive the period from what they read.

## See Also
- [[Orchestrator Core Loop, Logical Dates and Retries]] — extends
- [[Dagster Assets vs Airflow Tasks]] — related
- [[Backfills, As-Of Dimensions and Past-Dependent Tables]] — related
