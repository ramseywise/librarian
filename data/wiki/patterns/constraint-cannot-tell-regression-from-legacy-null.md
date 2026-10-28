---
title: A Constraint Cannot Tell a Regression From a Legacy Null
tags: [patterns, infra, pattern]
summary: "When a column is NULL both for legitimate legacy rows (a documented nullable, no-backfill convention) and for a future write-path regression, the two produce an identical row shape, so a NOT NULL CHECK cannot guard against the regression — it would only reject legitimate writes; defer the constraint until a backfill makes it meaningful, and guard the write path with a behavioural test instead."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/reviews/2026-09-16-dis275-human-label-persistence.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-16-dis275-human-label-persistence.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-16-dis275-human-label-persistence.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-16-dis275-human-label-persistence.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-16-dis275-human-label-persistence.md
---

# A Constraint Cannot Tell a Regression From a Legacy Null

## The case

An akira human-labelling table stored two kinds of label in one table behind a CHECK with two
branches:

- **absolute** labels, where the rater sees no model output. The CHECK *forbids* the model and
  prompt-identity columns: they must be NULL, because the label is structurally blind.
- **pairwise** labels, which compare two model outputs. The CHECK did not *require* the
  attribution columns. A pairwise row with all of them NULL is useless for the model-versus-human
  agreement statistic the labels exist to compute.

A reviewer flagged the asymmetry: the database enforced blindness in one direction and trusted
the RPC in the other, so a future edit that stopped populating the columns would write durable,
valid-looking, useless rows. The proposed fix was NOT NULL in the pairwise branch, "now, while
the migration is unpushed and it is only a text edit".

## Why the fix was declined (wont_fix, verified)

The fix round declined and reported back rather than guessing, and the orchestrator verified the
reasoning against the tree:

- The RPC does not take those values from the caller; it SELECTs them live from the referenced
  model-output row.
- That source column is nullable **by documented convention**: its migration header said
  *"NULLABLE, NO BACKFILL"* — every row written before the column existed keeps NULL, never a
  fabricated value. Most of the catalogue still carried NULL.
- So NOT NULL would make the RPC **reject** pairwise labels against most existing rows: a
  functional regression on the very corpus the rating session was built to label.

The underlying worry is real but **not closable by a constraint**: a regression that omits all
the fields produces a row identical to a legitimate pre-migration reference. No predicate over
data shape alone can separate them. The asymmetry was correct as written.

## The rule

1. Before adding a constraint, ask whether the bad state is **distinguishable by shape** from a
   legitimate state. If a documented convention already makes NULL legitimate, the constraint
   cannot target the regression.
2. Guard the write path where the information exists: a test on the RPC that asserts attribution
   is copied when the source row has it, rather than a CHECK on the result.
3. **Defer, do not drop.** Record the constraint as a follow-up tied to its enabling event (a
   backfill, or every source row re-run after the migration). At that point it is both safe and
   meaningful.
4. A "cheap now, expensive after push" argument is a reason to decide quickly, not a reason to
   add a constraint that rejects legitimate writes.

## See Also
- [[Migration Done Means Pushed and Probed]] — related (why unpushed migrations are cheap to edit)
- [[Landed Is Not Complete]] — related (rows split at the migration boundary)
- [[Natural Key Without a Discriminator Collapses Rows]] — related (another constraint that rejected legitimate rows)
- [[Silent Failure Catalogue]] — related
