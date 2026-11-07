---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- data-engineering/04-warehouse-lakehouse-streaming/slides/deck.yaml
cards:
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
- front: Why tune the query before buying capacity?
  back: Each fix changes what the next should be, so tune the query before you buy capacity.
  lesson: data-engineering/04-warehouse-lakehouse-streaming/notes/05-cost
---
