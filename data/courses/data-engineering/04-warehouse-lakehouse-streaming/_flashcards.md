---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- data-engineering/04-warehouse-lakehouse-streaming/slides/deck.yaml
cards:
- front: In what order does this lecture take the trips from storage to cost?
  back: The lecture moves from how one table is laid out, through a log and the lake against the warehouse, to streams and then the bill.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/readme
- front: Name four things this lecture teaches you to do with stored and streamed data.
  back: You will be able to lay data out, trust a table, choose a system of record and price it before the invoice arrives.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/readme
- front: Why does a column store make SELECT star expensive?
  back: A column store reads only the columns you name, so your column list is your first cost control.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/01-warehouse-and-store
- front: Why does sorted data skip row groups when unsorted data skips none?
  back: Clustering works through block statistics, which is why sorted data skips 29 of 30 row groups and unsorted skips none.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/01-warehouse-and-store
- front: What does partial aggregation shrink in a groupBy?
  back: Partial aggregation shrinks what crosses the network from every row to one result per key per executor.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/01-warehouse-and-store
- front: Why did the same one-column query read 12 times more bytes from 1,000 files?
  back: A footer read brings in over half of a 30 KB file, so pruning stops working once a file is about the size of that read, and compaction is the fix.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/01b-object-storage-and-the-data-lake
- front: Why does a table scanned twice a month belong in Standard?
  back: Retrieval fees outrun the storage saving at about one full scan a month, so check access logs first, and compact first because transitions charge per object.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/01b-object-storage-and-the-data-lake
- front: Why can a reader see half a rewrite when every PUT is atomic?
  back: Atomicity stops at one key, so a job dying 2 files into rewriting a 4-file table left readers counting 6,000 rows instead of 4,000, with no error.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/01b-object-storage-and-the-data-lake
- front: Which single step makes a commit atomic?
  back: One atomic create is the whole commit, so anything not named in the log does not exist.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/02-table-formats
- front: What limits Delta time travel, and what kind of decision does that make retention?
  back: Time travel lasts only until vacuum removes the files, so retention is a design decision.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/02-table-formats
- front: How do you keep a rule that spans rows safe under concurrent commits?
  back: Keep a rule of this kind inside one MERGE or UPDATE, or run one writer at a time, because the table cannot check a read it never saw.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/02-table-formats
- front: What do the open table formats share, and how do you choose between them?
  back: All three name live files in atomic metadata, so choose by engines and catalog, then check current docs.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/02-table-formats
- front: What should you know before choosing copy-on-write or merge-on-read, and why?
  back: Know your update distribution first, because random updates touch every file and clustered ones hardly any.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/02-table-formats
- front: What do open files give every engine, and what is the trap?
  back: Open files let every engine read one copy, and let any reader get it wrong with no error.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/03-lakehouse-vs-warehouse
- front: What did the crash do to each system?
  back: Log-per-table formats commit tables separately, so anything that must always agree needs a design around it.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/03-lakehouse-vs-warehouse
- front: What do medallion layers tell you, and what do they not?
  back: Layers say where a problem gets fixed, and only a test says that one happened.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/03-lakehouse-vs-warehouse
- front: What is the real decision behind warehouse versus lakehouse?
  back: The real decision is where the system of record lives and who owns the format.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/03-lakehouse-vs-warehouse
- front: Which order loses money and which invents it?
  back: Commit output and offset together or make the sink idempotent, because neither order alone is safe.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/04-kafka-and-stream-semantics
- front: What does exactly-once mean, and where does it stop?
  back: Exactly-once means the final effect is as if no fault occurred, and it stops at the transaction boundary.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/04-kafka-and-stream-semantics
- front: What is a watermark, and what does late data still need?
  back: A watermark is a heuristic claim about completeness, and late data still needs a policy.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/04-kafka-and-stream-semantics
- front: What does a watermark trade off?
  back: A stream never says a window is complete, so a watermark trades lost events against stale numbers.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/04-kafka-and-stream-semantics
- front: Where do you start on warehouse cost, and why not storage?
  back: Storage is the small number, so start with what queries read and where data travels.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/05-cost
- front: What does a byte limit in CI change about finding expensive queries?
  back: A byte limit in CI finds the expensive query at review, so the invoice stops being the alarm.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/05-cost
