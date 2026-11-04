---
title: "Object Store Guarantees and the Partial-Write Problem"
tags: [foundations, concept]
summary: "An object store gives atomic single-key writes and little else: no rename, no multi-key atomicity, so a half-finished overwrite shows readers a wrong answer without error."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--04-warehouse-lakehouse-streaming--notes--01b-object-storage-and-the-data-lake.md
---
# Object Store Guarantees and the Partial-Write Problem

A bucket is not a disk. It has no directories, no rename and no transaction across two keys, and it charges per request. These facts explain why a lake needs a table layer ([[Table Format as a Commit Log over Parquet]]). The behaviour below is from the provider's documentation plus a local emulator that issues real API requests but has none of the real service's latency, durability or scaling.

## Flat keys, no rename

The data model is flat: "folders" are key prefixes split on a delimiter. A prefix is not an object; a key like `odd//name/./x` is legal. Listing returns up to 1,000 keys per request. There is no rename, so moving a prefix means copy-then-delete per object: 2,500 objects took 3 list calls plus 2,500 PUTs and 2,500 DELETEs, and a reader during the move sees some keys in each place. The local-disk habit of writing to a temp directory and renaming does not carry over.

## What is guaranteed

| Guarantee | Meaning |
|---|---|
| Read after write | Strong, for PUT and DELETE of objects, including list after write |
| One key | A concurrent GET sees old or new data, never partial |
| Concurrent writers | No locking; the latest timestamp wins |
| Several keys | No atomic update across keys |
| Bucket settings | Eventually consistent; wait 15 minutes after enabling versioning |

Objects are replaced whole: no append to a Parquet file, so changing one row writes a new object.

## Conditional writes

A precondition on a PUT turns last-writer-wins into compare-and-set. `If-None-Match: *` fails if the key exists; `If-Match: <etag>` fails if the object changed since read. Both return 412 and the first write to finish succeeds.

- Eight writers tried to create one log key: one won, seven got 412. That is enough to build an ordered commit log.
- Eight writers each incrementing a counter 25 times (200 expected): blind read-modify-write ended at 25, so 175 increments vanished silently. With `If-Match` the count was exact at 200, at the cost of 700 retries. Suits low-contention commits, not a hot counter. The emulator handled one request at a time, so it cannot test the real race handling.

## A partial write is a wrong answer

A job rewrites a four-file table (4,000 rows) and dies after writing 2 of 4 new files. A reader listing the prefix sees old and new files together: 6,000 rows, no error. Hand cleanup of two old files returns 4,000 only because every row is identical; with changed values the table is a mix of two versions no query can detect. Idempotent partition overwrites limit the damage but cannot make a multi-file overwrite atomic to a concurrent reader.

The fix uses what is guaranteed: write the new version under a new prefix, then flip one pointer key naming the live prefix with a single atomic PUT. The reader sees the old complete table, then the new one. Add a conditional write on the pointer so two jobs cannot both win and you have the core of a table format.

## Multipart uploads

Large objects use multipart upload (suggested from 100 MB, up to 10,000 parts). Until completed the object does not exist, but its parts do and are billed, invisible to a normal listing. Add a lifecycle rule `AbortIncompleteMultipartUpload` to every bucket.

## See Also
- [[Small Files, Prefix Layout and Storage Tiers]] — related
- [[Table Format as a Commit Log over Parquet]] — extends
- [[Lakehouse vs Warehouse Decision]] — related
