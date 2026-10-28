---
title: Frozen Version Stamps on Logged Results
tags: [eval, infra, pattern, conflict]
summary: Every served result row carries a named version constant for each component that shaped it — prompt hash, enrichment, weights, ranker, composer, schema — and a classifier whose output is logged but whose rule-table is unversioned is a hole; instrumentation ships in the same commit as the feature because logs cannot be backfilled.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/research/2026-09-16-dis289-relevance-benchmark-corpus.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-16-dis289-relevance-benchmark-corpus.md
  - data/raw/claude-docs/akira/docs/research/2026-09-10-results-surface-design.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-10-results-surface-design.md
  - data/raw/claude-docs/akira/docs/research/2026-09-03-dis37-replay-corpus.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-03-dis37-replay-corpus.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-03-dis37-replay-corpus.md
  - data/raw/claude-docs/playground/docs/research/2026-09-03-dis37-replay-corpus.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-10-results-surface-design.md
  - data/raw/claude-docs/playground/docs/research/2026-09-10-results-surface-design.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-16-dis289-relevance-benchmark-corpus.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-31-b65-momentcontext-versioning.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-31-b65-momentcontext-versioning.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-31-b65-momentcontext-versioning.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-31-b65-momentcontext-versioning.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-31-b65-momentcontext-versioning.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-31-b65-momentcontext-versioning.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-31-b65-momentcontext-versioning.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis291-sparse-evidence-treatments.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis291-sparse-evidence-treatments.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis291-sparse-evidence-treatments.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis291-sparse-evidence-treatments.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis291-sparse-evidence-treatments.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis292-intake-scoring-semantics.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis292-intake-scoring-semantics.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis292-intake-scoring-semantics.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis292-intake-scoring-semantics.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis292-intake-scoring-semantics.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-15-dis272-enrichment-prompt-experiments.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-15-dis272-enrichment-prompt-experiments.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-15-dis272-enrichment-prompt-experiments.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-15-dis272-enrichment-prompt-experiments.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-15-dis272-enrichment-prompt-experiments.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-15-dis272-enrichment-prompt-experiments.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-15-dis272-enrichment-prompt-experiments.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis311-freeze-intake-option-set.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis311-freeze-intake-option-set.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis311-freeze-intake-option-set.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis311-freeze-intake-option-set.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis311-freeze-intake-option-set.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-15-dis272-prompt-identity-phase1.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-15-dis272-prompt-identity-phase1.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-15-dis272-prompt-identity-phase1.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-15-dis272-prompt-identity-phase1.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-15-dis272-prompt-identity-phase1.md
---

# Frozen Version Stamps on Logged Results

A logging convention from a recommendation ranker (akira) built so that a benchmark corpus
and a replay corpus could be reconstructed later.

## The stamps

Each independently-changeable component exports a named version constant, and every
served result row is stamped with all of them: enrichment version, review-gate version,
prompt hash, weight-set version, ranker version, composer/diversification version, and the
moment-context schema version. A relevance judgment made against a served row can then be
joined to exactly the configuration that produced it.

**The hole found by audit:** a specificity classifier had a point table but no version
constant. Its *output* (`low`/`medium`/`high`) was logged, so it looked covered — but the
output stamp does not change when the point table does. A logged output is not a logged
rule; every rule-table that can change gets its own constant.

## Which stamp a change bumps

A stamp's territory is set by what its doc comment says it covers. Which file a change
touches does not decide it. Two same-day plans on akira's ranker hit this:

- The weights version is documented as bumping only "when a number in the weight profiles
  changes". A change to dimension or modifier *composition* (an uncertainty treatment, a
  context-tag mapping table) leaves the weights alone. It is still a change to the
  ranker's output, so it bumps the **ranker** version.
- One plan's first draft checked only the weights and composer stamps, found neither file
  touched, and concluded no bump was needed. The ranker's scoring function calls the
  dimension directly, so editing the dimension's mapping table changes what `rank()`
  returns. On refine the plan bumped `ranker_v0.1 → ranker_v0.2` in the same commit, so
  log rows from before and after the fix can be told apart without leaning on deploy
  timestamps.
- Follow the call graph, not the file list. Grepping for the literal old stamp is a
  cheap blast-radius check. Graders and tests that import the constant need no edit.
- The remaining gap: individual dimensions' mapping tables have no stamp finer than the
  whole-ranker version. Any one table changing bumps the coarse stamp. That is recorded as
  a known limitation, not fixed.

## Instrumentation ships with the feature

The product's invariant: *instrumentation ships in the same commits as the ranker; logs
cannot be backfilled; a ranked result served without a complete log row violates the
measurement guarantee.* The concrete case: "alternatives" (similar items under each
primary) were about to be served with no log concept for them. The moment one is served
without `primary_id`, `alternative_rank`, `similarity_score`, and the chosen-over-primary
interaction, the only signal that could ever validate the similarity threshold is lost.
The struct the composer already produced carried exactly those fields, so the log shape
was the existing type. The migration ships *with* the serving change, not after.

