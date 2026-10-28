---
title: Mislabelled Column Is Worse Than Missing
tags: [patterns, infra, pattern]
summary: "A populated column whose name promises one quantity while it stores another gives every reader a confident wrong answer, and nothing in the data shows the error. Fix it by renaming the column to what it actually holds and adding a new column under the correct name. Rows from before the fix stay NULL in the new column, and that interpretation rule is written into the migration header and the type docstring."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-14-dis263-accepted-candidate-bridge.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-14-dis263-accepted-candidate-bridge.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-14-dis263-accepted-candidate-bridge.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-14-dis263-accepted-candidate-bridge.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-14-dis263-accepted-candidate-bridge.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-14-dis263-accepted-candidate-bridge.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-14-dis263-accepted-candidate-bridge.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-26-2a-log-completeness.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-26-2a-log-completeness.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-26-2a-log-completeness.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-26-2a-log-completeness.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-26-2a-log-completeness.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-26-2a-log-completeness.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-26-2a-log-completeness.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-20-dis353-home-feed-cards.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-20-dis353-home-feed-cards.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-20-dis353-home-feed-cards.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-20-dis353-home-feed-cards.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-20-dis353-home-feed-cards.md
---

# Mislabelled Column Is Worse Than Missing

From a log-completeness plan in the akira recommender. An audit of the serve-time result-set
log found several gaps. The one the plan called "the sharpest defect" was not a missing field.
It was a column that was always populated with the wrong quantity.

## The defect

The column was named `candidate_pool_size`. The code wrote `candidates.length` into it, but by
that point the array had already passed the hard filters. So the column held the count of
**eligible** candidates, not the full pool that was fetched. The true pool size was being
computed and then thrown away at the HTTP boundary.

A missing field is honest: an analysis that needs it finds the gap. A mislabelled field gives a
confident wrong answer to every query, notebook, and dashboard that reads it. The data itself
holds nothing that reveals the problem, because the value is plausible and consistent from row
to row.

## The three options

| Option | Result |
|---|---|
| (a) **Rename** to `eligible_pool_size`, **add** a new, correctly named `candidate_pool_size` | Every name matches its meaning from now on. Old rows keep their eligible count under the right name |
| (b) Keep the name, change what is written to it | Cheapest. Loses the eligible-count signal, which the scarcity mechanism needs. Swaps one blind spot for another |
| (c) Add `eligible_pool_size`, leave the old column as it is | Adds the signal and leaves the trap in place for any reader who doesn't know to distrust it |

The plan chose (a). Postgres `RENAME COLUMN` is transactional and keeps the data, so historical
rows end up under a name that is *correct* for what they hold.

## The interpretation rule travels with the schema

Every query that crosses the migration boundary needs a rule, and the plan put it in the
**migration header comment and the field's docstring**, not only in the plan document:

- In rows created before the migration, the new `candidate_pool_size` is `NULL`. The true pool
  size was never captured for them and cannot be recovered.
- `eligible_pool_size` (the renamed column) is correct for all rows.
- Treat `NULL` as "unknown for this row", never as zero, or filter on
  `created_at >= <migration timestamp>`.

## A constant in a required, unconstrained column

The same failure shows up without a rename. In the akira single-page importer, a required
`activity_type` column with no CHECK constraint received the constant "market / fair" for every
activity, and `primary_type` was a regex guess over the source name. Every museum, park, and spa
was typed as a market, every insert succeeded, and production's only value was the constant, so
nothing looked wrong. "No source for this field" here meant "no correct value", not "no value".
See [[Done-When the Cheapest Write Can Meet]] and [[Attribution Inherited From the Source Row]]
for the same plan's other findings.

## Related findings from the same audit

- **Do not log a value that has no source.** Five requested fields had nothing at serve time to
  fill them: no snippet-template module, no long-tail concept, no versioned taxonomy or taste
  model. The plan refused to invent them and listed each with the prerequisite it needs. A
  sixth (`degraded_mode`) was added as a nullable, unconstrained column with no writer, because
  its enum had not been ratified yet.
- **Don't add a second field for a fact that is already logged.** "Is long-tail" and "is
  exploration slot" both reduced to the existing `result_role` value. That value was null in
  production only because composition defaulted to off.
- **Store an evolving structure as one JSON field.** Per-dimension scores went in as one JSONB
  object inside each item, not seven numeric columns. Otherwise every change to the set of
  dimensions would need a migration and could silently drop a field again.
- **Size each fix by type**: pure passthrough of a value that already exists, small computation
  from an intermediate value, genuinely new instrumentation, or blocked on an external decision.
  The four types carry different risk. Only one step touched tested scoring logic, and that step
  required a before/after numeric diff.

## The same trap in a score badge (akira home feed, 2026-09)

An admin home feed was asked to show a taste-match badge, a moment score and an "Overall
relevance" score on each card. Six of the seven ranking dimensions score a candidate
*against* a moment. Only one (source trust plus enrichment completeness) means anything
without a moment, and no moment-independent composite existed. Labelling that one
dimension "Overall" would have printed a confident wrong answer on every card, and a real
composite would have needed its own weight decision: a second ranker nobody had designed.

The plan shipped the one dimension under its true name, "Data quality". It recorded in the
shelf module header and as a numbered decision that "Overall" was considered and dropped,
and why. The moment score appears only when the operator has set at least one moment
answer, and is absent otherwise. A display label is a column name a human reads. The same
rule applies: name the quantity it holds, or omit it.

## See Also
- [[Every Column Names Its Reader]] — extends (a column with a reader can still be lying to it)
- [[Ship Logging Before Features]] — extends (the serve-time log where this was found, and why the lost pool size can never be recovered)
- [[Parsed Then Dropped at the Insert Mapper]] — related (the true pool size was computed and dropped at the HTTP boundary)
- [[Silence Reads as Clean]] — related (a consistent wrong value raises no alarm)
- [[Attribution Inherited From the Source Row]] — related (a wrong value resolved at the wrong grain)
- [[Done-When the Cheapest Write Can Meet]] — related
- [[Insert-Only Upserts Strand Normalizer Fixes]] — related (old rows keep the wrong constant)
