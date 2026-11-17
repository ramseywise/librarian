---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- data-engineering/02-ingest-and-modelling/slides/deck.yaml
cards:
- front: In what order does this lecture take data from a source to a checked promise?
  back: Each step turns something a later stage would trust silently into an agreement that can be checked.
  lesson: data-engineering/02-ingest-and-modelling/readme
- front: Name four things this lecture teaches you to do with a source of data.
  back: You will be able to load data safely, say what a row means, and write down what the next stage may rely on.
  lesson: data-engineering/02-ingest-and-modelling/readme
- front: What happens without the BEGIN if the insert fails?
  back: Delete and insert one window in one transaction, so a re-run replaces data and a crash leaves it untouched.
  lesson: data-engineering/02-ingest-and-modelling/notes/01-ingest
- front: Which two changes did the watermark miss?
  back: A watermark misses deletes and late updates, while a change log carries both, at the cost of access and operations.
  lesson: data-engineering/02-ingest-and-modelling/notes/01-ingest
- front: Why take the snapshot at a known log position?
  back: CDC starts from a snapshot at a known log position, then applies changes in order and stores the position so a replay is harmless.
  lesson: data-engineering/02-ingest-and-modelling/notes/01-ingest
- front: When is batch still the right answer?
  back: Pick the simplest method whose blind spots the data can tolerate, and write down what it cannot see.
  lesson: data-engineering/02-ingest-and-modelling/notes/01-ingest
- front: Why does the grain come before the dimensions?
  back: Pick a process, state the grain in one sentence at the atomic level, and only then choose dimensions and facts true to it.
  lesson: data-engineering/02-ingest-and-modelling/notes/02-dimensional-modelling
- front: What would an inner join have done to those 2187 trips?
  back: Load facts with left joins to a default row, so totals reconcile and each gap is a row someone can count.
  lesson: data-engineering/02-ingest-and-modelling/notes/02-dimensional-modelling
- front: Why did revenue change with no error raised?
  back: A join to anything finer than the fact silently multiplies it, so roll up first and test key uniqueness after each join.
  lesson: data-engineering/02-ingest-and-modelling/notes/02-dimensional-modelling
- front: Which aggregate does Kimball insist on for ratios?
  back: Store the numerator and denominator of a ratio and compute it at query time, so nobody can add it up by accident.
  lesson: data-engineering/02-ingest-and-modelling/notes/02-dimensional-modelling
- front: Which type changes numbers you already published?
  back: Type 1 rewrites published history, Type 2 preserves it with a new key, and Type 3 keeps a single prior value.
  lesson: data-engineering/02-ingest-and-modelling/notes/02b-dimensional-modelling-history-and-conformed-dimensions
- front: Why does the fact query need no date condition?
  back: With Type 2 the fact keeps the key in force at event time, and joining through the natural key restates history to today.
  lesson: data-engineering/02-ingest-and-modelling/notes/02b-dimensional-modelling-history-and-conformed-dimensions
- front: What does drilling across do differently?
  back: Aggregate each fact to its shared conformed dimensions first and then join the results, because a direct join multiplies both sides.
  lesson: data-engineering/02-ingest-and-modelling/notes/02b-dimensional-modelling-history-and-conformed-dimensions
- front: What does adding a new source of zone attributes cost?
  back: A vault makes a new source cost one new table and keeps every version, and in exchange readers need marts built on top.
  lesson: data-engineering/02-ingest-and-modelling/notes/03-data-vault-and-obt
- front: Why is this evidence about reads and not a verdict?
  back: On one public TPC-DS benchmark a wide table read 25-50% faster, on ten chosen queries, with a vendor-published setup you should re-test.
  lesson: data-engineering/02-ingest-and-modelling/notes/03-data-vault-and-obt
- front: Why does object storage make this worse?
  back: A wide table copies each label into every row, so one change rewrites rows or files, and a second grain needs a second table.
  lesson: data-engineering/02-ingest-and-modelling/notes/03-data-vault-and-obt