- front: Which common cost controls do not do what they appear to?
  back: Each of these looks like a control and is not, so check bytes scanned and set a cap before you trust one.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/05-cost
- front: Why tune the query before buying capacity?
  back: Each fix changes what the next should be, so tune the query before you buy capacity.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/05-cost
- front: Why is a columnar store faster for analytics?
  back: Scans read only named columns; similar values compress well; execution runs on vectors of a column.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/01-warehouse-and-store
- front: Partitioning or clustering first?
  back: Partition on the date you always filter by; cluster on the next filters. Partition savings are known before the query, clustering savings only after.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/01-warehouse-and-store
- front: Why does a `groupBy` shuffle, and what limits its cost?
  back: Equal keys must meet on one executor. Partial aggregation first means one partial result per key per executor crosses the network.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/01-warehouse-and-store
- front: Broadcast or sort-merge join?
  back: Broadcast when one side fits in executor memory; otherwise sort-merge, which shuffles both sides.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/01-warehouse-and-store
- front: When does DuckDB replace Spark?
  back: When the data fits one machine's disk and memory limits with spilling, and no cluster-wide concurrency is needed.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/01-warehouse-and-store
- front: External or native table?
  back: External when other engines share the files or you are exploring; native for cost estimates and maximum performance.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/01-warehouse-and-store
- front: What does separating storage from compute buy?
  back: Resize, pause or run several clusters over one copy of the data. A pure shared-nothing system ties them together, so a resize reshuffles data.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/01-warehouse-and-store
- front: 'Redshift: distribution key or sort key?'
  back: Distribution places rows on nodes, so choose it for joins and even spread. Sort key orders blocks so min and max can skip them, so choose it for filters.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/01-warehouse-and-store
- front: BigQuery or Snowflake pricing?
  back: On-demand BigQuery bills bytes scanned, so layout directly lowers the bill. Snowflake bills warehouse time, so runtime and idle time do.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/01-warehouse-and-store
- front: Snowflake versus Airflow?
  back: Not alternatives. Snowflake stores and computes; Airflow schedules work that may run in Snowflake.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/01-warehouse-and-store
- front: Is S3 eventually consistent?
  back: Not for objects, since strong read-after-write arrived. Bucket configuration still is. Atomicity stops at one key.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/01b-object-storage-and-the-data-lake
- front: Why can't you rename a folder on S3?
  back: Folders are key prefixes. A rename is a copy and delete per object, so it isn't atomic and costs a request per object.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/01b-object-storage-and-the-data-lake
- front: What do conditional writes add?
  back: '`If-None-Match` and `If-Match` make a `PUT` fail with 412 if the object exists or has changed, which is enough to commit to a log.'
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/01b-object-storage-and-the-data-lake
- front: Why are small files bad?
  back: More requests per GB, per-file footers, worse compression, and column pruning stops working once a file is about the size of a footer read. Compaction fixes them.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/01b-object-storage-and-the-data-lake
- front: When do cold tiers lose money?
  back: When reads are frequent enough for retrieval fees to exceed the saving, or objects are small enough for transition fees and minimums to dominate.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/01b-object-storage-and-the-data-lake
- front: What is a data lake missing compared with a warehouse?
  back: Multi-key atomicity, schema enforcement and fast metadata. Table formats add these on top of object storage.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/01b-object-storage-and-the-data-lake
- front: What is the S3 request-rate limit?
  back: At least 3,500 writes and 5,500 reads per second per partitioned prefix, scaling gradually, with 503s while it scales.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/01b-object-storage-and-the-data-lake
- front: What is a table format?
  back: Metadata over immutable data files that names which files are the table, committed atomically.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/02-table-formats
- front: How does a commit become atomic on an object store?
  back: 'One atomic step: put-if-absent of the next log record, or a catalog pointer swap.'
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/02-table-formats
- front: Does a table format make my pipeline serializable?
  back: No. It serialises commits. A read done outside the commit, followed by a blind append, can still produce write skew.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/02-table-formats
- front: What is optimistic concurrency here?
  back: Write files first, claim the next version last; on a lost race, check for conflict and retry.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/02-table-formats
