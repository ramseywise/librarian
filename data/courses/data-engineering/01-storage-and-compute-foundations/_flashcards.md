---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- data-engineering/01-storage-and-compute-foundations/slides/deck.yaml
cards:
- front: In what order does this lecture add trouble to the one-machine system?
  back: The lecture adds one kind of trouble at a time, so each later mechanism can be read as the answer to the failure before it.
  lesson: data-engineering/01-storage-and-compute-foundations/readme
- front: Name four things this lecture teaches you to do with a data system.
  back: You will be able to say what a data system promises, which failure breaks that promise, and what it costs to keep it.
  lesson: data-engineering/01-storage-and-compute-foundations/readme
- front: Why does a slow backend hurt more as a request calls more of them?
  back: State latency as percentiles from the client, since the tail reaches most requests that fan out, and percentiles cannot be averaged.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/01-data-systems-and-data-models
- front: Which operation did the relational model make cheap, and which the document model?
  back: Normalised data keeps updates in one place, documents keep reads together, and declarative queries let the engine change the path later.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/01-data-systems-and-data-models
- front: Why do a mean latency, an averaged percentile and a closed-loop test all mislead?
  back: A mean, an averaged percentile and a closed-loop test each report a number that describes no real user.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/01-data-systems-and-data-models
- front: What can a reader skip using only the footer?
  back: Parquet's footer lets a reader skip columns and row groups, but min and max only help when the data's order matches the filter.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/02-encoding-and-files
- front: What does read_parquet do with a column only the second file has?
  back: Reading many Parquet files without union_by_name silently drops new columns, which is a stage trusting the one before it.
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
- front: Who rejects the stale writer, and why not the writer itself?
  back: A process can pause at any line and not know it, so the storage must reject stale work using a token that only goes up.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/06-when-distributed-systems-fail
- front: What does ordering writes by wall clock risk?
  back: Ordering by wall clock across machines silently drops acknowledged writes, so order by a sequence number from one source.
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
- front: Why is a slow reducer usually not a slow machine?
  back: Cluster jobs fail as wrong totals, duplicate writes or one slow task, so check the key, the output path and the bytes read before adding workers.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/08-distributed-compute
- front: Which rung covers your own bad DELETE, and why not a replica?
  back: A replica copies your mistakes in milliseconds, so your own bad DELETE needs point-in-time recovery from a backup you have restored.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/09-persistence
- front: What does synchronous replication pay for losing nothing on failover?
  back: Synchronous replication lost nothing but acknowledged nothing during a 1 s standby stall, while asynchronous kept committing and lost 15,620 rows.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/09-persistence
- front: Why does a replica or kill -9 not prove your data is safe?
  back: Replicas cover hardware and backups cover people, so say which failure you tested and which one you survive.
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
- front: Fault vs failure?
  back: A fault is one component deviating from spec. A failure is the whole system ceasing to serve its users. Design stops faults becoming failures, including by injecting them on purpose.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/01-data-systems-and-data-models
- front: Which faults are worst?
  back: Correlated software faults, since redundancy does not help, and human configuration errors, which lead outage causes.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/01-data-systems-and-data-models
- front: Why percentiles rather than a mean?
  back: Response time is a distribution with a long tail. The mean describes nobody, and p99 tracks what the unlucky users actually see.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/01-data-systems-and-data-models
- front: How do you combine percentiles across servers?
  back: Add the histograms. Averaging percentiles has no statistical meaning.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/01-data-systems-and-data-models
- front: What is tail latency amplification?
  back: When a request needs many backend calls, it waits for the slowest. At 100 calls, 63% of requests experience some call slower than its p99.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/01-data-systems-and-data-models
- front: What is coordinated omission?
  back: A closed-loop load generator stops sending during a stall, so it fails to record the requests that would have queued, and tail percentiles look healthy.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/01-data-systems-and-data-models
- front: Twitter's fan-out problem?
  back: Fan-out on write makes reads cheap, but a very large account means millions of writes per tweet. A hybrid handles the largest accounts at read time.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/01-data-systems-and-data-models
- front: Document vs relational?
  back: Documents suit self-contained trees read as a unit. Relational suits many-to-one and many-to-many data, since each fact is stored once and joins live in the database.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/01-data-systems-and-data-models
- front: Schema-on-read vs schema-on-write?
  back: Whether structure is implicit in readers or enforced on write. Lakes use read at the raw layer and write from the first transform.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/01-data-systems-and-data-models