- front: What makes a wide table stop being a cache?
  back: Keep definitions in a star and treat wide tables as caches, and add a vault only when sources and auditors demand it.
  lesson: data-engineering/02-ingest-and-modelling/notes/03-data-vault-and-obt
- front: What does this hold that a schema does not?
  back: A contract adds meaning, quality rules, service levels and an owner to a schema, in a format that tools can validate and enforce.
  lesson: data-engineering/02-ingest-and-modelling/notes/04-data-contracts
- front: Why does the checker test structure first?
  back: Check structure first and content second, and name the column and promise in every breach so the owner can act on it.
  lesson: data-engineering/02-ingest-and-modelling/notes/04-data-contracts
- front: Why is nothing loaded better than something wrong?
  back: Stop when the batch itself is suspect and quarantine isolated rows, using a threshold the business sets, and always reconcile counts.
  lesson: data-engineering/02-ingest-and-modelling/notes/04-data-contracts
- front: Which step needs sign-off, and why is it then harmless?
  back: Add the new field and write both, move consumers before a deadline, and only then remove the old field in a new major version.
  lesson: data-engineering/02-ingest-and-modelling/notes/04-data-contracts
- front: Why is a schema that calls itself a contract only an automated DESCRIBE?
  back: A contract needs meaning, an owner and a check at the boundary, or bad data still loads and nobody is responsible for it.
  lesson: data-engineering/02-ingest-and-modelling/notes/04-data-contracts
- front: What should each stage state, so that failures become visible?
  back: Each stage should state what it will not trust, in keys, default rows, history and contracts, so that failures become visible.
  lesson: data-engineering/02-ingest-and-modelling/notes/04-data-contracts
- front: Which pillar turns these models into scheduled builds?
  back: Pillar 3 builds these models with dbt and schedules them, so that everything agreed here is tested on every run.
  lesson: data-engineering/02-ingest-and-modelling/notes/04-data-contracts
- front: What makes a load idempotent?
  back: Re-running it gives the same end state. Replace a whole window in a transaction, or merge on a key.
  lesson: data-engineering/02-ingest-and-modelling/notes/01-ingest
- front: A retry doubled a table. Why, and how do you fix it?
  back: An append ran twice after a timeout. Fix the loader by replacing a window, then rebuild the affected days.
  lesson: data-engineering/02-ingest-and-modelling/notes/01-ingest
- front: What can a high watermark miss?
  back: Rows committed after the mark with an earlier timestamp, rows skipped by bulk updates, and every hard delete.
  lesson: data-engineering/02-ingest-and-modelling/notes/01-ingest
- front: How does an overlap help, and what does it cost?
  back: It re-reads a window behind the mark, and the merge removes duplicates. It costs extra reads and only covers commits within its width.
  lesson: data-engineering/02-ingest-and-modelling/notes/01-ingest
- front: What is CDC?
  back: Reading the database's change log and publishing each change in order, so that other systems act as followers.
  lesson: data-engineering/02-ingest-and-modelling/notes/01-ingest
- front: Why does CDC need a snapshot?
  back: Logs are truncated, so you need a consistent copy tied to a log position, and then you apply everything after it.
  lesson: data-engineering/02-ingest-and-modelling/notes/01-ingest
- front: How do you make CDC application idempotent?
  back: Store the log position with each row, keep tombstones for deletes, and ignore events not newer than what is stored.
  lesson: data-engineering/02-ingest-and-modelling/notes/01-ingest
- front: Batch or stream by default?
  back: Batch, unless a named consumer needs the freshness and can justify running brokers.
  lesson: data-engineering/02-ingest-and-modelling/notes/01-ingest