Related: an eval metric tuned against the same fixtures that grade it stays **ungated**
until an independent signal exists — here, which alternative users chose over its primary.
Serving with logging is what creates that signal.

## Versioning the context contract (akira B-65, 2026-08)

The moment-context type was the multi-surface seam and the consumer intake schema, yet it
lived beside the ranker's internal types with no version field. The change:

- **Move the contract to the schema layer**; the old location re-exports so scoring
  internals need no import churn.
- **Add `schema_version`, a coarse `surface` discriminant, and `locale` now**, even though
  per-surface weights and locale routing are deferred — so adding that logic later needs
  no contract change.
- **Additive and optional.** New fields carry producer-stamped defaults; pre-version rows
  have no stamp, and readers treat absence as "older than v1". No runtime throw on a
  missing stamp, because old rows must stay readable.
- **Exhaustive lookup over a ternary.** Mapping the four-value log `surface` onto the
  two-value context surface uses a `Record<LogSurface, MomentSurface>`, which fails to
  compile when a fifth value appears; a ternary silently routes it to the default.
- **Prove the stamp survives to the log row** with an end-to-end check through the
  recorder, not only a unit test of the producer.

A threshold baked in at write time (a viewport dwell cut-off) is the same problem in
miniature: free to change before the first production row, a version-stamp event after
([[Landed Is Not Complete]]).

## Freezing an instrument before a comparison round (akira, 2026-09-16)

Before a two-tester beta comparison, the intake question's option set was frozen. The
decision is reusable for any instrument that a comparison round depends on:

- **A copy-only change still bumps the stamp.** Only the visible label changed: "Event
  type" became a phrase that covered the four verticals the options now spanned. Option
  values and scoring mappings stayed byte-for-byte the same. The intake version still went
  from `v0.1` to `v0.2`, because otherwise one cohort would mix two prompt wordings under
  one stamp. The context-schema version did not move, because the context shape did not
  change. Each stamp tracks its own component.
- **Pin the frozen contract as an exact test, not prose.** An exact ordered `[value,
  label]` assertion plus an exact-version assertion, replacing a truthy check. Adding,
  removing, reordering or renaming an option, or forgetting to bump the stamp, fails
  deterministically.
- **Do not add an option that duplicates an existing state.** An explicit "Surprise me"
  tile would have duplicated the optional question's unanswered state, which already
  reaches scoring as `null`. It would also have added a second logged value for the same
  meaning. Options that need new mappings and licensed images (re-adding dropped
  categories, splitting drinks from food) expand the instrument right before the round
  without evidence. Keep their mappings as hidden compatibility paths instead.
- **Never reuse a stamp.** Rollback reverts label and version together, and `v0.2` is
  never reassigned to another vocabulary once beta rows carry it. The freeze holds until a
  named event: the acceptance round closing.

The acceptance run that depended on the freeze then hit blockers of its own. See
[[Ship Logging Before Features]] (the outcome signal has to be decided before the first
serve).

## Replay corpora

A de-identified replay corpus is the stamped descriptor rows kept past the raw-log
retention window. Because the stamps are on the row, a replay can re-run today's ranker
against yesterday's moments and attribute every diff to a named version change.

## Prompt identity columns (akira DIS-272)

The prompt stamp was built as three nullable columns on every enrichment table: `model`,
`prompt_version`, and `prompt_hash`. Two axes back each other up. The version is a constant
bumped by hand when the production prompt changes on purpose, kept separate from the
output-contract version. The hash is SHA-256 of the template rendered with empty
placeholders, so it moves only when the instruction text moves, never with row content. A
golden-hash test pins the per-vertical hashes, so an edit without a bump fails CI. (Contested: the build review found the test pins the version literal too, so re-pinning hashes alone passes; see `_conflicts.md`.) Rows
written before the migration stay NULL, with no fabricated backfill. The identity is
computed once, at the entry point both the sync and batch paths call. Details are in
[[Offline Prompt Experiment Runner]].

## See Also
- [[Append-Only Human Labels]] — complements (the judgments that join to these stamps)
- [[Landed Is Not Complete]] — related (a stamped row can still be incomplete or unjoinable)
- [[Write-Only Fields and the Reader Map]] — extends (keeping the breakdown is what makes stamping it possible)
- [[RAG Eval Gate Contract]] — related (config snapshot and run id as the gate input contract)
- [[Data Clusters by Writer and Trust]] — related (replay corpus as an interaction-cluster table)
- [[Frozen Ranking Baseline from a Pure Ranker]] — complements (the snapshot that carries these stamps so judgments can be joined)
- [[Ship Logging Before Features]] — extends
- [[Intake Option Separability via Reach Vectors]] — related (measuring whether intake options are distinct requests at all)
- [[Offline Prompt Experiment Runner]] — related (where the prompt-identity stamp was built and is consumed)
