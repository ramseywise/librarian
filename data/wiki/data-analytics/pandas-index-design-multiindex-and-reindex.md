---
title: Pandas Index Design, MultiIndex and Reindex
tags: [data-analytics, python-for-data-analysis, reference]
summary: Making a real key the index turns lookups into plain label access, but non-unique indexes change the return type and MultiIndex slicing needs sorting; reindex fixes the row list of a report.
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--01-python-for-data-analysis--notes--03-indexing-and-selection.md
  - data/raw/papers/2026-11-08-python-for-data-analysis-ch08-data-wrangling-join-combine-reshape.md
  - data/raw/papers/2026-11-08-python-data-science-handbook-ch03-data-manipulation-pandas.md
---

# Pandas Index Design, MultiIndex and Reindex

## Choosing an index

When a column identifies rows, `set_index` makes lookups read as what they are (`by_id.loc[1007, "customer"]`); `reset_index` moves the index back to a column. The default integer index carries no meaning (see [[Pandas loc, iloc and the Integer Index Trap]]).

## Non-unique indexes change the return type

An index need not be unique. With a customer index where one customer has two rows, `loc["ana"]` returns a DataFrame of shape (2, 8) while a customer with one row returns a Series of shape (8,). Passing a one-element list always returns a DataFrame. Check `index.is_unique` or pass a list.

## reindex: conform to a fixed list of labels

`reindex` conforms an object to the labels you give, inserting `NaN` (or `fill_value`) for new labels and dropping others. Use it when a report needs every category listed in a fixed order, including one with no activity this period: `sold.reindex([...], fill_value=0)`. Zero is right only when a missing label means none; see [[Pandas Missing Data Decisions]].

## MultiIndex

Grouping by two keys yields an index with two levels, a way to hold higher-dimensional data in lower-dimensional form (see [[Groupby Split-Apply-Combine and Result Shapes]]).

- Exact combination: `s.loc[("south", "filter")]`.
- Everything under an outer level: `s.loc["north"]`.
- Cut across an inner level: `s.xs("filter", level="product")`.
- Slicing needs a sorted MultiIndex: a groupby result already is; otherwise `sort_index()`.
- `reset_index()` flattens levels back to ordinary columns, which many analysts do on purpose; `unstack` moves a level into columns (see [[Tidy Data and Long-Wide Reshaping]]).

## What the books add

- McKinney says lookups on a MultiIndex run far faster once it is sorted lexicographically starting at the outer level (`sort_index(level=0)`); VanderPlas adds that partial slicing on an unsorted MultiIndex raises a lexsort-depth `KeyError`.
- VanderPlas uses `pd.IndexSlice` for slices inside a MultiIndex `.loc` tuple, for example `health_data.loc[idx[:, 1], idx[:, 'HR']]`, and advises a MultiIndex over tuple keys.
- `stack` discards missing cells by default, which keeps it the inverse of `unstack`; `dropna=False` keeps it (McKinney, ch8). `swaplevel`, level-wise statistics and `set_index`/`reset_index` are in the same chapter.

## Limits

- Edition: McKinney's ch8 code uses `MultiIndex` `labels=`, `sum(level=)` and `join_axes=`, and VanderPlas's ch3 is pinned to pandas 0.18.1; the extractions list `labels` (now `codes`), `sortlevel`, `mean(level=)` and `join_axes` as removed or changed.
- McKinney's ch8 repeats `data2.unstack()` where the sentence before it describes `stack`, and one of his example frames lists Ohio 2000 twice.
- The examples are small toy frames, and the sort-speed remark has no measurement.

## See Also
- [[Pandas loc, iloc and the Integer Index Trap]] — prerequisite-for
- [[Groupby Split-Apply-Combine and Result Shapes]] — related
- [[Tidy Data and Long-Wide Reshaping]] — related
