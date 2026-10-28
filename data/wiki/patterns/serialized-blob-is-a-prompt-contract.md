---
title: A Serialized Blob Is a Prompt Contract
tags: [patterns, prompting, eval, pattern]
summary: A JSON column that any consumer passes wholesale into a model prompt via JSON.stringify makes its shape part of that prompt, so restructuring the column for storage reasons changes what a judge sees, with no test to catch it. Grep for every reader before you reshape it, narrow on the read side with a fallback for old rows, and remember that stringified fixtures are invisible to the type checker.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-23-dis372-pre-model-evidence-stage.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-23-dis372-pre-model-evidence-stage.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-23-dis372-pre-model-evidence-stage.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-23-dis372-pre-model-evidence-stage.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-23-dis372-pre-model-evidence-stage.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-23-dis373-venue-probe-v3.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-23-dis373-venue-probe-v3.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-23-dis373-venue-probe-v3.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-23-dis373-venue-probe-v3.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-23-dis373-venue-probe-v3.md
---

# A Serialized Blob Is a Prompt Contract

From a plan to add a pre-model candidate stage to an enrichment pipeline (repo akira,
2026-09-23). The plan stored deterministic candidate labels beside the model's output by
reshaping an existing jsonb column. `raw_enrichment` would change from the bare sanitized
model payload to `{ model: <payload>, candidates: [...], resolution: [...] }`. That avoided a
migration repeated across three enrichment tables. The draft said the field had "no
confirmed reader beyond the flattener".

## The reader nobody listed

`grep -rn raw_enrichment src` found a QC stage that forwarded the field verbatim into its
input type as `unknown`. The QC prompt builder then ran `JSON.stringify(qcInput, null, 2)`.
So **the entire column value was serialized into the QC judge's prompt.** If the reshape had
shipped as written, the judge would silently have started seeing `{ model, candidates }`
instead of the flat payload it was written to evaluate. That is a prompt change to a second
model, made by a storage decision, and no fixture pinned the shape to catch it.

Why it hides:

- Typing the field as `unknown` and passing it through means the compiler raises nothing
  when the shape changes.
- Serializing the whole object into a prompt makes every key part of the prompt text,
  including keys added for unrelated reasons.
- The usual "who reads this field" search looks for property access (`.raw_enrichment.x`)
  and misses a reader that never looks inside.

## The fix: narrow on the read side, with a fallback

The QC preparation step now forwards `raw_enrichment?.model ?? raw_enrichment`. Rows written
before the change still have the flat shape, so the fallback keeps every existing row's QC
input identical. New rows narrow to the same `model` payload the judge always expected. The
plan's done-when kept a full `grep -rn raw_enrichment` sweep. Every other hit was confirmed
by reading to be shape-agnostic: key presence, deletion, or column name only.

## The same blindness in fixtures

A sibling plan made a field required on a model-output schema. `tsc` flagged the
hand-built object-literal fixtures. **Three parse tests failed only at runtime**, because
their fixtures went through `JSON.stringify` before being parsed, and a string has no shape
for the type checker to see. When you change a schema, look for stringified fixtures as well
as typed literals. A green type check says nothing about them.

## Rules

1. Before reshaping a JSON column, find every reader, including ones that pass it through
   untouched. Pay most attention to any that serialize it into a prompt, a log line read by
   a model, or an export.
2. Change the read contract at the consumer, with a fallback for old rows, in the same PR.
   Do not count on every future reader guessing which shape it holds.
3. Pin the shape a judge receives with a test, so the next reshape fails loudly.

## See Also
- [[Sanitize Never Fails, Validate Never Mutates]] — related (another stage contract on the same enrichment payload)
- [[Read-Every-Consumer Migration]] — extends (the consumer you missed is the one that never dereferences the field)
- [[Evidence-Labelled Generation with Deterministic QC]] — related (the pre-model stage whose storage triggered this)
- [[Verbatim Evidence Quote Verification]] — related (where the stringified-fixture break surfaced)
