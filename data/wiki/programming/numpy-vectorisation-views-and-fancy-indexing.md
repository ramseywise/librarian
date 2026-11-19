---
title: NumPy Vectorisation, Views and Fancy Indexing
tags: [programming, concept]
summary: NumPy replaces Python loops with whole-array operations, but slices are views while boolean and fancy indexing copy, and a few default behaviours (repeated indices, wrong-length masks, int truncation) fail without an error.
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-python-data-science-handbook-ch02-introduction-numpy.md
  - data/raw/papers/2026-11-08-python-for-data-analysis-ch04-numpy-basics-arrays-vectorized.md
---

# NumPy Vectorisation, Views and Fancy Indexing

An `ndarray` holds values of one fixed type, and a **ufunc** is a function that runs one operation over every element. **Vectorisation** means writing a batch operation with no `for` loop. VanderPlas (*Python Data Science Handbook*, ch2) and McKinney (*Python for Data Analysis*, 2nd ed., ch4) both teach the idioms below; pandas builds on them (see [[Pandas Label Alignment and Dtypes]]).

## Why loops lose

Setups are single `%timeit`/`%time` runs on the authors' own machines, with no hardware stated.

- McKinney: multiplying a 1,000,000-element integer array by 2, ten times, took 72.4 ms, against 1.05 s for the same work as a list comprehension. Drawing 1,000,000 normal samples took 61.7 ms with `np.random.normal` and 1.77 s with a comprehension over `random.normalvariate`. He states NumPy is generally 10 to 100 times faster and uses less memory (a claim, with no data beyond these runs).
- VanderPlas: a Python loop over the reciprocal of a million integers takes seconds and the vectorised form milliseconds. Python's `sum` over a million floats was about 235 times slower than `np.sum`, so use the NumPy aggregate on arrays (`min`, `max`, `any`, `all` likewise).
- The winner can flip with size. A hand-written `searchsorted` plus `np.add.at` binning beat `np.histogram` on 100 points, and `np.histogram` was about twice as fast on 1,000,000.

## Views, copies and silent failures

- **Slices are views.** After `arr_slice = arr[5:8]`, writing `arr_slice[1] = 12345` changes `arr`; use `.copy()` when the slice must not alias. Python list slices copy.
- **Boolean and fancy indexing return copies** (McKinney). Fancy indexing with two index arrays selects element pairs: on `np.arange(32).reshape(8, 4)`, indexing with `[1,5,7,2]` and `[0,3,1,2]` as the two arrays returns `[4, 23, 29, 10]`. For a rectangular block use `arr[[1,5,7,2]][:, [0,3,1,2]]`.
- **Repeated indices in `x[i] += 1` count once.** With `i = [2,3,3,4,4,4]` the entries at 3 and 4 each rise by 1; `np.add.at(x, i, 1)` applies every repeat (2 and 3).
- **Masks:** combine with `&`, `|`, `~` and parentheses, not `and`/`or`. A boolean mask of the wrong length does not raise (McKinney). `(arr > 0).sum()` counts matches because `True` is 1.
- **Defaults:** `np.empty` can return arbitrary leftover values, not zeros; assigning floats into an integer array truncates silently; `*` is element-wise and `@` or `np.dot` is the matrix product.
- `argmax` over booleans returns the first `True`, though it still reads the whole array. McKinney uses it for first-crossing times: of 5,000 simulated 1,000-step walks, 3,410 reached +-30, with mean first crossing at 498.89 steps (one unseeded run).

## Broadcasting and axes

Broadcasting applies a binary ufunc to arrays of different shape: prepend ones to the shorter shape, expand any size-1 dimension, and raise an error if sizes still disagree and neither is 1 (VanderPlas). `axis=` names the dimension that is collapsed, not the one returned.

## Other VanderPlas advice

`np.partition`/`argpartition` when only the k smallest are needed; `out=` to avoid temporaries; `np.expm1` and `np.log1p` for small inputs; seed the generator for reproducibility; for everyday mixed-type tables prefer pandas to structured arrays.

## Limits

- **Edition:** VanderPlas's chapter shows NumPy 1.11.1 and Python 3.4 (edition and year not printed; 2016 inferred); McKinney's is the 2nd edition. The extractions list what has since changed: aliases `np.float_`, `np.complex_`, `np.bool_` were removed in NumPy 2.0, `np.random.seed`/`RandomState` is superseded by `np.random.default_rng` (McKinney's own advice to use `RandomState` predates this), `np.in1d` is now `np.isin`, and array reprs and the default integer width differ by platform and version.
- Timings come from one machine, as best-of-3 `%timeit` or single runs, without variance or stated hardware.
- McKinney defers broadcasting, reshape and indirect sorts to an appendix. VanderPlas gives no guidance on memory layout, `einsum`, `matmul`, `np.where` or `np.unique`.
- VanderPlas's text has typos the extraction lists: Table 2-3 labels `np.mean` as median, Table 2-4 equates `np.dtype('f8')` with `np.int64`, and one rainfall output label says `< 0.1` where the test is `< 0.2`.

## See Also
- [[Pandas Label Alignment and Dtypes]] — extends
- [[Pandas loc, iloc and the Integer Index Trap]] — extends
- [[IPython Timing and Profiling Workflow]] — related (the `%timeit` method behind these timings)
- [[Python Data Model and Idioms]] — related (aliasing and mutability)