- front: What does declarative buy?
  back: The engine can change the access path, parallelise and reorder without the query changing. An index or a new storage layer speeds up existing SQL.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/01-data-systems-and-data-models
- front: System of record vs derived data?
  back: Records hold the authoritative facts. Derived data can be deleted and rebuilt. Knowing which is which decides what a bad day costs.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/01-data-systems-and-data-models
- front: Backward vs forward compatibility?
  back: 'Backward: new code reads old data. Forward: old code reads new data. Warehouses need both because files outlive code and rollouts are never atomic.'
  lesson: data-engineering/01-storage-and-compute-foundations/notes/02-encoding-and-files
- front: Why not CSV in a pipeline?
  back: No types, loose escaping, and every read parses the whole file. Fine for exchange; read it once with a stated schema and convert.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/02-encoding-and-files
- front: Avro vs Protobuf?
  back: Protobuf puts numbered tags in the data, good for hand-managed service APIs. Avro has no tags and resolves writer and reader schemas by name, good for generated schemas and streams.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/02-encoding-and-files
- front: What is in a Parquet footer?
  back: The schema, row group locations, and per-chunk encoding, sizes and min and max statistics. Readers fetch it first and then only the byte ranges they need.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/02-encoding-and-files
- front: Column pruning vs predicate pushdown?
  back: Pruning skips columns not named. Pushdown skips row groups whose statistics rule out the filter. Pushdown depends on physical sort order.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/02-encoding-and-files
- front: Parquet vs Arrow?
  back: Parquet is compressed for storage, so it saves I/O at a CPU cost. Arrow is uncompressed for memory, so it gives random access and zero-copy exchange. They complement each other.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/02-encoding-and-files
- front: Why can a sort make a Parquet file larger?
  back: Only one order can be physical. Runs in the sort key compress better, but a column that was in order before may lose its delta and dictionary savings.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/02-encoding-and-files
- front: How does a Kafka consumer find an Avro schema?
  back: Each message carries a schema ID, resolved through a schema registry, which also rejects incompatible changes.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/02-encoding-and-files
- front: OLTP vs OLAP?
  back: OLTP does small reads and writes by key for applications. OLAP does large scans and aggregates over history for analysis. Their access patterns need different storage.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/03-row-and-column-stores
- front: Why are column stores fast for analytics?
  back: They read only the named columns, compress similar values well, skip blocks by min and max, and use vectorised execution with tight loops over columns.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/03-row-and-column-stores
- front: Can a row store emulate one with narrow tables?
  back: Not effectively, as Abadi et al. (SIGMOD 2008) showed. Tuple reconstruction and per-row overhead dominate, and the executor must also be built for columns.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/03-row-and-column-stores
- front: B-tree vs LSM-tree?
  back: B-trees update fixed pages in place and write a log first, so reads are cheap and each key has one home. LSM-trees append sorted segments and merge them later, so writes are cheap, reads may open several segments and compaction can hurt tail latency.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/03-row-and-column-stores
- front: What is late materialisation?
  back: Keeping columns separate through the query and building rows only when necessary. Abadi et al. measured about a factor of three.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/03-row-and-column-stores
- front: Why do warehouses avoid secondary indexes?
  back: Each match is a random lookup, which loses to a scan as selectivity falls. Sort order and block statistics deliver most of the benefit without slowing writes.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/03-row-and-column-stores
- front: How do column stores handle writes?
  back: Recent writes go to an in-memory or row-oriented store and are merged into compressed columns in bulk. Reads combine both.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/03-row-and-column-stores
- front: Materialised view vs cube?
  back: A view stores one query's result. A cube precomputes aggregates over combinations of dimensions. Both are fast, and both are limited to the dimensions they kept.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/03-row-and-column-stores
- front: What are vectorised and compiled execution?
  back: Vectorised engines run interpreted operators over batches of values. Compiled engines generate code per query. DuckDB chose vectors, citing portability.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/03-row-and-column-stores
- front: What does the A in ACID really mean?
  back: Abortability. If a group of writes cannot finish, they are all discarded, so the client can safely retry. It says nothing about concurrency.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/04-transactions-and-isolation
- front: What does the C mean?
  back: Application invariants. The database can check some through constraints, but it is the application's property, unlike A, I and D.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/04-transactions-and-isolation