- front: Copy-on-write or merge-on-read?
  back: CoW pays at write and reads fast; MoR writes fast and pays at read until compaction. Pick by update distribution.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/02-table-formats
- front: What does Iceberg's hidden partitioning fix?
  back: Queries on the source column get pruning, and partition specs can change without a rewrite.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/02-table-formats
- front: What limits time travel?
  back: 'Retention: vacuum or snapshot expiry deletes old files.'
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/02-table-formats
- front: What don't table formats give you?
  back: Multi-table transactions in the usual log-per-table design, a query engine, or data quality on their own.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/02-table-formats
- front: Define a lakehouse.
  back: 'Low-cost, directly accessible open storage with DBMS features: ACID, versioning, indexing, caching, governance.'
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/03-lakehouse-vs-warehouse
- front: What problem does it attack?
  back: 'The two-tier lake-plus-warehouse: duplicated data, staleness, reliability gaps, poor ML access, lock-in.'
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/03-lakehouse-vs-warehouse
- front: What do you give up?
  back: Some data independence, multi-table transactions in log-per-table designs, and native-format performance without extra caching work.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/03-lakehouse-vs-warehouse
- front: How do you read the CIDR 2021 benchmark?
  back: As a vendor-run result showing open formats can be fast enough, and not as proof they are faster for you.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/03-lakehouse-vs-warehouse
- front: When would you still pick a warehouse?
  back: SQL-centred teams, high-concurrency BI, multi-table consistency, and a small platform team.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/03-lakehouse-vs-warehouse
- front: What is the medallion architecture?
  back: Bronze raw, silver conformed, gold aggregates. A convention with no enforcement unless tests are added.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/03-lakehouse-vs-warehouse
- front: Queue or log?
  back: A log retains records and each consumer group keeps an offset, so replay and multiple readers come free.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/04-kafka-and-stream-semantics
- front: What is ordered in Kafka?
  back: Records within a partition; nothing across partitions.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/04-kafka-and-stream-semantics
- front: At-most-once against at-least-once?
  back: Commit before processing loses on crash; commit after processing duplicates on crash.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/04-kafka-and-stream-semantics
- front: What does the idempotent producer solve?
  back: Duplicates from retries, through a producer ID and a per-partition sequence number.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/04-kafka-and-stream-semantics
- front: What does exactly-once mean?
  back: The final effect is as if no fault happened. It holds inside the transactional system. Outside, use idempotent sinks.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/04-kafka-and-stream-semantics
- front: Event or processing time?
  back: Event time for correct windows; processing time for operational rates.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/04-kafka-and-stream-semantics
- front: Why does a stream-table join change on replay?
  back: The local table has moved on since the event. Store the version in force at event time, as a Type 2 dimension does.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/04-kafka-and-stream-semantics
- front: What is a watermark?
  back: A heuristic claim that event time up to T has probably arrived, triggering windows and bounding state.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/04-kafka-and-stream-semantics
- front: Timeliness or integrity?
  back: Timeliness is about how fresh the data is, and heals with waiting. Integrity is about whether it is correct, and does not heal. Streams can give up the first and keep the second.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/04-kafka-and-stream-semantics
- front: What happens to late data?
  back: Dropped and counted, or emitted as a correction downstream if the sink can apply it.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/04-kafka-and-stream-semantics
- front: Main drivers of a warehouse bill?
  back: 'Compute: bytes scanned or slot-hours. Storage is usually small. Egress depends on topology.'
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/05-cost
- front: On-demand or capacity?
  back: On-demand for spiky or small; capacity for steady heavy load. Compute the break-even.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/05-cost
- front: Fastest ways to cut a scan bill?
  back: Select named columns, filter on the partition, cluster the next filter, materialise repeated aggregates.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/05-cost
- front: Does `LIMIT` reduce bytes scanned?
  back: Not on a non-clustered BigQuery table; the same columns are read and billed.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/05-cost
- front: How do you stop cost regressions?
  back: Dry runs or byte limits in CI, job labels and regular review of `INFORMATION_SCHEMA.JOBS`.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/05-cost
- front: Why are small files a cost problem?
  back: Per-file footer and open overhead, more operations, worse compression; compaction fixes it.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/05-cost
---
