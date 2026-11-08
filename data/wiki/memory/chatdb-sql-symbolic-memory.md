---
title: ChatDB SQL Symbolic Memory
tags: [memory, pattern]
summary: "ChatDB lets an LLM controller keep its memory in a SQL database and turn each request into a chain of SQL steps; on a 50-question synthetic shop dataset it scored 41/50 against 11/50 for the same model with the records in its prompt (self-reported, single run)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-hu-2023-chatdb.md
---

# ChatDB SQL Symbolic Memory

ChatDB (2023 preprint) argues that vector-similarity memory stores history without structure and manipulates it through inexact similarity, which can accumulate errors; the paper asserts this and does not measure it. Its alternative is a database as symbolic memory: an LLM controller reads and writes a MySQL store.

## Mechanism

Algorithm 1 has three stages: input processing, chain-of-memory, and response summary. If the request needs no memory the LLM answers directly. Otherwise the LLM writes a list of memory operations (SQL statements), and later operations are rewritten from the results of earlier ones before each is run against the database; the executed results are then summarised into the reply. A return in a fruit shop, for example, becomes SELECT, SELECT, UPDATE of stock, then DELETE of the sale rows, each step using values from the previous query. The authors compare the chain to chain-of-thought and give arithmetic to SQL, and they state that the database holds the current state and can be rolled back to a given time.

## Result

On a synthetic fruit-shop dataset (70 chronological records, about 3.3k tokens, 50 questions, 15 easy and 35 hard), temperature 0, each question answered independently, single run: ChatDB with GPT-3.5 Turbo scored 41/50 (82%) against 11/50 (22%) for GPT-3.5 Turbo with the records in its prompt (4096-token maximum). Easy questions: 13/15 against 10/15; hard: 28/35 against 1/35 (self-reported). The paper's examples show the baseline making arithmetic errors, missing or wrongly including records, and being cut off at the token limit.

## Limits

- One synthetic dataset, 50 questions, one run, no variance, no vector-RAG or other memory-system baseline.
- The data was kept under the context limit on purpose; the claim that ChatDB's advantage extends to larger data, and that it can handle unlimited records without losing performance, is theory and untested.
- The schema must be created manually or by an LLM; schema quality is not discussed. No SQL error rate is reported, although the paper says each database step is free from errors: only execution is symbolic, and 9 of 50 questions were still missed.
- No failure analysis, cost or latency, multi-session or unstructured-fact memory, or comparison with a program-of-thought route.
- The qualitative comparison table (prompt-based, matrix-based and symbolic memory) is the authors' judgement, not a measurement. The models are dated (GPT-3.5 Turbo, 4k window).

## See Also
- [[Memory Lifecycle]] — prerequisite-for
- [[Text-to-SQL as a Retrieval Strategy]] — related (the retrieval side of SQL access)
- [[Memory Forms Taxonomy]] — prerequisite-for
- [[MemInsight Attribute Augmentation]] — related (a different structured-annotation route)
