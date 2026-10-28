---
title: Build the Knobs, Not the Choice
tags: [patterns, eval, pattern]
summary: When a scoring question splits into defects you can decide from the definition and weighting questions only a benchmark can settle, ship the defects now and build the weighting options as a registry of switchable variants with a control arm identical to current behaviour. The benchmark then picks a variant that already exists.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/diskoe/docs/research/2026-09-16-dis292-intake-scoring-semantics.md
  - data/raw/claude-docs/akira/docs/research/2026-09-16-dis292-intake-scoring-semantics.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-16-dis292-intake-scoring-semantics.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-16-dis291-sparse-evidence-double-penalty.md
  - data/raw/claude-docs/akira/docs/research/2026-09-16-dis291-sparse-evidence-double-penalty.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-16-dis291-sparse-evidence-double-penalty.md
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
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis292-intake-scoring-semantics-continuation.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis292-intake-scoring-semantics-continuation.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis292-intake-scoring-semantics-continuation.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis292-intake-scoring-semantics-continuation.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis292-intake-scoring-semantics-continuation.md
---

# Build the Knobs, Not the Choice

From two research passes on akira's intake-to-scoring mapping. The ranker's judged
relevance corpus did not exist yet, so most "should this weigh more?" questions had no
honest answer. The method was to sort every claim into two bins before building anything.

## Bin 1: defects decidable by definition (ship now)

A claim goes here when the code contradicts a fact it already holds, so no taste is
involved. Examples from the intake audit:

- **The code had the fact and didn't read it.** A weekday morning or afternoon request
  mapped to the `weekend_day` context tag, and a weekday evening to `weekend_night`. The
  request's `date_range` sat on the same object, already computed, and was never read.
- **An additive, safe-by-default gap.** The `friends` option was missing from the
  with-whom audience map, so it reached scoring as nothing.
- **An independent grader hardcoding a version literal** (`'mc_v1'`) instead of importing
  the constant. When the constant moves, the grader keeps passing against the old version.
- **A structured reason for "no evidence" vs "mismatch"** (see
  [[No Evidence Ranks Below Confident Mismatch]]).

These ship with ordinary tests. A mapping fix bumps the weights/composer version stamps so
logged results stay attributable ([[Frozen Version Stamps on Logged Results]]). It does
not bump the schema version, because the shape didn't change.

## Bin 2: weighting and taste (build the switch, not the answer)

These were the overlap between mood bundles (Jaccard 0.2 for three pairs, compounded by
the adjacency graph), how a jump to "high" specificity disables discovery and lifts
repetition limits, and how the sparse-evidence penalty should behave. Each is real. None
can be settled without judged data.

The build for this bin:

- **A variant registry** that mirrors the existing prompt-variant registry for
  enrichment ([[Offline Prompt Experiment Runner]]). Each knob is a named variant, not an `if` buried in a dimension.
- **A control arm named for what it is** (`production` / `current_behavior`) that is
  **byte-identical** to today's code path. A parity test pins this, so turning the
  registry on changes nothing until a treatment is chosen.
- **`resolveVariants()` throws on an unknown id.** A typo in an experiment config must
  fail loudly instead of falling back to control and reporting a null result.

### Registry shape (from the build plan)

- **A folder of axes, not one file.** The first treatment set (uncertainty handling) was
  planned as a flat file. It was restructured into `variants/` with an `index.ts` holding
  an `axis → { variants, defaultId }` map and one file per axis. Two sibling issues could
  then add their own axes (weights, specificity, mood mapping) without editing each
  other's file. The axis type is generic over input and output, so a new axis is not
  forced into the first axis's contract.
- **The control arm calls the real production logic.** The penalty computation was
  extracted into a function that both production and the `current_behavior` arm call.
  The control arm is a reference, not a copy, so it cannot drift.
- **Treatments take already-computed dimension results.** Each one is a five-line pure
  function over dimension outputs and flags. It does not re-run the dimension internals.
  The control arm can then pass values straight through, which makes it provably
  identical to production.
- **Each variant names the version stamp it would bump if promoted** (here the ranker
  version, not the weights version). The comparison report can then say which stamp to
  bump without working it out again.
- **New structured fields stay out of serialized output.** The added `zero_reason` was
  set with a conditional spread (`...(x ? { x } : {})`), never `x: undefined`, so no
  existing deep-equality assertion picked up an unexpected key. One regression test pins
  that the field never reaches the served row. Checking by inspection is a weaker
  guarantee than a test that fails when the behaviour changes.

### Narrow the defect fix to the proven-wrong case

The weekday/weekend mapping fix first suppressed the weekend tag whenever the request's
date was missing. On refine this was reversed. The tag is suppressed only when the date
*resolves* to a known non-weekend day. An unknown date keeps today's behaviour. A defect
fix should change only the case shown to be wrong, not the "we don't know" case next to
it. A test asserts that the unknown-date case still gets the tag, so keeping that
behaviour is visible and deliberate.

### When the corpus lands

When the corpus lands, the decision becomes "compare arms that already run". It is no
longer a build. This mirrors [[Shadow Signal Before Gate Change]]: put the alternative in
place at zero effect, measure, then flip.

The follow-up plan wrote down the promotion rules ahead of time:

- Measure each treatment alone. Do not combine treatments into one arm before each has
  been measured on its own.
- Report the affected moment slice next to the aggregate. An overall win does not excuse
  a regression in the slice the mapping actually touches.
- A treatment is promoted only if it does not raise bad-in-top-5. If none clears the bar,
  record "keep" and change nothing.
- Variant plumbing can be built before labels exist, because it is offline and needs no
  judged rows. Promotion cannot. Having the tooling is not the same as having the
  evidence.

## Why the split matters

Mixing the bins causes two failures. Shipping a weighting change now, as if it were a
defect fix, re-baselines every ranked result on a guess. Waiting for the benchmark to fix
a defect leaves a known-wrong mapping in production. Sorting first lets each claim take
its proper path.

## See Also
- [[Taste vs Defect Verdict Split]] — extends (the same taste/defect split, applied to scoring claims instead of review verdicts)
- [[Frozen Ranking Baseline from a Pure Ranker]] — prerequisite-for (the offline harness that compares the arms)
- [[Shadow Signal Before Gate Change]] — related (zero-effect alternative first)
- [[No Evidence Ranks Below Confident Mismatch]] — instance-of (one knob built this way)
- [[UNGATED Metric Convention]] — related (measure before thresholding)
- [[Offline Prompt Experiment Runner]] — related (the enrichment prompt-variant registry this mirrors)
- [[Characterization Pins Before Extraction]] — related (control-arm-equals-today applied to a refactor's default policy)
