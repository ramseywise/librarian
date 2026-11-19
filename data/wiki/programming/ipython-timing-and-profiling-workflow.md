---
title: IPython Timing and Profiling Workflow
tags: [programming, concept]
summary: IPython's magics measure speed in a fixed order (timeit, then prun, lprun, memit, mprun), and %timeit misleads on in-place operations such as sorting because repeated runs act on already-changed data.
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-python-data-science-handbook-ch01-ipython-beyond-normal-python.md
  - data/raw/papers/2026-11-08-python-for-data-analysis-ch02-python-language-basics-ipython-jupyter-notebooks.md
  - data/raw/papers/2026-11-08-python-for-data-analysis-ch01-preliminaries.md
---

# IPython Timing and Profiling Workflow

A **line magic** starts with one `%` and takes one line; a **cell magic** starts with `%%` and takes the whole cell. VanderPlas (*Python Data Science Handbook*, ch1) tours the IPython features that speed up exploratory work, and McKinney (*Python for Data Analysis*, 2nd ed., ch1 and ch2) covers the same shell and Jupyter basics. The timings below are worked examples on the authors' own laptops with the hardware unstated.

## Measure in order

VanderPlas advises profiling in this order and not optimising early: `%timeit`, then `%prun`, then `%lprun`, then `%memit` and `%mprun`.

| Magic | Answers | Worked result (his `sum_of_lists` example) |
|---|---|---|
| `%timeit` | how long a short statement takes | a list comprehension squaring `range(1000)` ran roughly a tenth faster than the matching for loop (373 µs) |
| `%prun` | which function calls take the time | `sum_of_lists(1000000)`: 14 calls in 0.714 s, 0.599 s of it in the list comprehension |
| `%lprun` | which line takes the time | `sum_of_lists(5000)`: 95.9% on the comprehension line (9001 of 9382 µs) |
| `%memit` | peak memory | peak of 100.08 MiB when calling `sum_of_lists(1000000)` |
| `%mprun` | memory added line by line | building the list `L` adds about 25 MiB |

`%lprun` needs the third-party `line_profiler`, and `%memit` and `%mprun` need `memory_profiler`. `%mprun` works only on functions defined in a separate module, not in the notebook itself.

## When `%timeit` lies

`%timeit` repeats the statement, so an in-place `L.sort()` runs again on already sorted data. On 100,000 random floats, `%time L.sort()` took 41.5 ms once, a second `%time` on the sorted list took 8.24 ms, and `%timeit` reported 1.9 ms. Use `%time` when repetition changes the input.

## Smaller habits

- `?` shows docs, `??` the source, Tab explores, and `*` wildcards find names (`str.*find*?`). McKinney gives the same introspection tools.
- `%run` runs a script and leaves its functions defined; McKinney adds `%run -i` to give the script the interactive namespace. `%paste` and `%cpaste` accept code copied with prompt markers.
- A trailing semicolon suppresses output and keeps it out of `Out`.
- After an exception, `%debug` opens the debugger on it; `%pdb on` does so automatically, and `%xmode Plain/Context/Verbose` sets traceback detail.
- `!cd` runs in a temporary subshell and changes nothing, so use `%cd`.
- Plots: `%matplotlib` in the IPython shell, `%matplotlib inline` in Jupyter, or they do not show or block the session.
- McKinney's import conventions are `np`, `plt`, `pd`, `sns`, `sm`, and never `from numpy import *`.

## Limits

- Version-dated: IPython 4.0.1 (VanderPlas, 2015-2016, Python 2/3 transitional) and IPython 5.1.0 on Python 3.6 (McKinney, 2017). Modern `%timeit` prints mean and standard deviation over several runs, not "best of 3", and current tooling is JupyterLab or Notebook 7.
- The numbers come from one unspecified machine each and illustrate method, not benchmarks.
- Windows shell commands may fail; shell shortcuts depend on GNU Readline and differ by system. The 399 importable modules in VanderPlas's tab-completion example vary per install.
- McKinney's chapter 2 omits classes, Jupyter keyboard shortcuts and remote deployment, and prints one curly-quote typo that is a syntax error as written.

## See Also
- [[NumPy Vectorisation, Views and Fancy Indexing]] — related (timings taken with these magics)
- [[Python Foundations Reference]] — related
- [[Profile Then Select]] — related (a different use of "profile first")
