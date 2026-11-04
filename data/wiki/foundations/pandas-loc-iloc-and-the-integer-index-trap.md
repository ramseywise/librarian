---
title: Pandas loc, iloc and the Integer Index Trap
tags: [foundations, concept]
summary: loc selects by label and iloc by position; they agree only until a filter or sort leaves gaps in the default integer labels, after which the same-looking code returns different rows.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--01-python-for-data-analysis--notes--03-indexing-and-selection.md
---

# Pandas loc, iloc and the Integer Index Trap

## Three selectors

- `df[...]`: a column name or list of names selects columns; a boolean Series filters rows. Use it for those two jobs only.
- `.loc[rows, cols]`: by **label**.
- `.iloc[rows, cols]`: by integer **position**.

## Slice ends differ

A position slice excludes its end, like all of Python: `iloc[0:2]` is two rows. A label slice includes its end, because labels have no natural "one past the last": `loc[0:2]` is three rows. The two look identical on a fresh frame because labels equal positions, which hides the difference.

## The integer index trap

Filtering keeps the original labels, so the labels of a filtered frame have gaps. On a frame filtered to four rows labelled 1, 3, 6, 9, `iloc[1]` returns the row labelled 3, and `loc[0]` raises `KeyError`. Sorting does the same: after sorting by revenue descending, `iloc[0]` is the top row while `loc[0]` is whichever row kept label 0. Remedies: `reset_index(drop=True)` before position work, or never let a default integer label mean anything.

On a Series in pandas 3, a bare integer in brackets always means a label (older versions fell back to position when the index held no integers). With a text index `s[0]` now raises `KeyError`; use `iloc[0]` for the first value.

## Boolean masks

Vectorised comparison produces a True/False array; indexing with it keeps the True positions. This replaces the loop-with-an-if.

- Combine with `&`, `|`, `~`, each condition in parentheses (these operators bind tighter than comparisons). `and`/`or` raise `ValueError: The truth value of a Series is ambiguous`.
- Helpers: `isin`, `between` (both ends included by default), `.str` methods, `query("region == 'north' and qty > 1")`, `nlargest`.
- A mask is also a number: `True` counts as 1, so `mask.sum()` is the match count and `mask.mean()` the share (5 of 11 orders, 0.455, in a worked example). Counting orders and revenue shares can disagree: one product was 0.364 of orders but 0.186 of revenue.

## Setting values

Put selection and column in one `.loc` (see [[Pandas Copy-on-Write and Chained Assignment]]). For a conditional new column: `np.where` for two outcomes, `np.select` or `pd.cut` for more.

## NumPy underneath

An array is same-typed values with a shape. Selection by position, slice, boolean mask or list of positions carries over to pandas. Axis 0 runs down the rows, axis 1 across the columns; `sum(axis=0)` collapses the rows and gives one value per column. An array has no idea that column 1 means a given product, which is the silent bug that labels fix.

## Pitfalls

- Treating labels as positions.
- Forgetting `.loc` slices are end-inclusive.
- `and`/`or` in a mask.
- Old `.ix` code: decide whether you meant label or position.

## See Also
- [[Pandas Copy-on-Write and Chained Assignment]] — related
- [[Pandas Index Design, MultiIndex and Reindex]] — extends
- [[Pandas Label Alignment and Dtypes]] — prerequisite-for
