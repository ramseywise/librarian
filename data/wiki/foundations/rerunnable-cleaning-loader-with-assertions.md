---
title: Rerunnable Cleaning Loader with Assertions
tags: [foundations, pattern]
summary: Keep the raw file untouched and put every cleaning step in one function that asserts what must be true and prints row counts, so the next export runs through the same checks.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--01-python-for-data-analysis--notes--02-loading-and-cleaning.md
---

# Rerunnable Cleaning Loader with Assertions

Cleaning is not a one-off first step: new problems surface and the same data gets cleaned again. So cleaning should be a script, not a set of hand edits.

## Shape of the loader

1. Read the raw text first (`open`, `pathlib`) and pass `encoding` explicitly; the default differs across systems.
2. `read_csv` with stated options, never the naive call. A banner line became the header and collapsed a 7-column file to one column; `comment="#"` fixed it. Checking `shape` exposes this.
3. Chain steps in reading order with `assign`: drop duplicates, normalise text, convert types.
4. Assert invariants, then print the row count lost.

```python
def load_orders(path):
    df = pd.read_csv(path, comment="#", na_values={"region": ["-"]}, parse_dates=["date"])
    n_raw = len(df)
    df = df.drop_duplicates(subset="order_id").assign(
        product=lambda d: d["product"].str.strip().str.lower(), ...)
    df = df[df["qty"] > 0].reset_index(drop=True)
    assert df["order_id"].is_unique and df["unit_price"].notna().all()
    print(f"loaded {n_raw} rows, kept {len(df)}")
    return df
```

In the worked example, 13 raw rows became 11 with every removal accounted for.

## read_csv options that matter

- `dtype={"zip": "str"}`: stops `01234` becoming 1234; use for any identifier with leading zeros.
- `usecols`, `nrows`: peek at a large file. `chunksize`: iterate frames for a file larger than memory.
- `na_values`, `parse_dates`: see [[Pandas Missing Data Decisions]] and [[Datetime Parsing, Frequency Aliases and Time Zones]].
- The other readers (`read_json`, `read_excel`, `read_parquet`, `read_sql`) follow the same pattern: state types and missing markers up front. `read_html` returns a list of frames; `read_excel` needs `openpyxl`, `read_parquet` needs `pyarrow`.

## Text and keys

- Normalise every text column the same way: `.str.strip().str.lower()`. Spelling variants (`South`/`south`, trailing space) otherwise split groups.
- `str.extract` pulls structure by regex capture group; no match gives `NaN`, not an error.
- Use `regex=False` when removing a literal `$`, then `to_numeric`.
- `map` with a dict gives `NaN` for unmapped values (use when the dict should be complete); `replace` changes only listed values.
- Check duplicates on the column that should be unique, with `keep=False` to see all copies: two rows can share an id yet differ elsewhere, which a whole-row check misses.

## Assertions worth writing

Key uniqueness, no nulls in required columns, values within a plausible range, categories within an allowed set, dates inside the export period. A failed assertion in a script is cheap; a wrong number in a report is not.

## Storage

CSV keeps only text, so every reader redoes type decisions (a date came back as text). Parquet is compressed, columnar and stores dtypes. On a tiny frame the Parquet file was larger (5266 bytes against 556) because metadata outweighs compression; the size advantage appears at scale, the type advantage at once. Use CSV to hand data over and Parquet between your own steps. Pickle is for short-lived scratch only: a later library version may not read it, and unpickling untrusted files can run code.

## Pitfalls

- Editing the raw file by hand makes the work unrepeatable.
- `errors="coerce"` without counting.
- Dropping rows silently; print counts at each step.

## See Also
- [[Pandas Missing Data Decisions]] — prerequisite-for
- [[Pandas Label Alignment and Dtypes]] — prerequisite-for
- [[Groupby Silent Group Loss and Pivot Defaults]] — related
- [[SQL from Python]] — related
- [[Idempotent Batch Loads and Partition Overwrite]] — related
- [[Medallion Layers Need Tests]] — related
