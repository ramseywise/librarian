---
title: Tidy Data and Long-Wide Reshaping
tags: [foundations, concept]
summary: Ask what one row means; tidy data puts each variable in a column and each observation in a row, and melt, pivot, stack and unstack move between long and wide layouts.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--01-python-for-data-analysis--notes--04-reshaping-and-joins.md
---

# Tidy Data and Long-Wide Reshaping

## Tidy data

Every value belongs to a **variable** (one attribute across units) and an **observation** (all measurements on one unit). A dataset is tidy when:

1. each variable is a column,
2. each observation is a row,
3. each type of observational unit is a table.

Rule 3 is close to database normalisation: keep customers apart from orders so each fact lives once. The catch is that analysis tools mostly want one table, so analysis re-merges (see [[Pandas Merge Validation and Many-to-Many Blow-up]]). Ask "what does one row of this table mean?" before and after every operation.

## Long and wide

The same information in two layouts: wide has a column per week; long has one row per (product, week) with `week` and `units` as columns. In wide form `w1`, `w2`, `w3` are values of `week` sitting in the header, the first messy-data problem. Wide suits reading and matrix arithmetic, and can store a crossed design compactly; long suits `groupby`, plotting and modelling (plotting libraries that map columns to roles need it, see [[Matplotlib Figures, Axes and Seaborn Levels]]).

- **`melt`**: wide to long (`id_vars` kept, other columns become a variable/value pair).
- **`pivot`**: long to wide (pick row column, header column, value column). Each row/column combination must occur once; duplicates raise `ValueError: Index contains duplicate entries, cannot reshape`. `pivot_table` handles duplicates by aggregating (see [[Groupby Silent Group Loss and Pivot Defaults]]).
- Two variables in one header (`north_w1`): melt, then `str.split("_", expand=True)` into two columns.

## stack and unstack

The same job on index levels, usually right after a multi-key groupby. `unstack` moves a level into the columns, and missing combinations become `NaN`; `stack` reverses it. `unstack(fill_value=0)` is correct only when a missing combination means none sold; otherwise leave the gap. Round trip check: a customer-by-product table melted back to long form kept the same total (23 units).

## Pitfalls

- Summing a wide table's columns as if comparable; a table already aggregated can be double-counted.
- `pivot` on repeated combinations.

## See Also
- [[Pandas Merge Validation and Many-to-Many Blow-up]] — related
- [[Groupby Split-Apply-Combine and Result Shapes]] — related
- [[Pandas Index Design, MultiIndex and Reindex]] — related
