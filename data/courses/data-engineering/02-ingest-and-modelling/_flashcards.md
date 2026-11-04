---
imported_hash: 1cedba55f63c4a7c
decks:
- learn-ai-engineering/data-engineering/02-ingest-and-modelling/slides/deck.yaml
cards:
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
  lesson: data-engineering/02-ingest-and-modelling/notes/02-dimensional-modelling
- front: Why does the fact query need no date condition?
  back: With Type 2 the fact keeps the key in force at event time, and joining through the natural key restates history to today.
  lesson: data-engineering/02-ingest-and-modelling/notes/02-dimensional-modelling
- front: What does drilling across do differently?
  back: Aggregate each fact to its shared conformed dimensions first and then join the results, because a direct join multiplies both sides.
  lesson: data-engineering/02-ingest-and-modelling/notes/02-dimensional-modelling
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
- front: What should each stage state, so that failures become visible?
  back: Each stage should state what it will not trust, in keys, default rows, history and contracts, so that failures become visible.
  lesson: data-engineering/02-ingest-and-modelling/notes/04-data-contracts
- front: Which pillar turns these models into scheduled builds?
  back: Pillar 3 builds these models with dbt and schedules them, so that everything agreed here is tested on every run.
  lesson: data-engineering/02-ingest-and-modelling/notes/04-data-contracts
---