- front: What does dlt give you, and what doesn't it?
  back: State, schema evolution, normalisation and merge. Its incremental cursor is still a watermark, so it cannot see hard deletes.
  lesson: data-engineering/02-ingest-and-modelling/notes/01-ingest
- front: What are the steps of dimensional design?
  back: Business process, grain, dimensions, facts, in that order. The grain sentence decides what the others may contain.
  lesson: data-engineering/02-ingest-and-modelling/notes/02-dimensional-modelling
- front: What is a surrogate key and why use one?
  back: A warehouse-owned meaningless integer. It buffers from source key changes and recycling, and it lets one natural key have several history rows.
  lesson: data-engineering/02-ingest-and-modelling/notes/02-dimensional-modelling
- front: How do you handle a fact whose dimension is unknown?
  back: Point it at a default row such as key -1 rather than dropping it, so totals reconcile and the gap can be counted.
  lesson: data-engineering/02-ingest-and-modelling/notes/02-dimensional-modelling
- front: What is a degenerate dimension?
  back: A key in the fact with no dimension table, such as an order number. It is useful for grouping lines and tracing to the source.
  lesson: data-engineering/02-ingest-and-modelling/notes/02-dimensional-modelling
- front: Additive, semi-additive, non-additive?
  back: Sums across all dimensions, across some but not time, and across none. Store the parts of a ratio and compute it at query time.
  lesson: data-engineering/02-ingest-and-modelling/notes/02-dimensional-modelling
- front: Why did a join inflate revenue?
  back: A grain mismatch fanned out the fact. Roll up the finer table first or model it as its own fact, and test key uniqueness after joins.
  lesson: data-engineering/02-ingest-and-modelling/notes/02-dimensional-modelling
- front: Transaction, periodic and accumulating snapshot?
  back: One row per event, per entity and period, or per process instance updated at milestones.
  lesson: data-engineering/02-ingest-and-modelling/notes/02-dimensional-modelling
- front: SCD Types 1, 2, 3?
  back: Overwrite and lose history; new row with new key and full history; new column with one prior value. Chosen per attribute.
  lesson: data-engineering/02-ingest-and-modelling/notes/02b-dimensional-modelling-history-and-conformed-dimensions
- front: Why does Type 2 need no change to fact queries?
  back: The fact row holds the surrogate key of the version in force at event time, so a plain key join gives history as it was.
  lesson: data-engineering/02-ingest-and-modelling/notes/02b-dimensional-modelling-history-and-conformed-dimensions
- front: How do you restate Type 2 history to current values?
  back: Join through the natural key to the row with `is_current`.
  lesson: data-engineering/02-ingest-and-modelling/notes/02b-dimensional-modelling-history-and-conformed-dimensions
- front: How do you load a late-arriving fact?
  back: Look up the dimension by event date within the validity range, use that key, write into the correct partition.
  lesson: data-engineering/02-ingest-and-modelling/notes/02b-dimensional-modelling-history-and-conformed-dimensions
- front: What is a conformed dimension?
  back: One dimension shared across facts with identical meaning, the basis for comparing processes.
  lesson: data-engineering/02-ingest-and-modelling/notes/02b-dimensional-modelling-history-and-conformed-dimensions
- front: How do you combine two facts?
  back: 'Drill across: aggregate each to the shared dimensions separately, then join the results.'
  lesson: data-engineering/02-ingest-and-modelling/notes/02b-dimensional-modelling-history-and-conformed-dimensions
- front: What are hubs, links and satellites?
  back: Business keys, relationships between keys, and descriptive history, with every table insert-only.
  lesson: data-engineering/02-ingest-and-modelling/notes/03-data-vault-and-obt
- front: What does a vault buy you?
  back: Adding a source or rule costs a new table, plus loads simple enough to generate and a full audit trail.
  lesson: data-engineering/02-ingest-and-modelling/notes/03-data-vault-and-obt
- front: What does it cost?
  back: Several joins per attribute, so readers need marts, and point-in-time tables for speed.
  lesson: data-engineering/02-ingest-and-modelling/notes/03-data-vault-and-obt
