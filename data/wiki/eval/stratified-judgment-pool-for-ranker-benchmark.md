---
title: Stratified Judgment Pool for a Ranker Benchmark
tags: [eval, pattern]
summary: Build a human-graded ranker benchmark by freezing an offline snapshot, deriving its strata from the snapshot's own counts, and filling each moment's pool with a deliberate mix (top slate, ranks 6-20, near-threshold by score, one per exclusion reason, random) — and expect the first real-data run to expose defects that every fixture test passed over.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis289-relevance-benchmark-corpus.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis289-relevance-benchmark-corpus.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis289-relevance-benchmark-corpus.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis289-relevance-benchmark-corpus.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis289-relevance-benchmark-corpus.md
---

# Stratified Judgment Pool for a Ranker Benchmark

From the build of a relevance benchmark corpus for a deterministic recommender (repo akira,
2026-09-16 to 09-22): moment × candidate judgments, graded 0-3 with reason codes, feeding the
[[Frozen Ranking Baseline from a Pure Ranker]]. The goal was to make "does the ranker get this
right?" a question with instrumented evidence. The build's done-when was the instrument and
tooling; the grading itself was scheduled as separate human work.

## Contract first, tooling second

Phase 1 shipped only what the downstream metrics work imported: the judgment-row schema, the
storage table and a side-by-side "full breakdown" function over the ranker and composer. It
was a new sibling file, so the production serving path was never edited. Phase 2 (snapshot
builder, moment sampler, rating UI, export plus agreement calculator) blocked nothing
downstream, because the metrics could ship UNGATED against synthetic fixtures meanwhile.

## Pool construction

- **Label from an offline snapshot, never the live published pool.** About 5-10 published
  rows cannot fill one moment's pool. The snapshot takes every enriched row in any
  non-terminal review status (draft, needs-review, published), stamped with every frozen
  version ([[Frozen Version Stamps on Logged Results]]), and writes a strata-coverage report
  so the moment grid is sized against reality rather than an assumed count.
- **Derive strata from the data, not an editorial list.** District density (dense-central vs
  sparse-outer) is a median split over each snapshot's own per-district candidate counts. It
  is reproducible and re-derives itself on every snapshot, so there is no hand-kept table to
  go stale. Tests pin the boundary case (exactly at the median counts as dense) and the
  all-tied case (one bucket, not an error). A skewed snapshot can still empty one slice; the
  fix is a wider snapshot, not code.
- **Derive axes the schema splits.** "Scope" (near me / citywide with a district / citywide
  with none) is computed from two orthogonal fields rather than treated as one native field.
- **A deliberate pool mix per moment:** the composed top 5, ranks 6-20, near-threshold items,
  one excluded item per hard-filter reason present, and a random eligible sample, with no
  candidate in two buckets. Near-threshold is **an epsilon on the score** (0.03 of the
  composed cutoff), not a rank window, so it also catches a rank-25 near-tie. The epsilon is
  a named tunable registered in the change contract; a bare literal would break the repo's
  no-magic-numbers rule.
- **Skip empty strata cells**; never pad them with ungradeable moments.
- **Validate slugs at the boundary.** `moment_id` must match `^m[0-9]{3,}$` and rater ids
  `^r[0-9]{2}$`, so a hand-typed id fails validation instead of silently creating a new,
  uncorrelated moment. There is no moments table: the frozen `moment_context` JSON is the
  record of what the id meant. Rater ids are opaque codes, never account ids.

## Agreement calculator with no dependencies

Quadratic-weighted kappa for the ordinal grade and plain Jaccard for the fixed
reason-code vocabulary (not MASI, which suits free-text tags). Both are hand-ported, so the
script runs with zero setup before any judgment exists. A `--self-test` checks against
hand-computed confusion matrices: identical gives 1.0, one off-by-one in 8 gives 17/18, a
balanced reversal gives -1.0. The export keeps only `(moment, candidate)` groups with two or
more *distinct* raters, so a rater is never counted against themself.

## What the first real-data run exposed

Every fixture test was green. The first run against the real snapshot (113 candidates)
still failed in three ways:

- **Zero moments generated.** Every candidate's price was `unknown`, so no price stratum had
  coverage. Fix: unknown answers every band, and a strata key with zero count is not coverage.
- **Pools of about one row.** The breakdown used the *visitor-facing* eligibility gate, which
  is much stricter than "fits this moment". Fix: one named pool gate shared by the pool
  builder and the corpus loader.
- **A served-path feature had been inert.** A schema parser (`z.object`) strips keys it does
  not name, and the venue-join schema never named the place-subtype field, so an earlier
  subtype demotion never reached the served path. Fix: name the keys and pin them with a
  parse-survival test.

After the fixes: 24 moments and 467 grading tasks. One finding stayed open: the composer
filled only 1 of 5 slots on every real moment.

## Build-time defect classes

- **Layer rules force a substrate module.** The rating route imported pool helpers from the
  eval-experiments directory. The lint rule (nothing outside evals may import evals) rejected
  it, and the shared code moved to the scoring substrate with a backward-compatible re-export.
- **Hand-written DB types must match the SQL signature exactly.** RPC parameters with no
  default are required-but-nullable (`X | null`), not optional. The wrong choice produced
  five type errors.
- **Repo-wide guards fire on synthetic data too.** A "never log raw coordinates" test flagged
  the new moment-context carries. They carried only a synthetic constant, so the fix was a
  type annotation that matched the guard's safe pattern, plus justified allowlist entries.
- **Vocabulary duplicated between TypeScript and SQL CHECKs drifts.** Reason codes got a
  cross-check test; the exclusion-reason union had none and was flagged.

## See Also
- [[Frozen Ranking Baseline from a Pure Ranker]] — prerequisite-for (this corpus is the judged input the baseline scores)
- [[Append-Only Human Labels]] — extends (the judgment table follows the same append-only, picklist-rater rules)
- [[Frozen Version Stamps on Logged Results]] — related (every snapshot carries the stamps)
- [[Write-Time Deterministic Holdout]] — related (why favourites stayed out of the judgment rows)
- [[Human Agreement Ceiling Protocol]] — related (what the kappa figure is for)