- front: Read committed vs snapshot isolation?
  back: Read committed takes a new snapshot per statement, so a transaction can see different states (read skew). Snapshot isolation fixes one snapshot for the whole transaction.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/04-transactions-and-isolation
- front: How does MVCC work?
  back: An update creates a new row version and marks the old one deleted, tagged with transaction IDs. Readers pick the version visible to their snapshot, so readers and writers do not block one another.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/04-transactions-and-isolation
- front: What is a lost update, and how do you stop it?
  back: Two read-modify-write cycles where the later overwrites the earlier. Use an atomic update, `SELECT FOR UPDATE`, compare-and-set, or automatic detection under snapshot isolation.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/04-transactions-and-isolation
- front: What is write skew?
  back: Two transactions read the same data, then write different rows, and together break an invariant neither broke alone. Snapshot isolation allows it. Use serializable, explicit locks or a constraint.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/04-transactions-and-isolation
- front: What is a phantom?
  back: A write that changes the result of another transaction's search. Locks cannot help when the row does not exist yet, so use a constraint or serializable.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/04-transactions-and-isolation
- front: Name the three ways to get serializability.
  back: Actual serial execution, two-phase locking, and serializable snapshot isolation. They trade throughput limits, blocking and tail latency, and aborts under contention.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/04-transactions-and-isolation
- front: 2PL vs SSI?
  back: 2PL is pessimistic and blocks readers and writers. SSI is optimistic, lets them run, and aborts at commit if a premise has been invalidated.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/04-transactions-and-isolation
- front: Why might a retry charge twice?
  back: The commit can succeed with the acknowledgement lost. Store a unique request ID in the same transaction so the retry does nothing.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/04-transactions-and-isolation
- front: What does this have to do with a table format?
  back: A commit is a compare-and-set on a pointer to an immutable snapshot, which gives multi-version reads and optimistic writers at file scale, so a retry on conflict is normal.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/04-transactions-and-isolation
- front: Partitioning vs replication?
  back: Partitioning splits data so no node has it all, for scale. Replication copies data so that a node can fail, for availability. Most systems do both.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/05-partitioning-and-replication
- front: Range vs hash partitioning?
  back: Range keeps order and supports range scans, but sequential keys cause write hot spots. Hash spreads evenly and forces range queries to fan out. Compound keys mix both.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/05-partitioning-and-replication
- front: Why not `hash mod N`?
  back: Adding a node moves most keys. Use many fixed partitions and move whole partitions instead.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/05-partitioning-and-replication
- front: How do you handle a hot key?
  back: Add a random suffix to split writes across many keys and combine them on read, only for the keys that need it.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/05-partitioning-and-replication
- front: Local vs global secondary index?
  back: Local has fast writes and scatter-gather reads. Global has targeted reads and slower, often asynchronous, writes.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/05-partitioning-and-replication
- front: Sync vs async replication?
  back: Sync guarantees the follower is current but blocks when it stalls. Async keeps writing but can lose acknowledged writes on failover. Semi-sync makes one follower synchronous.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/05-partitioning-and-replication
- front: What are read-your-writes, monotonic reads and consistent prefix?
  back: 'Respectively: you see your own write; time does not go backwards across reads; causally ordered writes appear in order. All can fail under replication lag.'
  lesson: data-engineering/01-storage-and-compute-foundations/notes/05-partitioning-and-replication
- front: What does `w + r > n` mean, and what doesn't it?
  back: 'Read and write sets overlap, so a read should touch the latest write. It does not provide linearisability: sloppy quorums and last-write-wins can break it.'
  lesson: data-engineering/01-storage-and-compute-foundations/notes/05-partitioning-and-replication
- front: Why does CDC read the logical log?
  back: Row-based logs are decoupled from the storage format and record exact changes, so external tools can parse them and replay them in order.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/05-partitioning-and-replication
- front: What is a partial failure?
  back: Some parts of a system are broken while others work, nondeterministically, so an operation may or may not have taken effect.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/06-when-distributed-systems-fail
- front: What does a timeout tell you?
  back: Nothing about the outcome. The request may be lost, or the server dead, or the work done and the reply lost.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/06-when-distributed-systems-fail
- front: How do you choose a timeout?
  back: Measure the round-trip distribution. Short gives false positives and duplicate work, long gives slow detection. Adaptive detectors like phi accrual automate this.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/06-when-distributed-systems-fail
