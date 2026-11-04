---
title: Pandas Copy-on-Write and Chained Assignment
tags: [foundations, concept]
summary: Since pandas 3.0 every indexing or method result behaves as a copy, so chained assignment does nothing and one .loc call is the only way to update part of a frame.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--01-python-for-data-analysis--notes--01-series-and-dataframe.md
  - data/raw/repos/learn-ai-engineering/data-analytics--01-python-for-data-analysis--notes--03-indexing-and-selection.md
---

# Pandas Copy-on-Write and Chained Assignment

## The rule

Pandas 3.0 adopted **Copy-on-Write**: the result of any indexing operation or method behaves as if it were a copy. Data is still not copied until it has to be, which is the name's origin, but this is invisible from outside. Consequence: one statement can never update more than one object.

Before 3.0, a column pulled out of a frame could be a view, so writing to it could change the frame, and `SettingWithCopyWarning` meant "pandas cannot tell whether this write reaches the original". Both the ambiguity and the warning are gone, and so is the need for defensive `.copy()` calls.

```python
col = orders["qty"]
col.iloc[0] = 99          # changes col only; orders is untouched
```

## Chained assignment is a no-op

Selecting and then assigning in two steps produces two objects, and the write lands on a temporary that is discarded:

```python
df["qty"][df["customer"] == "ana"] = 0      # does nothing, raises ChainedAssignmentError
df.loc[df["customer"] == "ana", "qty"] = 0  # works: selection and column in one call
```

The same holds for `df[mask]["a"] = 1`. **To change part of a frame, put the row selection and the column in a single `.loc`.** The one-call form also builds conditional columns, with `np.where` for two outcomes and `np.select` or `pd.cut` for more.

## Related edge

The array returned by `to_numpy()` may be a read-only view of the frame's data, and writing to it raises an error; copy it first. Old idioms from earlier books (`df["a"][mask] = x`, `df.ix[...]`) should be rewritten as `df.loc[mask, "a"] = x` or an `iloc` form.

## Check yourself

Given `s = pd.Series([1, 2], index=["a", "b"])`, `u = s[s > 1]`, then `u.iloc[0] = 50`: `s["b"]` is still 2, because `u` behaves as a copy.

## See Also
- [[Pandas Label Alignment and Dtypes]] — prerequisite-for
- [[Pandas loc, iloc and the Integer Index Trap]] — related
