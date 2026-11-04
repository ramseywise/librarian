---
title: "Encoding Compatibility and Schema Evolution"
tags: [foundations, concept]
summary: "Data outlives code, so a format must be both backward and forward compatible; text formats silently destroy types, and schema-carrying binary formats (Avro, Protobuf) make evolution a checked property, with silent drift across files as the remaining trap."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--01-storage-and-compute-foundations--notes--02-encoding-and-files.md
---

# Encoding Compatibility and Schema Evolution

Pipeline stages are programs that never meet: the one that wrote a file is gone and the one reading it was written by someone who never saw it. The bytes are all they share, so the format decides how much the reader must guess. Data outlives code: a redeploy takes minutes, but a five-year-old partition keeps the shape it was written in.

- **Backward compatibility:** new code reads data written by old code (easy, the author knows the old format).
- **Forward compatibility:** old code reads data written by new code (harder: it must ignore what did not exist yet).

A warehouse needs both: years of files from past schemas, and consumers that lag the producer during any rollout. Language-native formats such as `pickle` fail first: one language, arbitrary code on load, versioning an afterthought. Acceptable for a rebuildable cache only.

## What text formats leave unsaid

A CSV has no schema, so the reader guesses, and a sensible guess destroys data silently: zip code `02134` became integer `2134` and amount `007` became `7` with no error. State the schema on first read; treat inference as exploration only. Gzip shrinks a 48.7 MB CSV to 11.7 MB, but a compressed CSV still must be decompressed and parsed from the first byte to read one column.

JSON distinguishes strings from numbers but has no integer, decimal, date or binary type (binary is base64-encoded at roughly a third more bytes). Readers that parse every number as a double cannot hold integers above 2^53: 9007199254740993 came back as 9007199254740992, off by one and looking fine. APIs work around this by returning IDs also as strings. Check any key column that passes through a JSON API. Text formats suit interchange between organisations, where agreement matters more than efficiency.

## Schema-carrying binary formats

One small record took 81 bytes as compact JSON, 66 in MessagePack (which still repeats every field name), 59 in Thrift binary, 34 in Thrift compact, 33 in Protocol Buffers and 32 in Avro. Avro bytes hold no field names or tags, so a reader needs the **writer's schema**; it resolves it against the **reader's schema** by field name. They must be compatible, not identical.

- **Avro rule:** add or remove only fields that have a default. A new field with a default reads old data; a new required field fails loudly with a resolution error, which is the feature.
- **Protobuf/Thrift:** numbered field tags. Rename freely (names are not in the data), but never change a tag's meaning or reuse a deleted tag; new fields cannot be required, only optional fields can be removed. Widening a type can truncate silently when old code reads a 64-bit value into 32 bits.
- Avro's by-name resolution lets a schema be generated from a database table on every export, which is why it suits dumps and streams. A rename through a reader alias is backward but not forward compatible.

| Setting | Where the writer's schema lives |
|---|---|
| Large file of many records | Once, at the start of the container file |
| Database of records written over time | A version number per record, with a table of versions |
| Message stream | Negotiated on connect, or a version ID resolved through a schema registry |

A registry also refuses an incompatible change before it ships. One failure survives the tooling: an old service decodes a record written by newer code into a model class and writes it back, dropping fields it did not know. Check the application, not just the format.

Which side must be compatible depends on direction. For a service, deploy servers first, so requests need backward compatibility and responses forward. Writing to a database is a message to your future self; a bulk rewrite is worth doing only when making an archive snapshot anyway.

## Schema drift across files

A dataset is many files over time. When February's file adds a column, reading both Parquet files in DuckDB without `union_by_name=true` takes the first file's schema and drops the new column with no error or warning. Read by name, or use a table format that keeps schema history in a transaction log.

## See Also
- [[Parquet Row Groups, Pruning and Sort Order]] — related (the at-rest format this feeds)
- [[Relational, Document and Graph Models and Schema on Read]] — prerequisite-for
- [[Idempotent Retries and Request IDs]] — related (a service call can time out with no way to know if it ran)
