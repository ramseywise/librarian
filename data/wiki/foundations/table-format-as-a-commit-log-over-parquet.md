---
title: "Table Format as a Commit Log over Parquet"
tags: [foundations, pattern]
summary: "A table format turns a bucket of immutable Parquet files into a table by keeping an ordered log of live files, committed by one atomic create, which gives atomic commits, time travel and optimistic concurrency."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--04-warehouse-lakehouse-streaming--notes--02-table-formats.md
  - data/raw/repos/learn-ai-engineering/data-engineering--04-warehouse-lakehouse-streaming--notes--01b-object-storage-and-the-data-lake.md
---
# Table Format as a Commit Log over Parquet

A nightly job rewrites a month of data in the lake and the instance dies halfway: half the data is new, half is gone, and every dashboard reading the directory reports a wrong number without an error. Nothing in a bucket says which files belong together ([[Object Store Guarantees and the Partial-Write Problem]]). The fix: stop treating the directory as the table. The table is a list of files, stored as an ordered series of records in the object store. A reader consults the list, never the directory, so files not named in the list do not exist to any reader.

## Mechanism

- Data files are immutable Parquet. The log is numbered records (`000000.json`, `000001.json`, ...) of `add` and `remove` actions; the live set at version N is the replay of records 0..N.
- **The commit** is creating the next numbered record, with create-if-absent semantics (exclusive create, a conditional PUT, or a catalog pointer swap). Only one writer can win that name.
- **Optimistic concurrency:** write data files first, claim the slot last. A loser re-reads what the winner changed and decides whether the two actually conflict. Two appends never do; a delete of a file the other writer also rewrote does, and that writer redoes its work.
- **Copy-on-write delete:** only files holding the row are rewritten, and one commit removes the old and adds the new. A toy version left 3 data files on disk with 2 live; version 1 stayed readable (time travel costs only storage).
- **Crash is harmless:** a Parquet file written before the commit fails is an orphan, invisible to readers; the only damage is wasted storage until cleanup.
- **Statistics in the log:** each `add` carries min and max per column, so a reader skips files from the log alone, without listing the directory or opening footers.
- **Checkpoints:** replaying thousands of JSON records is slow, so formats periodically write a Parquet checkpoint; Delta's Spark writer defaults to one every 10 transactions, and a reader starts at the latest. A Rust writer given twelve plain appends wrote none until asked.

A vendor benchmark on a 33-million-row synthetic table split into 1,000 to 1,000,000 partitions: one engine took over an hour at 10,000 partitions, another over an hour at 100,000, while the log-based reader took 108 s at one million partitions and 17 s with the log cached on SSD. The cause is structural: reading a log with statistics replaces listing and opening footers.

Which stores had the primitive: some offered atomic put-if-absent, one an atomic rename, and S3 at the time needed a coordinator to allot log record IDs; conditional PUTs now supply it.

## In database terms

The commit point is the durable record deciding the fate of a set of writes; snapshot isolation is a reader pinning a version, with unreferenced files as old row versions and vacuum as garbage collection (too eager cleanup breaks long readers and time travel); optimistic concurrency inherits the weakness of retries under contention; a numbered log only one writer can extend is a total order built on compare-and-set. Consensus is moved into the store or catalog, not removed.

## Delta specifics

Each commit is a file of newline-delimited actions: `commitInfo` (audit trail), `protocol`, `metaData`, `add`, `remove`. A DELETE commit holds an `add` with a `remove` (a file was rewritten); a MERGE can hold two `add`s. The `add` record's `stats` field holds record counts and min/max per column. A `txn` action stores an application ID and version in the same commit as the data, which is what makes an exactly-once sink possible ([[Delivery Guarantees and Effectively-Once Processing]]).

**Vacuum** deletes unreferenced files older than a retention window. With retention forced to zero, a table with 5 Parquet files on disk and 3 live lost 2, and reading version 1 then failed with `FileNotFoundError` though the log still listed it. Retention sets how far time travel reaches, and a deleted person's row stays in old files until vacuum runs.

## What it does not give you

A format serialises commits; it does not make your pipeline serialisable. Two jobs each read version 0, saw 2 drivers on duty, and each appended an off-duty row; both commits succeeded and 0 were on duty, breaking the rule. Appends cannot conflict. Keep such a rule inside one `MERGE` or `UPDATE` (which record what they read) or run one writer. Also: no multi-table transactions in the log-per-table design.

## Pitfalls

- **Reading the directory instead of the table** returns unreferenced files and resurrects deleted rows ([[Lakehouse vs Warehouse Decision]]).
- **Vacuuming below the time-travel promise.**
- **Never compacting.** Streaming writers make many small files per commit ([[Small Files, Prefix Layout and Storage Tiers]]); schedule compaction as a production job.
- **Hand-copying a table directory** can break absolute paths or lose commit order.

## See Also
- [[Iceberg Metadata Tree and Hidden Partitioning]] — alternative-to
- [[Copy-on-Write vs Merge-on-Read]] — related
- [[Object Store Guarantees and the Partial-Write Problem]] — prerequisite-for
- [[Lakehouse vs Warehouse Decision]] — related