- front: Time-of-day clock vs monotonic clock?
  back: Time-of-day is comparable across machines but can jump. Monotonic only goes forward, so it suits durations, but is meaningless elsewhere.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/06-when-distributed-systems-fail
- front: Why is last-write-wins dangerous?
  back: It uses timestamps from unsynchronised clocks and drops acknowledged writes without an error. Skew of a few milliseconds is enough.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/06-when-distributed-systems-fail
- front: Why can't you just check your lease before writing?
  back: The process can pause between the check and the write for an arbitrary time, so the check may be stale by the time you act.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/06-when-distributed-systems-fail
- front: What is a fencing token?
  back: A number that increases with each lock grant. The resource rejects a write with a token lower than one it has seen, which stops a zombie.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/06-when-distributed-systems-fail
- front: What is a zombie task?
  back: An attempt declared dead that is actually still running. It needs a commit protocol or fencing so that it cannot overwrite the retry.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/06-when-distributed-systems-fail
- front: Why an odd number of nodes?
  back: A majority of 4 is 3 and tolerates 1, the same as 3 nodes. Two majorities must overlap, which prevents split decisions.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/06-when-distributed-systems-fail
- front: Safety vs liveness?
  back: 'Safety: nothing bad ever happens, and it can be violated at a point in time. Liveness: something good eventually happens. Keep safety always, and let liveness wait for recovery.'
  lesson: data-engineering/01-storage-and-compute-foundations/notes/06-when-distributed-systems-fail
- front: What is a Byzantine fault, and do you need to handle it?
  back: A node that sends arbitrary or malicious messages. Generally not within one organisation's datacenter, but do use checksums and sanity checks for weak forms.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/06-when-distributed-systems-fail
- front: What is linearizability?
  back: The system behaves as if there were one copy of the data, and every operation takes effect atomically at a point in time. Once a new value has been read, no later read returns an older one.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/07-consistency-and-consensus
- front: Linearizable vs serializable?
  back: Linearizable is a real-time recency guarantee on one object. Serializable is an isolation guarantee on transactions, in some order. Both together are strict serializability.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/07-consistency-and-consensus
- front: What does CAP actually say?
  back: When a network partition occurs, you choose between linearizability and availability. Partitions aren't optional, so "pick two" misleads.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/07-consistency-and-consensus
- front: Why do systems give up linearizability?
  back: Mostly for performance. It requires waiting on the network, and response time is at least proportional to the delay uncertainty.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/07-consistency-and-consensus
- front: What is a Lamport timestamp?
  back: A `(counter, node)` pair, where a node takes the max on receipt. It gives a total order consistent with causality, but only after the fact.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/07-consistency-and-consensus
- front: Why isn't a Lamport timestamp enough for a uniqueness check?
  back: The order is only final after hearing from every node, so a node can't decide at request time.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/07-consistency-and-consensus
- front: What is total order broadcast?
  back: Reliable delivery of messages to all nodes in the same order, fixed at delivery. In practice it is a replicated log, and it is equivalent to consensus.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/07-consistency-and-consensus
- front: Explain 2PC.
  back: A coordinator asks participants to prepare, each votes and promises, the coordinator logs a decision, and it delivers that decision. A participant that voted yes is stuck until it hears.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/07-consistency-and-consensus
- front: What is an in-doubt transaction?
  back: One that voted yes and hasn't heard the decision. It holds locks, and survives restarts, until the decision arrives or an admin resolves it.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/07-consistency-and-consensus
- front: How does consensus improve on 2PC?
  back: It needs a majority rather than everyone, elects a replacement leader, and is designed to terminate while a majority is up.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/07-consistency-and-consensus
- front: How does an old leader get stopped?
  back: Each election uses a higher term, and nodes refuse lower terms. An old leader can't reach a majority, and so can't commit.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/07-consistency-and-consensus
- front: How does Airflow stop two schedulers doing the same thing?
  back: Row locks in its metadata database, not a consensus algorithm between schedulers. Agreement is delegated to the database.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/07-consistency-and-consensus
- front: Walk through MapReduce.
  back: Map emits key-value pairs. The framework partitions by hash of key, sorts, and copies them to reducers (the shuffle). Reduce handles all values for one key. Output is committed atomically.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/08-distributed-compute
- front: Why is the shuffle the bottleneck?
  back: It moves data across the network and sorts it, and nearly every join and group-by needs one. Reducing it is most of tuning.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/08-distributed-compute
