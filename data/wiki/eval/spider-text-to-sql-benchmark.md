---
title: Spider Text-to-SQL Benchmark
tags: [eval, concept]
summary: "Spider is a human-labeled text-to-SQL dataset of 10,181 questions over 200 multi-table databases, split so test databases are unseen; in 2018 the best baseline reached 9.7% exact match on that split against 34.3% when databases were shared (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-yu-2018-spider.md
---

# Spider Text-to-SQL Benchmark

The EMNLP 2018 paper asks if a big dataset of human-labeled text-to-SQL pairs, containing complex SQL over many multi-table databases and divided so no test database appears in training, can gauge true generalisation in semantic parsing. Its hypothesis is that models scoring high on earlier datasets were memorising query templates, and would fail on unseen databases and complex SQL.

## Construction

Over five stages, eleven students authored and reviewed questions and SQL against 200 databases. The paper reports about 1,000 man-hours: 150 for database creation, 500 for annotation, and 150 each for SQL review, question review and final review. The corpus holds 10,181 questions, 5,693 distinct SQL queries and 138 domains; databases average 28 columns and 9 foreign keys. Spider averages 5.1 tables per database against 1 for WikiSQL, and Table 1 counts 1335 ORDER BY queries, 1491 with GROUP BY, 844 nested ones and 388 using HAVING. It is cross-domain, with no database or SQL query shared between training and test. Ambiguous questions and ones needing outside knowledge are excluded.

Three metrics are defined. Component matching is F1 on exact set matching per SQL component. Exact matching asks whether the whole predicted query is equivalent to the gold one. Execution accuracy compares results on SQLite databases. The paper defers execution results to a website.

## Results (self-reported)

Baselines were 2014-2018 neural parsers adapted to take the schema as a column list.

- TypeSQL, the best baseline, reached 9.7% exact match on the database split (40 test databases, all hardness levels) and 34.3% on the example split (7862/1831/2147), about 3.5 times higher.
- Vanilla Seq2Seq dropped to 5.4% on the database split from 11.2% on the example split.
- On the database split TypeSQL scored 29.6% on easy queries and 0.3% on extra hard.
- SQLNet reached 8.3% overall on the database split; its WHERE F1 was 18.0% and its SELECT F1 24.0%; the paper says column selection is poor for all models.
- More foreign keys in a database means lower accuracy (Figure 4, a plot with no numbers).

## Limits

- No baseline has its hyperparameters, optimizers, epochs or seeds reported. Condition values are neither predicted nor evaluated. Column names were cleaned by hand, which means real abbreviated schemas go untested.
- The baselines are pre-LLM parsers and their scores have since been far surpassed.
- Internal inconsistency: the abstract says 200 databases, while the split counts 206, which adds six existing datasets (752 queries, 1659 questions).

## See Also
- [[Text-to-SQL as a Retrieval Strategy]] — prerequisite-for (the use of text-to-SQL this benchmark measures)
- [[Lost in Conversation (Sharded Multi-Turn Simulation)]] — related (its database tasks come from this benchmark)
- [[Simulated User Evaluation]] — related
