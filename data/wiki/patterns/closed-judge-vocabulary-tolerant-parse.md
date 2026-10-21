---
title: Closed Judge Vocabulary, Tolerant Parse
tags: [patterns, eval, pattern]
summary: "An LLM judge's free-text issue list cannot be trended across prompt versions (108 distinct strings over 40 rows). Close it to a fixed code set, but parse leniently: accept free strings, map them through a synonym table to canonical codes, keep an `other` escape valve, and never ask the judge to name what a deterministic layer already records."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-23-dis373-venue-probe-v3.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-23-dis373-venue-probe-v3.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-23-dis373-venue-probe-v3.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-23-dis373-venue-probe-v3.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-23-dis373-venue-probe-v3.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-24-dis375-venue-probe-eval-metric.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-24-dis375-venue-probe-eval-metric.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-24-dis375-venue-probe-eval-metric.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-24-dis375-venue-probe-eval-metric.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-24-dis375-venue-probe-eval-metric.md
---

# Closed Judge Vocabulary, Tolerant Parse

A venue-enrichment probe (repo akira, 2026-09) had an LLM judge that returned an open
`issues: string[]` field. Over 40 rows it produced **108 distinct strings**. A defect list
like that cannot be counted, compared across two prompt versions, or registered as an eval
metric. Closing the vocabulary was a prerequisite for the follow-up issue that registered
the metric.

## The mechanism

- **Do not make the field an enum in the schema.** One unrecognised string would fail the
  *entire* judge parse and discard four good scores over one bad label. Parse `issues` as
  free strings, as before.
- **Map at parse time.** Every entry goes through a synonym table to a canonical code. The
  canonical set and the mapping live in one module, so the grader downstream imports one
  constant, not two.
- **Keep an `other` escape valve.** A fully closed set fails the day a real defect does not
  fit, and that is worse than an occasional `other`.
- **Widening is additive. Renaming is a version bump.** New codes or synonyms need no judge
  version change. Only removing or renaming a code does.
- **Seed it from what you can read, and reconcile later.** The 108 raw strings lived only in
  one operator's gitignored notebook. The starter set came from the five documented defect
  families (hallucination, generic or vague, empty output, facts only, calibration) plus the
  six example codes the rubric prompt already used. Reconciling against the raw corpus was
  logged as an operator follow-up, not a blocking step.
- **Do not ask the judge for facts a deterministic layer already has.** The judge used to
  emit `vocabulary_gap:<word>`. The output parser already produced a structured `dropped[]`
  entry for every out-of-vocabulary tag, so the code was removed from the judge's job.
  Asking a model to restate a structural fact in free text is how a judge vocabulary bloats.

## What it enabled

The next plan registered two UNGATED metrics on the probe. One grades the heuristic flags
against a committed 40-row fixture corpus. The other grades the verdict combiner against
the judge's recorded `pass` bit. Both import the closed vocabulary instead of re-deriving it.
The same move appears in ingestion detectors that write to a closed issue store rather than
a log ([[Layered Ingestion Failure Posture]]).

## See Also
- [[LLM-as-Judge Evaluation]] — extends (judge output design: structure the defect list, not just the score)
- [[Layered Ingestion Failure Posture]] — instance-of (closed issue vocabulary for detectors, same reason: countable and trendable)
- [[Verbatim Evidence Quote Verification]] — related (shipped in the same probe version)
- [[UNGATED Metric Convention]] — prerequisite-for (the metric registered on top of the closed set)
- [[Widen a Capped Vocabulary Without Displacing]] — related (additive vocabulary change on the model side)
- [[Closed-Vocabulary Parser Silently Drops Invented Types]] — extends (the same failure in a link parser)
