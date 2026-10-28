---
title: Category Is a Bucket, Not a Recurrence Signature
tags: [patterns, eval, pattern]
summary: Counting recurrence by finding category groups unrelated defects; recurrence needs a named-pattern signature that cuts across categories, durable finding identity, and a log window longer than the recurrence threshold.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-09-friction-learning-loop.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-08-09-friction-learning-loop.md
---

# Category Is a Bucket, Not a Recurrence Signature

Source: the guacamayo friction learning-loop plan. It audited why the
[[Friction Promotion Ladder]] was not promoting recurring review findings.

## Mechanism

The promotion rule was "N=3 recurrences gets a hook". It counted recurrences by finding
**category**, but a category group is heterogeneous: one category holds many unrelated
defects. Real recurring defects **cut across** categories. One keyword pattern
(hardcoded-not-configurable) appeared 22 times across 7 categories and 4 repos. Another
(silent-swallow) appeared 13 times. The free-text `issue` field that might have carried a
signature was filled in on only 7 of 125 rows.

## Fix: a curated named-pattern table

An 8-entry table of named patterns with keyword matchers beat lexical clustering. The
corpus was too small for clustering to be stable, and a table can be audited: a human can
read why a finding matched.

## Two identity traps that destroy the history

- **A per-run id used as a primary key.** Finding ids like `CR-001` restart on every
  review run: 125 rows had only 44 distinct ids. With `INSERT OR REPLACE` on that key,
  each run silently overwrote earlier findings, and the review history collapsed from
  125 rows to 36. Fix: a composite
  `finding_uid = sha1(id|date|repo|file|title)`, plus a migration that detects the old
  schema with `PRAGMA` (see [[Cross-Sweep Finding Fingerprint]]).
- **The log window is shorter than the threshold.** The pass log rotates at 1000 lines,
  about 10 days. It cannot show an N=3 recurrence spread over two weeks, so the window
  must outlast the recurrence rule.

## See Also
- [[Cross-Sweep Finding Fingerprint]] — extends
- [[Friction Promotion Ladder]] — prerequisite-for
- [[Falsifiable Hypothesis Gate]] — extends
- [[Silence Reads as Clean]] — instance-of
