---
title: Frozen Ranking Baseline from a Pure Ranker
tags: [eval, foundations, pattern]
summary: Because the ranker and composer are pure functions, an offline "snapshot in, ranked slate out" baseline is a composition of three things the tree already has — not new infrastructure — and the genuinely missing pieces are an export that keeps excluded candidates with their reason, a slice-breakdown layer over the per-case grade file, and a version stamp for every rule table.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/diskoe/docs/research/2026-09-16-dis290-frozen-ranking-baseline.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-16-dis289-relevance-benchmark-corpus.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-10-results-surface-design.md
  - data/raw/claude-docs/playground/docs/research/2026-09-10-results-surface-design.md
  - data/raw/claude-docs/akira/docs/research/2026-09-16-dis290-frozen-ranking-baseline.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-16-dis290-frozen-ranking-baseline.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis290-frozen-ranking-baseline.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis290-frozen-ranking-baseline.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis290-frozen-ranking-baseline.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis290-frozen-ranking-baseline.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis290-frozen-ranking-baseline.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis292-intake-scoring-semantics-continuation.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis292-intake-scoring-semantics-continuation.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis292-intake-scoring-semantics-continuation.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis292-intake-scoring-semantics-continuation.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis292-intake-scoring-semantics-continuation.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis289-relevance-benchmark-corpus.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis289-relevance-benchmark-corpus.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis289-relevance-benchmark-corpus.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis289-relevance-benchmark-corpus.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis289-relevance-benchmark-corpus.md
---

# Frozen Ranking Baseline from a Pure Ranker

Research for a dated ranking baseline (NDCG@5, pairwise accuracy, recall-of-relevant,
bad-in-top-5, eligibility correctness, slate quality) on a deterministic recommender
(repo diskoe/akira). The headline finding was that almost nothing needed to be built from
scratch — and that the small pieces that *were* missing had been hiding behind things that
looked covered.

## Purity is the eval harness

`rank(candidates, context)` and the composer take no I/O: time, viewport and seed are
inputs, and the header states the determinism contract. That is what [[Replayable Slate Ranker]] buys at eval time: an offline execution path already existed (a recommendation-
quality metric and a `compare-rankers` dev script), a snapshot exporter already existed,
and the harness's per-case shape (`EvalCase → GraderResult{isCorrect, score, dimensions}`)
already carried multi-number, per-item results. Freezing a baseline is **composing** those
three and pointing them at judged moments instead of golden fixtures. A "case" becomes one
judged moment rather than one judged item; NDCG@5 goes in `score`, the other ranking
numbers ride in `dimensions`, and the existing pass-rate summariser yields a defensible
gate value ("fraction of moments clearing NDCG ≥ x") without a new grader kind.

## What was genuinely missing

- **Hard-filter-then-tag, not hard-filter-then-drop.** The snapshot exporter queried
  `published` server-side and then re-applied the hard filters, keeping only survivors. The
  eligibility-correctness metric needs exactly the rows it discarded — the wrong-district,
  missing-display-data and expired candidates — judged as "should have been excluded".
  Keep every candidate the pool query returns and record `hardFilterReason()` (or `null`)
  alongside it. Exclusions tallied as counts without identity cannot be judged.
- **Slice breakdown.** Every metric was to be reported by specificity, content kind,
  district density and completeness. Nothing in the report or gate code grouped by
  `EvalCase.metadata`; but the per-case `graded.jsonl` already carried `caseId`, metric and
  grades, so slicing is an additive script over an existing output file, not a change to
  the grading loop.
- **A version constant for every rule table.** Five of six stamps existed as named
  constants; the specificity classifier had a point table and no version. The issue's text
  also claimed serving logs carried `prompt_hash`; they did not — the hash lived per
  enrichment row and had to be pulled onto the snapshot from there. Another stamp was
  populated from a differently-named constant (`diversification_version` ← `composer_version`),
  a naming mismatch that is harmless until a join fails silently. See [[Frozen Version Stamps on Logged Results]].
- **The field contract with the labelling side.** The one thing to agree before either
  side writes code: does `candidate_id` equal the scoring candidate's id for *every*
  content kind, and do the judgment rows' "frozen versions" field names match the stamps the
  snapshot emits. A mismatch surfaces only as an unexplained join failure months later.

## Two halves of slate quality, gated differently

