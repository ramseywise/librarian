---
title: Dead Modifier Trace
tags: [eval, foundations, pattern]
summary: "When a scoring modifier reads 0 across every scored pair, trace each pair's raw inputs before fixing anything: the zero is either a plumbing bug (an evals-local candidate constructor feeding a bare value where the modifier keys on a namespaced spelling) or a real absence (the upstream pipeline never emits the field) — the two need opposite responses, and only the trace tells them apart."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-24-dis392-s1-corpus-metrics.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-24-dis392-s1-corpus-metrics.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-24-dis392-s1-corpus-metrics.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-24-dis392-s1-corpus-metrics.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-24-dis392-s1-corpus-metrics.md
---

# Dead Modifier Trace

## The observation

An akira relevance experiment scored about 200 venues against 130 moments, giving 17,940
scores through the real ranker. Three modifiers read exactly 0 on every one of them: a
discovery-value boost, an uncertainty penalty, and a subtype-fit penalty. Two similar zeros
had already turned out to be plumbing bugs: a tag read with the wrong object key, and a
candidate constructor that never set two fields. So the issue split item 2 into **"needs
the trace before it needs a plan."**

## The trace

A pure helper records, per (venue, moment) pair, each modifier's value **and which of its
inputs were present** (`inputs_present: { discovery_value: false, ... }`). The full rows go
to a gitignored JSON file and a summary table goes to stdout. The trace's findings were read
and **not acted on**: the fix is a follow-on ticket.

Results:

- **Discovery boost and uncertainty penalty: real absence.** Their four input fields were
  present on 0 of 17,940 pairs. The corpus came from a lighter venue probe, not the full
  enrichment pipeline, and that probe never emits these fields. Nothing is mis-wired. The
  corpus just cannot exercise these modifiers.
- **Subtype penalty: structurally dead, a plumbing bug.** The experiment had a **second,
  evals-local** candidate constructor that set `place_subtype` to the bare OSM value
  (`'restaurant'`, `'fast_food'`). The modifier's demoted-subtype set is keyed on the
  production `key:value` spelling (`'amenity:fast_food'`). The spellings can never match.
  Separately, the corpus held zero fast-food venues, so it could not have exercised the
  penalty even with matching spellings.
- **A static finding, printed once:** the candidate type had no `enrichment_confidence`
  field at all, and the quality dimension derived its confidence component from status
  alone.

## Why trace before fixing

The two causes need opposite responses. A plumbing bug is a re-key in one constructor. A
real absence means the modifier is correct and the corpus is the wrong instrument, so the
response is a different corpus or an explicit "not measurable here." Without the
`inputs_present` column, both look like the same zero.

The recurring root cause is a **second constructor for the same type**. Production builds
candidates in one place, and an experiment or eval builds them in another with a different
vocabulary. Every dead-zero in this ranker had that shape.

## Two harness lessons from the same slice

- **A grader that re-derives its own expected value is trivially true.** A field-population
  grader as first planned compared recomputed booleans to `expected` values that the same
  arithmetic had generated at export time. It read **1.000** on all 200 rows, whatever the
  corpus held. Computing pass/fail straight from the input (all four fields populated?) gave
  **0.475** overall, 0.667 on enriched and 0.048 on probed. Those numbers move when coverage
  moves. See [[UNGATED Metric Convention]].
- **Importing a CLI module ran its CLI.** Exporting the corpus loader from a script whose
  `main()` ran unconditionally at module scope made every importer run that CLI against its
  own `argv`. The fix was the ESM entry guard (`import.meta.url` against `argv[1]`), the
  same fix an earlier script had needed.

## See Also
- [[Starved Tag Triage: Edge, Prompt, or Supply]] — related (separate edge, prompt and supply causes before fixing a zero)
- [[Keep the Source Subtype Before the First Collapse]] — related (subtype vocabularies that stop matching)
- [[Read-Side Schema Strips the New Field]] — related (a zero caused by the reader, not the data)
- [[Frozen Ranking Baseline from a Pure Ranker]] — related (the pure ranker the trace runs through)
- [[Edge Registry With a Completeness-Checked Manifest]] — related (a missing map key, another silent zero)
- [[The Eval Harness Has Its Own Adapter]] — extends (the repair of the subtype plumbing bug)
