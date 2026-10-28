---
title: Write-Time Deterministic Holdout
tags: [eval, pattern]
summary: Decide which side of a train/benchmark split a logged signal belongs to at insert time, as a pure hash of the item's identity stored on the row itself, so the split exists before any consumer does, a re-save never flips sides, and each consumer enforces it with one WHERE clause.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis288-favourites-feedback-loop.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis288-favourites-feedback-loop.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis288-favourites-feedback-loop.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis288-favourites-feedback-loop.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis288-favourites-feedback-loop.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis289-relevance-benchmark-corpus.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis289-relevance-benchmark-corpus.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis289-relevance-benchmark-corpus.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis289-relevance-benchmark-corpus.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis289-relevance-benchmark-corpus.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis310-labelled-session-export.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis310-labelled-session-export.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis310-labelled-session-export.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis310-labelled-session-export.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis310-labelled-session-export.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-23-dis374-data-platform-maturity.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-23-dis374-data-platform-maturity.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-23-dis374-data-platform-maturity.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-23-dis374-data-platform-maturity.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-23-dis374-data-platform-maturity.md
---

# Write-Time Deterministic Holdout

From a recommendation app (repo akira, 2026-09-16) that started logging every save and
unsave of a favourite. Two future consumers wanted the same signal for opposite purposes:
a taste-vector and an internal rating would train or derive features on it, and a relevance
benchmark wanted some favourites as held-out evidence. If the same favourite feeds both,
the benchmark grades the ranker on data the ranker learned from. Neither consumer existed
yet, and the benchmark's table did not exist either, so there was nothing to join against.

## The mechanism

Make the split **a property of the log row, decided when the row is written**:

- A `benchmark_holdout boolean not null` column, computed at insert as a pure function of
  the item's identity `(user_id, content_kind, item_id)`, bucketed against a fixed rate
  (20%, chosen to match the benchmark's existing second-rater overlap so the two
  percentages need no separate justification).
- **Deterministic and replayable.** The same user–item pair always lands on the same side,
  so a favourite saved today and an unsave-then-resave next month cannot flip sides and leak.
- **Reuse the tree's existing hash.** Research first proposed inline SQL hash math. Planning
  found the app already bucketed randomisation arms with an FNV-1a "hash to unit interval"
  function against a fixed rate. The writer calls that function rather than deriving hash
  math a second time in SQL.
- **Enforcement is one filter per side.** Anything feeding derived aggregates filters
  `WHERE NOT benchmark_holdout`; any export for the benchmark filters `WHERE benchmark_holdout`.
  The rule is written down the day the column lands, not the day the first consumer does.

Add the column now, write the rule now, build the join later. A split that only exists in a
consumer's query can be applied differently by the second consumer.

## The tradeoff it did not settle

The alternative was operator-tagged: a manual flag on the operator's own curated
favourites. The hash split needs no bookkeeping and extends automatically to test-group
users. But it cannot guarantee that a *specific* curated pick lands on the held-out side,
and the benchmark's own text read as if it expected exactly those picks. The research
flagged this as the largest disconfirming risk and raised it as an explicit open question
rather than choosing silently.

The later resolution narrowed the holdout's role. A favourite carries no moment, context or
version set, so it cannot be mapped onto a graded (moment, candidate) judgment. Favourites
became a **validation check** against the judged corpus, never judgment rows (see
[[User Feedback Loops]]). The benchmark kept only a `source` column seam for them.

## The consumer side: exporting labelled sessions (2026-09-22)

The first consumer to read the column was an exporter turning labelled tester sessions into
immutable eval fixtures. It showed how the holdout is meant to be used once a real label
exists:

- **The holdout flag filters. It never becomes the label.** The label came from the one
  table shaped like an explicit verdict on a real served slate (`for_me` / `not_mine` /
  `wrong` plus a note). A save is a ranking signal, and a rater grading a sampled corpus
  is not judging a real session, so neither could supply the label. The exporter uses
  `benchmark_holdout = false` only to **drop** any served candidate whose save signal fed
  ranking. Without that, the same interaction would both train and grade one candidate.
- **Two pseudonym namespaces do not join.** The save log keyed on `sha256(user_id)`, and
  the study membership table on a random UUID. The bridge runs server-side on the real
  account id: hash it in-process to match the save log, join the verdict table directly,
  and write neither id nor either pseudonym to the output. The fixture key is a hash of
  `(result_set_id, candidate_id)`, never anything derived from identity.
- **A missing or ambiguous label join fails loud.** Exporting a smaller, partly unlabelled
  case would pass silently. Incomplete child rows fail that session's export. Pagination
  errors fail the run.
- **The fixture schema bans identity structurally.** A strict schema rejects any row that
  carries `user_id`, either pseudonym or a signed token. "Done" means changing a live
  catalogue row cannot change a saved fixture's grade, and a synthetic end-to-end fixture
  proves the grading path never queries a live table.


## Rotating the identifier under a recomputed split (akira, 2026-09-23)

Several holdout checks are **recomputed** from a pseudonym, not read from a stored column.
A later privacy plan that rotated the pseudonym scheme would have flipped existing users'
holdout status. The fix decoupled the bucketing input into a frozen key equal to the old
hash ([[Freeze the Bucketing Key Across Identifier Rotation]]).

## See Also
- [[User Feedback Loops]] — extends (favourites as a held-out signal, not ground truth)
- [[Study-Scoped Pseudonymous Attribution]] — related (the attribution seam the session exporter reads through)
- [[Data Clusters by Writer and Trust]] — related (the log is an interaction-cluster table with the same FK-less shape)
- [[Append-Only Human Labels]] — related (the judgment table the holdout was meant to feed)
- [[Explore Slice for Position Bias]] — related (the same hash-bucket mechanism assigns randomisation arms)
- [[Freeze the Bucketing Key Across Identifier Rotation]] — extends (keeps the split stable when the pseudonym scheme is versioned)