Structural slate quality (diversity, non-repetition, role coverage) is a heuristic grader
over the composition's slots and needs no judgment data. Subjective slate quality
(useful, actionable) is an LLM-judge metric — registered, but its threshold left commented
until agreement with human labels has been measured. Same rule as [[UNGATED Metric Convention]]: a metric tuned against the fixtures that grade it stays ungated until an
independent signal exists.

## Build on fixtures, wait only for the number

Every mechanism — snapshot export, metric functions, graders, the variant-compare command
— is buildable now against hand-authored synthetic judged moments, exactly as earlier
metrics shipped UNGATED before real data existed. Only the dated baseline *number* and any
`targets.yaml` threshold wait on the real judged corpus, because the repo rule is that a
threshold is written from an observed pass rate. The variant-compare command reuses an
existing experiment runner's ([[Offline Prompt Experiment Runner]]) manifest → run → resumable JSONL → report skeleton with its
spend-ledger machinery removed, since ranking has no paid call. A separate de-identified
replay corpus (retaining old serving rows) answers "what happens to old rows", not "how do
I freeze a snapshot" — orthogonal, not a dependency.

## Decisions from the build plan

The plan that followed the research added a few decisions the research could not make:

- **Phase by dependency, not by evaluation family.** The pure metric functions (NDCG@5,
  pairwise accuracy, recall, bad-in-top-5, slate diversity) and the eligibility grader had
  no dependency on the labelling side and shipped as Phase 1. Grader wiring, which imports
  the judgment contract and the shared full-breakdown function, came second. The
  variant-compare CLI came last. Each phase was a review boundary and could be reverted
  alone.
- **One execution seam, accepted as a cost.** Every grader runs the pipeline through the
  single `computeFullBreakdown` function owned by the labelling plan, rather than three
  separate `rank()`/composer call sites. That made Phase 2 wait on the other plan even
  though some of the math did not need it. The plan took that delay over three copies of
  the same pipeline wiring.
- **Static import over a soft import.** The first draft loaded the sibling variant
  registry with a `try/await import()` that degraded silently if the module was missing.
  Once the registry's shape was settled, this became a static import and a declared hard
  build-order dependency. A dynamic import that quietly no-ops when its target is absent
  is the silent-failure shape the repo bans elsewhere. The "degrades gracefully" test was
  replaced by one asserting that an unknown `--axis`/`--variant` is rejected loudly.
- **Bookkeeping thresholds are labelled as such.** A per-moment pass mark
  (`NDCG ≥ 0.7`) and a relevance floor for recall (grade ≥ 2 on a 0–3 scale) shipped as
  tunable constants, only to fill `isCorrect` for pass-rate reporting. Because the metrics
  are ungated, a wrong default costs a misleading console number and nothing more.
- **The subjective judge is doubly blocked.** Its `targets.yaml` line stays commented
  until both the real corpus exists *and* a human-agreement (κ) measurement exists for
  that instrument. The corpus landing alone does not unblock it.
- **Decide per mapping, by slice.** A later plan used the CLI to judge four mapping
  changes one at a time. Each treatment is measured alone before any are combined. A win
  has to show up in the affected moment slice as well as overall, and must not raise
  grade-0-in-top-5. "Keep" (no change) is a valid recorded result. Tooling existing in
  code was explicitly not counted as evidence collected.

The build also turned up a dormant bug. An existing dev script called its own `main()` at
module scope, so importing one helper from it ran that script against the importer's argv.
It printed a second error and exited 1 after the new CLI had already succeeded. The fix
was the same entry-point guard its sibling scripts already used.

## See Also
- [[Build the Knobs, Not the Choice]] — related (the variant registry this CLI enumerates)
- [[Eval Falsifiability]] — related (fixtures must disagree with the ranker somewhere, or NDCG passes by construction)
- [[Replayable Slate Ranker]] — extends (purity is what makes the offline baseline a composition rather than a build)
- [[Frozen Version Stamps on Logged Results]] — complements (the stamps the snapshot must carry to join judgments)
- [[UNGATED Metric Convention]] — instance-of (register everything now, threshold only from an observed rate)
- [[Append-Only Human Labels]] — prerequisite-for (the judgment rows this baseline is scored against)
- [[Write-Only Fields and the Reader Map]] — related (the exporter that dropped the rows a reader needed)
- [[REUSE/ADAPT/SKIP Asset Verdicts]] — related (the per-asset verdict table that found the three reusable pieces)
- [[Offline Prompt Experiment Runner]] — extends (the manifest → run → JSONL → report skeleton reused here)
- [[Stratified Judgment Pool for a Ranker Benchmark]] — extends (how the judged corpus was actually built and what its first real run broke)
