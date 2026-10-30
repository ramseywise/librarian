---
title: SQL Schema Design and DDL
tags: [foundations, concept]
summary: "A schema makes promises about its data and constraints let the database keep them: the four data-hygiene rules behind normal forms, PRIMARY KEY/UNIQUE/CHECK/FOREIGN KEY semantics (and SQLite's off-by-default foreign keys), safe UPDATE/DELETE, ON CONFLICT upserts for idempotent loads, atomic transactions, and views vs materialised views."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/programming--sql--notes--07-modeling-and-ddl.md
  - data/raw/repos/learn-ai-engineering/programming--sql--README.md
---

# SQL Schema Design and DDL

> A schema makes promises about its data. Constraints let the database keep those promises for you.

## Data hygiene: the rules behind normal forms

Software Carpentry's checklist covers most normalisation in practice:

1. **Each value is atomic.** Store `personal` and `family` separately, not `"William Dyer"` in one field. Concatenating later is easy; splitting reliably is hard.
2. **Each record has a unique key that never changes and carries no meaning** (`memid`, not the member's email).
3. **No redundant data.** Store a facility's cost once, in `facilities`, not copied into every booking — redundant copies drift apart.
4. **Units are explicit**, in the column name (`reading_c`, `duration_slots`) or a separate column.

Breaking rule 3 deliberately (denormalising) is legitimate for analytics tables built by a pipeline — provided the pipeline, not humans, keeps the copies in sync.

## Creating tables

```sql
CREATE TABLE facility_price_history (
    facid      INTEGER NOT NULL REFERENCES facilities(facid),
    valid_from DATE    NOT NULL,
    membercost NUMERIC NOT NULL CHECK (membercost >= 0),
    guestcost  NUMERIC NOT NULL CHECK (guestcost >= membercost),
    PRIMARY KEY (facid, valid_from)
);
```

| Constraint | Promise |
|---|---|
| `PRIMARY KEY` | Unique and not `NULL`; one per table; may span columns |
| `UNIQUE` | No duplicates — **but multiple `NULL`s are allowed** |
| `NOT NULL` | Value must be present |
| `CHECK (…)` | Arbitrary per-row condition (can compare columns) |
| `REFERENCES` / `FOREIGN KEY` | Value must exist in the parent; `ON DELETE CASCADE / SET NULL / RESTRICT` decides what happens when the parent goes |
| `DEFAULT …` | Used when an insert omits the column |

**SQLite enforces foreign keys only after `PRAGMA foreign_keys = ON;`, once per connection** — the single most common SQLite surprise. A declared `REFERENCES` is otherwise documentation only.

## Changing data safely

```sql
UPDATE facilities SET initialoutlay = 10000 WHERE facid = 1;
DELETE FROM bookings WHERE memid = 37;
```

**`UPDATE` or `DELETE` without `WHERE` changes every row.** Before running one, run the same `WHERE` as `SELECT count(*)` to see how many rows it would touch.

## Upsert

```sql
INSERT INTO facilities (facid, name, membercost, guestcost, initialoutlay, monthlymaintenance)
VALUES (9, 'Spa', 25, 35, 100000, 800)
ON CONFLICT (facid) DO UPDATE
  SET membercost = excluded.membercost, guestcost = excluded.guestcost;
```

`ON CONFLICT … DO UPDATE` works in SQLite, Postgres and DuckDB; `excluded` is the row you tried to insert. **Idempotent loads** — re-running a pipeline step without duplicating data — are built on upserts, or on delete-then-insert inside a transaction. What an upsert's `SET` list omits never gets refreshed on existing rows; see [[Insert-Only Upserts Strand Normalizer Fixes]].

## Transactions

```sql
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;      -- or ROLLBACK to undo both
```

A transaction is **atomic**: every statement takes effect or none does. Wrap multi-step writes in one. In Python, `with sqlite3.connect(…) as conn:` commits on success and rolls back on exception — but does not close the connection ([[SQL from Python]], [[Python Exceptions and Context Managers]]).

## Views

```sql
CREATE VIEW member_usage AS
SELECT memid, count(*) AS bookings, sum(slots) AS slots FROM bookings GROUP BY memid;
```

A view is a saved query, so it always reflects current data. A materialised view (Postgres), or a table rebuilt by a pipeline, stores the result for speed at the cost of going stale.

## See Also
- [[SQL Query Fundamentals]] — prerequisite-for
- [[SQL Indexes and Query Plans]] — extends (physical design on top of the logical schema)
- [[SQL from Python]] — extends (transactions and batch loads from code)
- [[Insert-Only Upserts Strand Normalizer Fixes]] — related (an upsert failure mode in a real pipeline)
- [[Idempotency Lives on the Link Column, Not the Synthetic Key]] — related (a UNIQUE constraint that doesn't make a backfill idempotent)
- [[Data Engineering Foundations]] — related (denormalised analytics tables built by pipelines)
- [[Programming Curriculum]] — related (course map)
