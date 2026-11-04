---
title: "Erasure on Immutable Storage: Vacuum, Crypto-Shredding and the Ledger"
tags: [foundations, pattern]
summary: "Deleting one person from immutable files needs a file rewrite, a vacuum in table formats, a ledger replayed on restore or crypto-shredding, and a coverage check across every store."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--07-architecture-and-governance--notes--02-access-control-pii-gdpr.md
---

# Erasure on Immutable Storage: Vacuum, Crypto-Shredding and the Ledger

GDPR Art. 17 gives a right to erasure without undue delay when a ground applies, but it is not absolute: Art. 17(3) excludes processing needed for a legal obligation, some archiving and research, and legal claims, so tax records can stay while a marketing profile goes. Art. 12(3) sets the response time at one month, extendable by two further months for complex or numerous requests, so compaction and retention schedules must fit inside it. Engineering guidance, not legal advice.

The usual architecture pulls the other way: immutable logs, append-only tables and reprocessing make pipelines safe, and on such systems deletion is more a matter of making data harder to retrieve than impossible, since copies linger in storage engines, file systems and backups. Holding data creates risk that outlives the system, and purpose-limited collection conflicts with collect-everything lakes; a retention rule is a design decision.

## Rewrite files

Parquet cannot be edited, so find every file holding the person and rewrite it. Partitioned by month and not by person, one subject sat in 3 of 6 files. Keep identifying data in a small dimension table that facts reference by key to shrink this cost.

## Table formats: delete is not erase

After a Delta delete the current table had no rows for the subject, but time travel to version 0 still returned all 7. Data is gone only after `VACUUM`, which is not automatic, defaults to seven-day retention, removes data files only, and ends time travel beyond the horizon (the demo set retention to zero, dangerous for concurrent readers). Iceberg has the same shape: expiring snapshots removes them from metadata and files are deleted once unreferenced. Schedule the whole path inside the Art. 12 window.

## Backups: crypto-shredding or a ledger

- **Crypto-shredding:** encrypt each person's direct identifiers with a per-person key and destroy the key on request; a backup copy then holds ciphertext with no plaintext. Limits: quasi-identifiers and history stored in clear can still identify her ([[K-Anonymity, Quasi-Identifiers and Linkage Attacks]]); a KMS holding millions of keys becomes a dependency of every read; losing a key by accident is a breach, so destruction must be deliberate and logged. The sources contain no regulator statement that key destruction satisfies Art. 17, so its legal standing is unsettled.
- **Erasure ledger:** keep the IDs of erased people and replay deletes on every restore. A restored backup brought back 17 rows for a ledger subject; replay left 0. The ledger stores an identifier of an erased person, so keep it minimal (the pseudonymous key and nothing more) and record the reason.

## Coverage check

Automate "is every store clean". After deleting subject 42, the lake and the Delta table were clean, but a feature table (1 row) and a backup (7 rows) were still open. Lineage belongs to the erasure process: the downstream list of the source is the list of places to check. It still misses analyst exports, notebook copies and processors, so pair it with a storage scan for the key column and processor confirmations. A backup stays open until it expires or the ledger covers it; you should be able to say which. Whether a trained model holds personal data is an open question given membership-inference and inversion attacks, so decide with the DPO whether retraining is on the erasure path and record the training-data version.

## Retention

Storage limitation is easiest as a scheduled job per column; free text goes first. A demo nulled notes past 90 days and deleted rows past 730 (invented periods; real ones come from legal). The job must run on every store in the coverage check, and date deletes in a table format need the same vacuum step.

## See Also
- [[Access Control Below the User, Audit Logs and Breach Scope]] — prerequisite-for
- [[Contract Change Impact Chain and the Same-Name Unit Change]] — related (lineage as the downstream list)
- [[Pseudonymised Is Not Anonymised: Hashing Attacks and Keyed Pseudonyms]] — related
