---
title: SQL from Python
tags: [foundations, pattern]
summary: "SQL does the set operations and Python orchestrates: sqlite3 connection/cursor mechanics (the `with` block commits but doesn't close), parameters instead of f-strings with allow-lists for identifiers, DuckDB for SQL over files and DataFrames, and filter-in-SQL/reshape-in-pandas as the division of labour."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/programming--sql--notes--09-sql-from-python.md
  - data/raw/repos/learn-ai-engineering/programming--sql--README.md
---

# SQL from Python

> SQL does the set operations. Python does the orchestration. Values cross the boundary as **parameters**, never as pasted strings.

## sqlite3 (standard library)

```python
import sqlite3

with sqlite3.connect("clubdata.db") as conn:      # commits or rolls back on exit
    conn.row_factory = sqlite3.Row                 # rows behave like dicts
    rows = conn.execute(
        "SELECT surname, firstname FROM members WHERE joindate >= ? ORDER BY joindate",
        ("2012-09-01",),
    ).fetchall()

for r in rows:
    print(r["firstname"], r["surname"])
```

- `execute` returns a cursor: `fetchone()`, `fetchall()`, or iterate to stream rows.
- `executemany(sql, rows)` batch-inserts. Wrap large loads in one transaction — which is what the `with` block does.
- **The `with` block commits or rolls back; it does not close the connection.** Call `conn.close()` or use `contextlib.closing`. See [[Python Exceptions and Context Managers]] for the protocol, and [[SQL Schema Design and DDL]] for transaction semantics.
- SQLite foreign keys need `PRAGMA foreign_keys = ON` per connection.

## Parameters, not f-strings

```python
name = "O'Brien'; DROP TABLE members; --"
conn.execute(f"SELECT * FROM members WHERE surname = '{name}'")   # SQL injection
conn.execute("SELECT * FROM members WHERE surname = ?", (name,))  # safe
```

The driver sends SQL and values separately, so a value can never become code. Placeholder styles differ: `?` (sqlite3, DuckDB), `%s` (psycopg), `:name` (sqlite3, SQLAlchemy).

**Parameters work only for values.** A table or column name cannot be parameterised; if one must be dynamic, check it against an allow-list. [[Production Hardening Patterns]] records exactly this bug — filter *keys* interpolated into DuckDB SQL — and its allow-list fix.

## DuckDB: analytics in-process

```python
import duckdb, pandas as pd

duckdb.sql("SELECT facid, sum(slots) FROM 'bookings.parquet' GROUP BY facid").show()
duckdb.sql("SELECT * FROM read_csv('data/*.csv') WHERE amount > 100").df()   # → pandas

df = pd.DataFrame({"x": [1, 2, 3]})
duckdb.sql("SELECT avg(x) FROM df")      # queries an in-scope DataFrame by variable name
```

DuckDB is columnar and vectorised. It queries CSV, Parquet, JSON, and pandas/Polars frames directly with no load step, and can attach SQLite files (`ATTACH 'clubdata.db' (TYPE sqlite)`). It is the quickest way to put SQL in front of files.

## pandas ↔ SQL

```python
df = pd.read_sql("SELECT * FROM bookings WHERE facid = ?", conn, params=(1,))
df.to_sql("bookings_copy", conn, if_exists="replace", index=False)
```

**Division of labour: filter and aggregate in SQL** (the database reads less and sends back less); **reshape and plot in pandas**. Pulling a million rows to compute one `groupby` in pandas is the classic anti-pattern. Moving a filter out of SQL can also change what a `LIMIT` keeps — see [[Dropped Filter Flips the Truncation Direction]].

## SQLAlchemy (when you need it)

SQLAlchemy Core gives one API across engines plus connection pooling; the ORM maps classes to tables. Use it in applications. For analysis scripts and pipelines, plain DB-API (`sqlite3`, `psycopg`) or DuckDB is simpler.

```python
from sqlalchemy import create_engine, text
engine = create_engine("sqlite:///clubdata.db")
with engine.connect() as c:
    c.execute(text("SELECT count(*) FROM bookings WHERE facid = :f"), {"f": 1}).scalar_one()
```

## See Also
- [[Python Foundations Reference]] — prerequisite-for (its databases section)
- [[Python Exceptions and Context Managers]] — prerequisite-for (how `with` commits/rolls back)
- [[SQL Query Fundamentals]] — prerequisite-for
- [[SQL Schema Design and DDL]] — prerequisite-for (transactions, upserts, foreign-key pragma)
- [[Production Hardening Patterns]] — instance-of (DuckDB identifier-injection fix via allow-list)
- [[Dropped Filter Flips the Truncation Direction]] — related (moving a SQL filter into Python changes LIMIT semantics)
- [[Text-to-SQL as a Retrieval Strategy]] — related (LLM-generated SQL executed from Python)
- [[Programming Curriculum]] — related (course map)
