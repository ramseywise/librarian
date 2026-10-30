---
title: Programming Curriculum
tags: [foundations, reference]
summary: "Course map for the three languages an AI or data engineer writes daily — Python, SQL, TypeScript — with the phase order, the hand-offs between tracks, the rules of thumb each track ends on, and where each topic's wiki page lives."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/programming--README.md
  - data/raw/repos/learn-ai-engineering/programming--CURRICULUM.md
  - data/raw/repos/learn-ai-engineering/programming--references.md
  - data/raw/repos/learn-ai-engineering/programming--python--README.md
  - data/raw/repos/learn-ai-engineering/programming--python--04-python-for-data--README.md
  - data/raw/repos/learn-ai-engineering/programming--sql--README.md
  - data/raw/repos/learn-ai-engineering/programming--typescript--README.md
---

# Programming Curriculum

The *Programming* course is the depth layer under everything else in the learning repo:
the three languages the rest of the material is written in. Each track runs from first
principles to the idioms production code relies on, as short notes plus exercises that
run offline. It is the entry point; it has no prerequisites beyond a terminal, Python
3.12+, the `sqlite3` CLI and Node 22.18+.

The split between repos: the course teaches the skill, a separate drills repo practises
it (timed HackerRank/LeetCode-style problems and interview-format rounds), and librarian
shows both, as the *Programming* and *Drills* courses. Notes and drills share
`concepts:` slugs, so a drill links back to the note that teaches it.

## Phase Order

Python comes first because the other two tracks assume you can read it. SQL starts once
Python 01 is done, TypeScript once Python 03 is done.

| Phase | Python | SQL | TypeScript | Roughly |
|---|---|---|---|---|
| 1. Write programs | 01 foundations | — | — | 2 weeks |
| 2. Talk to the world | 02 informatics | 01–05: select → CTEs | — | 2–3 weeks |
| 3. Write it like an engineer | 03 language for engineers | 06–09: windows, DDL, indexes, SQL from Python | — | 3 weeks |
| 4. Analyse data | 04 Python for data | 10: capstone | 01–05: JS → type transformations | 3–4 weeks |
| 5. Build typed apps | — | — | 06–09: async, tooling, Zod, TS for AI apps | 2 weeks |

**Skip what you already know.** Every module's exercises double as a placement test: if
the file passes on the first try, move on.

## Hand-offs Between Tracks

| When you finish | You're ready for |
|---|---|
| Python 02 · 05 (databases from Python) | SQL 01 |
| SQL 09 | Python 04's DataFrame joins, with the SQL mental model |
| Python 03 · 07 (concurrency) | TypeScript 06 — the same async model with promises |
| Python 03 · 05 (types, Pydantic) | TypeScript 02 and 08 — types and boundary validation with a stricter checker |
| Python 04 | Data analytics and data science courses |
| Python 03 + TypeScript 09 | AI engineering — every pillar's code is Python or TS |

## Tracks and Wiki Pages

**Python** — *Python for Everybody* order for 01–02 (paraphrased), *A Whirlwind Tour of
Python* and the Python docs for 03, McKinney's *Python for Data Analysis* for 04.
- 01–02: [[Python Foundations Reference]]
- 03: [[Python Data Model and Idioms]], [[Python Generators and Lazy Iteration]],
  [[Python Closures and Decorators]], [[Python Exceptions and Context Managers]],
  [[Python Type Hints and Dataclasses]], [[Python Packaging and Tooling]],
  [[Python Concurrency Models]]
- 04 (Python for data): seven compact notebooks — arrays and broadcasting, Series vs
  DataFrame, plotting, `groupby` aggregation, time series — then McKinney's chapters on
  loading, cleaning, wrangling (merge/concat/reshape), aggregation and time series. The
  book's chapters 2–5 are skipped because Python 01–03 cover them.

**SQL** — Software Carpentry's *Databases and SQL*, PGExercises (converted to SQLite) and
*Use The Index, Luke* for indexing; the Knight Lab SQL Murder Mystery as capstone.
- [[SQL Query Fundamentals]], [[SQL NULL and Three-Valued Logic]], [[SQL Join Patterns]],
  [[SQL Subqueries and CTEs]], [[SQL Window Functions]], [[SQL Schema Design and DDL]],
  [[SQL Indexes and Query Plans]], [[SQL from Python]]

**TypeScript** — the TypeScript Handbook (paraphrased), vendored *typescript-exercises*
and *type-challenges*, Zod's docs, and the Anthropic TypeScript SDK for the last module.
- [[TypeScript for Python Developers]], [[TypeScript Discriminated Unions and Narrowing]],
  [[TypeScript Generics and Type Transformations]], [[TypeScript Async Patterns]],
  [[TypeScript Modules and Tooling]], [[Runtime Validation with Zod]],
  [[TypeScript for AI Apps]]
- Lint findings in practice: [[TypeScript any Escapes]]

## Rules of Thumb, by Track

**Python**
- Functions return values; printing is for the edge of the program.
- `with` for anything that must be closed or released: files, connections, locks.
- Catch the narrowest exception you can actually handle; let the rest crash with a traceback.
- `None` as a default, never `[]` or `{}`.
- Values reach SQL as `?` parameters, never through f-strings.
- Type every signature. Validate data from outside the program (Pydantic) and trust it afterwards.
- Iterate lazily over anything that might be large.

**SQL**
- Write the query in evaluation order (`FROM` → `WHERE` → `GROUP BY` → `HAVING` → `SELECT` → `ORDER BY`).
- `NULL` is "unknown": `= NULL` is never true, and `NOT IN` with a `NULL` in the list returns nothing.
- Date ranges are half-open (`>= start AND < next_start`), which is right for timestamps and keeps the index usable.
- A filter on the right table of a `LEFT JOIN` belongs in `ON`, not `WHERE`.
- Top-N per group is `row_number() OVER (PARTITION BY … ORDER BY …, unique_col)` in a CTE, filtered outside.
- Run `SELECT count(*)` with the same `WHERE` before any `UPDATE` or `DELETE`.

**TypeScript**
- Types are erased; `as` checks nothing, so parse anything from outside the program with a schema.
- Annotate signatures and exports; let inference handle the rest.
- `unknown` instead of `any`, narrowed before use.
- Model "one of these" as a discriminated union and end the `switch` with a `never` check.
- Always `await` or return a promise; `Promise.all` for independent work, with a limit for large fan-outs.
- Turn on `strict` from day one.

## Definition of Done (per module)

1. The note's code samples run as written.
2. Every exercise has a worked solution, and the solutions check is green.
3. Exercises run offline, or say what they need (only the TypeScript live example needs an API key).
4. Every note has `sources` and `concepts` frontmatter.

## See Also
- [[Data Science Curriculum Layers]] — related (sibling course map; Python 04 hands off to it)
- [[Programming Interview Study Guide]] — related (the interview-format review of the same languages)
- [[Python Foundations Reference]] — extends
- [[SQL Query Fundamentals]] — extends
- [[TypeScript for Python Developers]] — extends
