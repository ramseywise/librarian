---
title: "Time-Series Leakage: Shift and Rolling Windows"
tags: [foundations, pattern]
summary: shift and rolling windows build comparisons and features from the past, but a negative shift or a centred window reads the future and leaks, and count-based windows misbehave on irregular rows.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--01-python-for-data-analysis--notes--06-time-series.md
---

# Time-Series Leakage: Shift and Rolling Windows

## shift and seasonal comparison

`shift(1)` slides values along the index so each row sees the previous one; it underlies every comparison to an earlier period. A daily percentage change on data with a weekly cycle mostly measures the cycle. Shifting by 7 compares like weekdays: mean absolute change fell from 0.13 day over day to 0.091 week over week, leaving mostly noise.

## Leakage

`shift(-1)` puts tomorrow's value on today's row. As an input to predict today it looks brilliant in testing and is impossible in production. Rule: **features look backward, positive shifts only**. The general taxonomy is in [[Tabular ML Leakage Taxonomy]], and window timing in [[Label Horizon vs Sampling Window]].

## Rolling windows

Split-apply-combine assumes independent pieces; rolling windows overlap, so they need their own tools.

- `rolling(7)` counts rows and, by default, requires all seven non-missing; `min_periods` relaxes it.
- `rolling("7D")` covers seven calendar days. With absent rows a count window reaches further back than it seems (nine days on one date in the example), so prefer the time-based form on irregular data.
- A 7-day mean removes a weekly pattern because each window holds one of every weekday.
- `expanding()` uses everything so far (running mean).
- `ewm(span=7)` weights recent values more, decaying exponentially, so it responds faster and has no hard edge.
- `rolling(...).corr(other)` gives rolling correlation; rolling std gives a volatility view.

### Trailing versus centred

The default window is trailing: a value uses that date and earlier ones, so it could have been known then. `center=True` removes the lag and looks nicer on a chart but uses future values. With a December bump starting on the 1st, on 29 November the centred mean was 614 against a trailing 565: it rose days before the jump by reading ahead, while the trailing line reacted only after. Acceptable for a chart, cheating for a forecast. Backward filling also leaks.

## See Also
- [[Time-Series Resampling, Bins and Gaps]] — prerequisite-for
- [[Tabular ML Leakage Taxonomy]] — related
- [[Label Horizon vs Sampling Window]] — related
- [[Datetime Parsing, Frequency Aliases and Time Zones]] — related