- front: When would you use one?
  back: Many overlapping changing sources with an audit obligation. Not for a small team.
  lesson: data-engineering/02-ingest-and-modelling/notes/03-data-vault-and-obt
- front: Why did OBT become viable?
  back: 'Columnar storage: repeated values compress well and unread columns cost no I/O.'
  lesson: data-engineering/02-ingest-and-modelling/notes/03-data-vault-and-obt
- front: How much faster is OBT?
  back: On Kaminsky's TPC-DS subset, 25-50% depending on the warehouse, with some simple queries favouring the star.
  lesson: data-engineering/02-ingest-and-modelling/notes/03-data-vault-and-obt
- front: What is OBT's main weakness?
  back: A label change rewrites every affected row or file, and there is no room for a second grain.
  lesson: data-engineering/02-ingest-and-modelling/notes/03-data-vault-and-obt
- front: What default would you recommend?
  back: Raw, then star for definitions, then wide tables as disposable outputs where read speed or ease matters.
  lesson: data-engineering/02-ingest-and-modelling/notes/03-data-vault-and-obt
- front: Can you keep history in OBT?
  back: Only as whatever was joined at build time, or by duplicating columns, so it usually means keeping dimensions.
  lesson: data-engineering/02-ingest-and-modelling/notes/03-data-vault-and-obt
- front: What is a data contract?
  back: An enforced agreement between producer and consumers covering structure, meaning, quality, service levels and ownership.
  lesson: data-engineering/02-ingest-and-modelling/notes/04-data-contracts
- front: How does it differ from a schema?
  back: A schema covers structure only. A units change passes any schema.
  lesson: data-engineering/02-ingest-and-modelling/notes/04-data-contracts
- front: Where do you enforce it?
  back: In producer CI for changes, at the boundary for each batch, and in monitoring for what rules cannot foresee.
  lesson: data-engineering/02-ingest-and-modelling/notes/04-data-contracts
- front: What is ODCS?
  back: The Open Data Contract Standard from Bitol, a YAML format with a published JSON Schema, covering schema, quality, SLAs and team.
  lesson: data-engineering/02-ingest-and-modelling/notes/04-data-contracts
- front: What counts as a breaking change?
  back: Removing or renaming a column, changing a type, making something required, removing a guarantee. Adding an optional column is safe.
  lesson: data-engineering/02-ingest-and-modelling/notes/04-data-contracts
- front: How do you ship a breaking change?
  back: 'Expand and contract: add new, write both, migrate consumers with a deadline, then drop the old in a new major version.'
  lesson: data-engineering/02-ingest-and-modelling/notes/04-data-contracts
- front: Stop or quarantine?
  back: Stop when the batch as a whole is suspect. Quarantine isolated rows with a reason. Set a threshold between them and reconcile the counts.
  lesson: data-engineering/02-ingest-and-modelling/notes/04-data-contracts
- front: How do you catch dollars becoming cents?
  back: A semantic rule, range or distribution. Type checks cannot see it.
  lesson: data-engineering/02-ingest-and-modelling/notes/04-data-contracts
- front: How do you get contracts adopted?
  back: Start with the few critical datasets, make the check easy for producers in CI, and get a mandate from whoever owns both teams.
  lesson: data-engineering/02-ingest-and-modelling/notes/04-data-contracts
- front: What about third-party sources?
  back: Apply the same checks on arrival as a one-sided contract. It cannot bind them, though it does protect you.
  lesson: data-engineering/02-ingest-and-modelling/notes/04-data-contracts
- front: Should contracts be hand-written or inferred?
  back: Breck reports inferring the first schema and curating it as it evolves, since many pipelines start with no schema. Either way a human reviews the semantics.
  lesson: data-engineering/02-ingest-and-modelling/notes/04-data-contracts
---
