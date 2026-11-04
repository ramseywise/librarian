---
imported_hash: 76785288f777b427
decks:
- learn-ai-engineering/data-engineering/01-storage-and-compute-foundations/slides/deck.yaml
cards:
- front: Why does a slow backend hurt more as a request calls more of them?
  back: State latency as percentiles from the client, since the tail reaches most requests that fan out, and percentiles cannot be averaged.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/01-data-systems-and-data-models
- front: Which operation did the relational model make cheap, and which the document model?
  back: Normalised data keeps updates in one place, documents keep reads together, and declarative queries let the engine change the path later.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/01-data-systems-and-data-models
- front: What does read_parquet do with a column only the second file has?
  back: Reading many Parquet files without union_by_name silently drops new columns, which is a stage trusting the one before it.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/02-encoding-and-files
- front: What can a reader skip using only the footer?
  back: Parquet's footer lets a reader skip columns and row groups, but min and max only help when the data's order matches the filter.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/02-encoding-and-files
- front: Why did SQLite's index fall behind on the busy zone?
  back: An index is a series of random lookups, so it loses to a compressed scan as selectivity falls, and warehouses mostly skip them.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/03-row-and-column-stores
- front: What does an LSM-tree pay for its cheap writes?
  back: B-trees update in place and read predictably, and LSM-trees batch writes cheaply but must merge and search several segments on read.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/03-row-and-column-stores
- front: Which level first stops write skew in Postgres?
  back: A level's name tells you little, so ask which anomalies it allows, because in Postgres only serializable stopped write skew and phantoms.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/04-transactions-and-isolation
- front: Why did a transaction with a new id charge twice as much?
  back: Fix lost updates with atomic writes, locks or compare-and-set, and if aborts are possible retry with one id so effects do not repeat.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/04-transactions-and-isolation
- front: When does optimistic concurrency perform badly?
  back: Serializable snapshot isolation runs without blocking and aborts a transaction whose premise changed, so it costs most under contention.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/04-transactions-and-isolation
- front: Which warehouse habit is a write skew waiting to happen?
  back: Pipelines hit the same anomalies as applications, so make one load one commit and do not let concurrent jobs check and write separately.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/04-transactions-and-isolation
- front: What problem does a compound key solve?
  back: Range keeps order at the risk of write hot spots, hash spreads load but fans out, and a compound key gets some of both.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/05-partitioning-and-replication
- front: What is a good rule for choosing lake partition and sort keys?
  back: Partition lake folders by a low-cardinality column you backfill by and sort within files, because too-fine partitions create slow small files.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/05-partitioning-and-replication
- front: How did an autoincrement key get reused in our model?
  back: Asynchronous replication acknowledges writes a failover can lose, and a stale new leader can reuse their keys, so don't trust IDs alone.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/05-partitioning-and-replication
- front: What does a request id let the receiver do?
  back: Plain retries trade lost writes for duplicates, and only an id the receiver checks stops the duplicates.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/06-when-distributed-systems-fail
- front: What does ordering writes by wall clock risk?
  back: Ordering by wall clock across machines silently drops acknowledged writes, so order by a sequence number from one source.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/06-when-distributed-systems-fail
- front: Who rejects the stale writer, and why not the writer itself?
  back: A process can pause at any line and not know it, so the storage must reject stale work using a token that only goes up.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/06-when-distributed-systems-fail
- front: Why can't a prepared participant decide by itself?
  back: Two-phase commit is atomic only by blocking, since a prepared participant must hold its locks until the coordinator's decision arrives.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/07-consistency-and-consensus
- front: What releases a prepared transaction's locks?
  back: A prepared transaction outlives its client and a restart and keeps its locks until someone commits or rolls it back, so a lost coordinator stops others.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/07-consistency-and-consensus
- front: Why is two of five not enough?
  back: Any two majorities share a node, which carries an acknowledged write into each new term, and below a majority the proof and the system both fail.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/07-consistency-and-consensus
- front: How does MapReduce make retries safe?
  back: MapReduce partitions keys with a stable hash, sorts and merges them, and commits output atomically so a retry cannot double count.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/08-distributed-compute
- front: Why test one machine before a cluster?
  back: DuckDB and Polars plan queries like a cluster engine and can work beyond memory, so test one machine first.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/08-distributed-compute
- front: Which rung covers your own bad DELETE, and why not a replica?
  back: A replica copies your mistakes in milliseconds, so your own bad DELETE needs point-in-time recovery from a backup you have restored.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/09-persistence
- front: What does synchronous replication pay for losing nothing on failover?
  back: Synchronous replication lost nothing but acknowledged nothing during a 1 s standby stall, while asynchronous kept committing and lost 15,620 rows.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/09-persistence
- front: Why did the same 2,000,000 rows favour SQLite on one query and DuckDB on another?
  back: A store is a bet on how data is read and written, so row-oriented SQLite won the lookup and columnar DuckDB won the scan, with neither the better database.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/10-choosing-a-store
- front: When does plain Postgres stop being enough?
  back: Postgres cleared these bars on one laptop, and stops being enough when writes exceed one primary, scans cover most of a large table, or search is the product.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/10-choosing-a-store
- front: In this worked app, which need forces a store beyond Postgres, and why?
  back: Scanning 500 million order lines is the one need that forces a different store, and search can move out later, once relevance becomes a project of its own.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/10-choosing-a-store
- front: Which mechanisms do most data engineering debates reduce to?
  back: Most data engineering debates reduce to layout, isolation, faults and shuffles, so learn these mechanisms and measure before you decide.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/08-distributed-compute
- front: Which pillar builds on these mechanisms first?
  back: Later pillars rely on these mechanisms, starting with how to extract from a lagging source and model what arrives.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/08-distributed-compute
---