- front: What did Spark change?
  back: It runs the whole workflow as one job, keeps intermediate data in memory or on local disk, and recovers via lineage rather than replicated intermediate files.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/08-distributed-compute
- front: What is lineage, and what does it need?
  back: The record of transformations that built a partition, used to recompute it. It needs deterministic operators.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/08-distributed-compute
- front: Broadcast vs sort-merge join?
  back: Broadcast copies a small table to every worker, with no shuffle of the large table. Sort-merge shuffles both sides by key, and is the general fallback.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/08-distributed-compute
- front: How do you handle skew?
  back: Find the hot keys, then salt them and aggregate in two stages, or broadcast the small side. Adaptive execution can split skewed partitions.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/08-distributed-compute
- front: What is COST?
  back: The hardware configuration needed before a system beats a competent single thread (McSherry et al., HotOS 2015). Some systems never do.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/08-distributed-compute
- front: When would you not use Spark?
  back: When the query's input after pruning fits on one large machine. DuckDB or Polars are simpler and cheaper, and each can spill.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/08-distributed-compute
- front: A write returned success. Where is the data?
  back: 'It depends on the rung: process buffer, page cache, device, replica, or backup. Each survives a different failure, so ask which failure you must survive.'
  lesson: data-engineering/01-storage-and-compute-foundations/notes/09-persistence
- front: Difference between `flush` and `fsync`?
  back: '`flush` moves data from the process to the OS and survives a process crash. `fsync` asks the OS to push it to the device, which is what a power cut requires, assuming the drive honours it.'
  lesson: data-engineering/01-storage-and-compute-foundations/notes/09-persistence
- front: RPO versus RTO?
  back: RPO is how much data you can lose, measured in time. RTO is how long you can be down. They are set by business cost and bought separately.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/09-persistence
- front: Why does a WAL make commits faster?
  back: One sequential append and sync replaces many random page writes. Pages follow later, and replay rebuilds them after a crash. One sync can also commit many transactions.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/09-persistence
- front: '`synchronous_commit = off` versus `fsync = off`?'
  back: The first can lose recent commits but stays consistent. The second can corrupt the database and is only for data you can rebuild.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/09-persistence
- front: Async or sync replication?
  back: Async can lose the lag on failover. Sync loses nothing acknowledged, but commits stop if the standby stalls. It's a choice between RPO and availability.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/09-persistence
- front: Is a replica a backup?
  back: No. It copies deletes in milliseconds. You need point-in-time recovery from a retained backup.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/09-persistence
- front: What does eleven nines cover?
  back: The provider losing your object, not you overwriting it. Versioning and Object Lock cover that.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/09-persistence
- front: What makes something a cache rather than a source of truth?
  back: You can delete it and rebuild it from elsewhere. Write-behind breaks that for its flush window.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/09-persistence
- front: How do you choose a database?
  back: 'Start with access patterns: how records are found, how much one query touches, how data changes, size and who operates it. Then match a store.'
  lesson: data-engineering/01-storage-and-compute-foundations/notes/10-choosing-a-store
- front: When is Postgres enough?
  back: Usually, until writes outgrow one primary, or you need scans over most of a huge table, multi-region writes, or search as a product.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/10-choosing-a-store
- front: Key-value versus document?
  back: Key-value stores an opaque value read by key. A document store understands the value's fields, so it can index and query them.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/10-choosing-a-store
- front: Is Cassandra a column store?
  back: No. Wide-column means rows with flexible columns under a partition key. It's built for writes by key, not scans.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/10-choosing-a-store
- front: Do you need a vector database?
  back: 'Not for small corpora: exact search over a million vectors took about 17 ms here. Above that, an index in your existing database is the next step, then a dedicated store.'
  lesson: data-engineering/01-storage-and-compute-foundations/notes/10-choosing-a-store
- front: Why not use Elasticsearch as the primary store?
  back: It is refreshed periodically and is built as a derived index. Keep the record elsewhere and rebuild from it.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/10-choosing-a-store
- front: Snowflake versus Airflow?
  back: They don't compete. Snowflake stores and computes; Airflow schedules. Compare warehouses with warehouses and orchestrators with orchestrators.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/10-choosing-a-store
- front: What does a new store really cost?
  back: Backups, upgrades, monitoring, on-call and hiring, and a new set of failure modes on top of the licence.
  lesson: data-engineering/01-storage-and-compute-foundations/notes/10-choosing-a-store
---
