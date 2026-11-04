---
imported_hash: 7f881de11c724b49
decks:
- learn-ai-engineering/programming/sql/slides/deck.yaml
cards:
- front: In what order does SQL evaluate a query?
  back: FROM, WHERE, GROUP BY, HAVING, SELECT, DISTINCT, ORDER BY, LIMIT. Rows have no order unless you ask for one.
  lesson: programming/sql/notes/01-select-and-filter
- front: What does a comparison with NULL return?
  back: '`NULL` means unknown, and `WHERE` keeps only true rows. Test with `IS NULL`, never `= NULL`.'
  lesson: programming/sql/notes/02-nulls-and-expressions
- front: Why can NOT IN return no rows at all?
  back: One `NULL` in the subquery makes `x NOT IN (...)` never true, so use `NOT EXISTS` for anti-joins.
  lesson: programming/sql/notes/02-nulls-and-expressions
- front: What is the difference between count(*) and count(col)?
  back: '`count(*)` counts rows and `count(col)` skips `NULL`. In a grouped query, every column is a key or an aggregate.'
  lesson: programming/sql/notes/03-aggregation
- front: When do you filter with WHERE, and when with HAVING?
  back: '`WHERE` filters rows before grouping and `HAVING` filters groups after. Push all you can into `WHERE`.'
  lesson: programming/sql/notes/03-aggregation
- front: How do you pivot rows into columns portably?
  back: Put `CASE` inside an aggregate, one per output column. It is the portable way to pivot.
  lesson: programming/sql/notes/03-aggregation
- front: Which rows does each join keep?
  back: An inner join drops unmatched rows, and a `LEFT JOIN` keeps every left row with `NULL`s on the right.
  lesson: programming/sql/notes/04-joins
- front: How does WHERE undo a LEFT JOIN?
  back: A `WHERE` filter on the right table discards the `NULL` rows, so put the condition in `ON`. Count `b.bookid`, not `*`.
  lesson: programming/sql/notes/04-joins
- front: Why use a CTE instead of a nested subquery?
  back: A CTE names each step so the query reads top to bottom and each step can be tested alone, usually at no cost.
  lesson: programming/sql/notes/05-subqueries-and-ctes
- front: How does a recursive CTE work?
  back: An anchor, `UNION ALL`, then a step that reads the CTE, repeated until no rows come back. Always give it a stopping condition.
  lesson: programming/sql/notes/05-subqueries-and-ctes
- front: How do you get the top N rows per group?
  back: A window function computes over a group and keeps every row. Rank inside a CTE, because you can't filter on it in the same query.
  lesson: programming/sql/notes/06-window-functions
- front: How do row_number, rank and dense_rank differ?
  back: '`row_number` is always unique, `rank` leaves gaps after ties and `dense_rank` doesn''t.'
  lesson: programming/sql/notes/06-window-functions
- front: What does each constraint promise?
  back: Primary keys, `UNIQUE`, `NOT NULL`, `CHECK` and foreign keys are promises, and SQLite enforces foreign keys only after the pragma.
  lesson: programming/sql/notes/07-modeling-and-ddl
- front: How do you make writes safe to re-run?
  back: Idempotent loads use upserts or delete-then-insert in a transaction. Check `UPDATE` and `DELETE` with `SELECT count(*)` first.
  lesson: programming/sql/notes/07-modeling-and-ddl
- front: How do you read a query plan?
  back: The first line is the outer table of the join. Ask whether it is a `SEARCH` or a `SCAN`, and how many rows it feeds the rest.
  lesson: programming/sql/notes/08-indexes-and-query-plans
- front: Which queries can use an index on (memid, starttime)?
  back: Put equality columns first and the range or sort column last, like a phone book sorted by surname then first name.
  lesson: programming/sql/notes/08-indexes-and-query-plans
- front: What makes a predicate sargable?
  back: Wrapping an indexed column in a function usually hides it from the index, so compare the bare column.
  lesson: programming/sql/notes/08-indexes-and-query-plans
- front: How do values get from Python into SQL safely?
  back: The driver sends SQL and values separately. Parameters work only for values, so check table names against an allow-list.
  lesson: programming/sql/notes/09-sql-from-python
- front: How do you handle `NULL`, joins, slow queries and user values?
  back: Handle `NULL` deliberately, check row counts after joins, read the plan, and pass values as parameters.
  lesson: programming/sql/notes/02-nulls-and-expressions
- front: How do you practise all of it at once?
  back: The SQL Murder Mystery uses only notes 01 to 05. Keep going after your first answer, because there is a second twist.
  lesson: programming/sql/notes/10-capstone-murder-mystery
---
