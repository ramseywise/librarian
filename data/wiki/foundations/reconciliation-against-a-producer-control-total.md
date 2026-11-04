---
title: "Reconciliation Against a Producer Control Total"
tags: [foundations, pattern]
summary: "Nothing inside a table can show it is true; the cheapest accuracy test compares it with a second, independent account such as the producer's own daily row count, and it fails if that count is computed after a retry."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--05-quality-and-observability--notes--01-quality-dimensions-and-tests.md
---

# Reconciliation Against a Producer Control Total

Accuracy needs a second account of the same events. The cheapest is a control total: the producer writes a manifest with its row count per day, and the consumer compares counts per partition.

In a synthetic quarter, one comparison caught two faults that needed different row-level tests: a day with 2,980 rows sent and 0 received, and a day the producer counted once (2,947) but that arrived twice (5,894).

## Failure modes

- **The count must be independent of the send.** A count taken after a retry would have said 5,894 and agreed with the bug.
- **Counts miss value faults.** A null spike leaves the row count unchanged, so where money is involved reconcile sums as well as counts.
- **A late partition is missed once it has landed**, because the totals then agree.

The general argument is end-to-end: do not trust that disks, pipelines and libraries work, read data back and check it, preferably across the whole derived pipeline so one check covers every step on the way. Comparison at the wrong grain hides faults (see [[Parallel Run and Reconcile at the Grain People Read]]).

## See Also
- [[Data Quality Dimensions and Tests as Failing-Row Queries]] — prerequisite-for
- [[SQL Fan-Out and Source Reconciliation]] — related (same idea for query results)
