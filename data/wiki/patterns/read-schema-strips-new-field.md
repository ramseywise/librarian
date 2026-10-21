---
title: Read-Side Schema Strips the New Field
tags: [eval, infra, pattern]
summary: "Adding a field to a model's output schema is not enough when a second, read-side schema parses the stored results — a strict object parser silently drops undeclared keys, so the comparison tool reports the new field's yield as 0 while the raw JSONL holds real values; declare the field on every parse boundary and report undefined for versions that never emitted it, not 0."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-24-dis384-measurement-loop.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-24-dis384-measurement-loop.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-24-dis384-measurement-loop.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-24-dis384-measurement-loop.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-25-dis214-six-issue-batch.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-25-dis214-six-issue-batch.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-25-dis214-six-issue-batch.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-25-dis214-six-issue-batch.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-25-dis214-six-issue-batch.md
---

# Read-Side Schema Strips the New Field

## The incident

An akira venue-enrichment probe gained a new output field, `context_tags`, in v4. The
probe's own output schema was extended and the prompt asked for the field. The
before/after comparison tool then reported a `context_tags` yield of **0**.

The raw stored JSONL had real, populated arrays. The comparison module had its own
`probeResultRowSchema` for parsing stored rows, and that schema's `output` sub-object did
not declare `context_tags`. Zod's default object parsing **strips unknown keys without an
error**, so every parsed row lost the field before any count ran. Nothing failed. The
number was just wrong, and it pointed toward "the prompt change did nothing."

## Why it happens

A field crosses more than one schema: the writer's output schema, and every reader that
re-parses persisted output (comparison tooling, exporters, read models). Extending the
writer's schema feels like the whole change. The read-side schemas are usually in other
files, often on tooling paths nobody runs during the change.

## The fix

- Declare the new field on **every** parse boundary that reads the stored rows. A grep for
  the writer schema's sibling field names finds them.
- Make the derived metric honest about versions: `mean_context_tags` is `undefined` for
  probe versions that never emitted the field, not a misleading `0`. A zero should mean
  "emitted and empty", never "not parsed."
- Where silent dropping is the risk, a strict parser (reject unknown keys) on a tooling
  boundary turns the miss into an error. Use it there, where an error costs nothing.

## The general shape

A measurement that reads 0 right after a change meant to move it is a plumbing suspect
before it is a model finding. Check the raw artifact before the parsed one. This is the
same diagnostic as [[Measurement Fix Mistaken for Model Gain]], seen from the other side:
there a broken scorer hid real gains, here a broken parser hid a real field.

## A second instance: the loader's own schema (akira, 2026-09-25)

A probe parser returned a `corroborated` flag, but the intermediate result-line type dropped
it, so a production flag could never fire. Fixing that exposed the second strip: the loader CLI
re-parsed the JSONL through **its own** zod schema, which did not declare the field. The durable
fix was to **colocate the schema with the interface** (one exported schema beside the result-line
type, imported by the CLI) so the two cannot drift, plus a JSONL round-trip test covering the
field and a pre-change line.

## See Also
- [[Silent Failure Catalogue]] — instance-of (a default value filling a field the parser dropped)
- [[Measurement Fix Mistaken for Model Gain]] — related (scorer-side version of the same trap)
- [[Dead Modifier Trace]] — related (a zero that is either plumbing or real absence)
