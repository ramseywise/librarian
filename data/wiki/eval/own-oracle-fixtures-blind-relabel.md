---
title: Own-Oracle Fixtures and the Blind Relabel Path
tags: [eval, pattern]
summary: "Fixtures whose expected values came from running the function under test can never justify a threshold. The way out is a separate export of real rows with `expected` set to null and the function's actual output in a separate `observed` field, labelled by a human from the written rule, appended to the same fixture file with provenance, measured, and only then gated at the observed rate."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-22-dis319-gate-enrichment-input-shaping.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-22-dis319-gate-enrichment-input-shaping.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-22-dis319-gate-enrichment-input-shaping.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-22-dis319-gate-enrichment-input-shaping.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-22-dis319-gate-enrichment-input-shaping.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-22-dis295-edition-collision-fixture-set.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-22-dis295-edition-collision-fixture-set.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-22-dis295-edition-collision-fixture-set.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-22-dis295-edition-collision-fixture-set.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-22-dis295-edition-collision-fixture-set.md
---

# Own-Oracle Fixtures and the Blind Relabel Path

**The trap:** fixtures for a deterministic function are often written by running the
function and pasting its output into `expected`. The grader then passes at 1.0 by
construction and proves nothing. In akira, several metrics were registered but held
UNGATED for exactly this reason (see [[UNGATED Metric Convention]]). One was an input-shaping
function that decides which prompt-summary lines stay `unknown`, with 14 fixtures. The
[[Q0–Q5 Quality Ladder]] prevents the trap for new functions by writing cases from the
requirement before the function exists. This page covers the repair for a metric that is
already caught in it.

## The repair path

One earlier metric had escaped the trap (#277). The input-shaping plan (#319) copied that
shape:

1. **A pure corpus-row builder.** For each real row it records the raw inputs and runs the
   real function, but stores the result in **`observed`** for the labeller's reference.
   `expected` is hard-coded to `null`, and `metadata.labelled` is false.
2. **A thin, read-only export CLI** over production, with a bounded `--limit` split evenly
   across verticals (40 rows), no write flag, and no spend. It goes on the read-only
   allowlist of the write-guard test, with a reason.
3. **A human labels `expected` from the written rule.** The rule here was the mapping table
   in the original plan, from vertical × input shape to summary line. The labeller never
   calls the function to get the answer.
4. **Append the labelled rows to the same fixture file** that holds the hand-authored
   cases. Use distinct ids and record provenance in `metadata`. Then re-run the grader.
5. **Gate at the observed rate**, mirroring the comment style of the earlier gated metric.
   If the run finds a real defect, the plan says to split the fix into its own plan rather
   than absorb it.

## Rules that make it hold

- **`observed` and `expected` are structurally separate,** and the export never fills one
  from the other. The named review risk is a labeller copying `observed` as a shortcut,
  which turns the measurement back into an own-oracle.
- **The number lands in a committed, gated artifact, not a notebook.** An earlier plan's
  "re-run the notebook" step never ran: the notebook directories were gitignored and the
  build had no production read. Notebooks prove nothing to the gate.
- **The check and the target are separate deliverables.** A related fixture slice (#295
  edition collisions) committed an *empty* fixture file plus a schema-parse test. That
  test is green at zero rows, so the code lands with the gate green whatever the
  labelling progress. Labelling is an operator follow-up, not a build step.
- **Collect pointers, not labels, when the store cannot reconstruct the answer.** The
  edition-collision collector only queried the database. It emitted candidate pairs (event
  ids, occurrence source URLs, a heuristic hint), and the operator read the live pages to
  label them. Code did no outbound fetching, which kept the slice out of the rights lane.
- **Drop rows that cannot be labelled.** A null-labelled row is not evidence either way,
  and it would break the parse test's non-null `expected` requirement.
- **Small N is acceptable for a first gate** (30-40 rows), provided the defects the sample
  cannot exercise are named.

## See Also
- [[UNGATED Metric Convention]] — extends (how an UNGATED metric earns its threshold)
- [[Q0–Q5 Quality Ladder]] — related (prevention: cases authored before the function)
- [[Human Verdicts as Judge Fixtures]] — alternative-to (the same loop for LLM judges, where the human decision rides in metadata)
- [[Natural Key Without a Discriminator Collapses Rows]] — instance-of (the edition-collision fixture slice)
- [[Design Decisions Migrate Into Plans]] — related (the behavioural-cases row that names the own-oracle trap)
