---
title: Datetime Parsing, Frequency Aliases and Time Zones
tags: [foundations, reference]
summary: Parse dates with an explicit format, use the explicit pandas 3 frequency aliases, and store timestamps in UTC so ambiguous days, renamed aliases and daylight-saving hours do not corrupt results.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--01-python-for-data-analysis--notes--06-time-series.md
---

# Datetime Parsing, Frequency Aliases and Time Zones

## Parsing

A date in a CSV is text until converted. `pd.to_datetime` with an explicit `format` is faster and stops wrong guesses: the string `03/04/2025` parsed to 3 April with `%d/%m/%Y` and to 4 March with `%m/%d/%Y`. If a file mixes conventions no parser can save you; check `min` and `max` for implausible values. `errors="coerce"` yields `NaT` ("not a time"); count what it produces.

The `.dt` accessor gives calendar parts (`day_name()`, `to_period("M")`) and `diff()` on a datetime column gives a timedelta (`.dt.days`).

**Unit change in 3.0:** parsed datetimes are `datetime64[us]` (microseconds); older versions defaulted to nanoseconds. Converting to integer now gives a number 1000 times smaller than old code expects (1735862400000000 against 1735862400000000000 for the same date). Use `dt.as_unit("ns")` first if you depend on the unit.

## Frequency aliases

Pandas 3.0 removed `M`, `Q`, `Y` (and `A`) and uppercase `H`, `T`, `S`. `freq="M"` now raises `ValueError: Invalid frequency`. The explicit names remove an ambiguity: month **end** versus month **start**.

| Alias | Meaning | Old |
|---|---|---|
| `D` / `B` | calendar / business day | same |
| `W-SUN` | weekly, ending Sunday | same |
| `MS` / `ME` | month start / end | `MS` / `M` |
| `QE` | quarter end | `Q` |
| `YE` | year end | `A`, `Y` |
| `h`, `min`, `s` | hour, minute, second | `H`, `T`, `S` |

Related removals: `resample(rule, how="mean")` is `resample(rule).mean()`, and a period `freq="A-DEC"` is `"Y-DEC"`.

## Time zones

A timestamp with no zone is naive. For stored data, keep UTC and convert only for display. `tz_localize` declares the zone of a naive timestamp; `tz_convert` changes the zone of an aware one.

- The zone changes which day a sale belongs to: 22:00 UTC on 31 March is already 1 April in Europe/Oslo, so daily or monthly totals by local date differ from totals by UTC date. Choose the reporting zone before resampling.
- Daylight saving makes local days irregular: on the spring-forward day the local day lasted 23 hours, another reason to do arithmetic in UTC.

## Pitfalls

- Dates left as text sort alphabetically and do not resample.
- Ambiguous day/month without `format=`.
- Local-time arithmetic across daylight-saving changes.

## See Also
- [[Time-Series Resampling, Bins and Gaps]] — extends
- [[Time-Series Leakage: Shift and Rolling Windows]] — related
- [[Rerunnable Cleaning Loader with Assertions]] — related
