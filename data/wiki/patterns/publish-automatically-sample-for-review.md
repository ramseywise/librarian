---
title: Publish Automatically, Sample for Review
tags: [patterns, eval, pattern]
summary: "Instead of gating every item behind human review, publish automatically and draw a random sample at publish time for an operator to grade pass/fail. Each failure is attributed to a pipeline stage, so the sample measures quality per stage without blocking throughput."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-08-26-b4b-sampling-loop.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-26-b4b-sampling-loop.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-26-b4b-sampling-loop.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-26-b4b-sampling-loop.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-26-b4b-sampling-loop.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-26-b4b-sampling-loop.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-26-b4b-sampling-loop.md
---

# Publish Automatically, Sample for Review

This comes from a sampling-loop plan in the akira event pipeline. The pipeline moved from
reviewing every item before publish to a post-hoc audit: items go live automatically, and a
random fraction is queued for an operator to check.

## Mechanism

- **Sample at publish, atomically.** When an event is published, a random 10% are written to a
  `quality_samples` table in the same transaction as the publish. A sample cannot exist for an
  unpublished event, and every published event has had exactly one roll.
- **One sample per event, ever.** A unique constraint stops re-publishes and re-runs from
  sampling the same event twice and skewing the rate.
- **The verdict is pass/fail plus a stage.** The operator records pass/fail and a
  `failure_stage` ∈ {`extraction`, `enrichment`, `qc`, `none`}. Each value maps to a pipeline
  stage, so the failure rate breaks down by the component that caused it, not just "quality is
  80%".

## Risks the plan named

- **Stage misattribution.** The stage is chosen by hand. An operator who blames enrichment for an
  extraction miss pollutes the per-stage signal. The vocabulary is kept small to limit this.
- **`Math.random` is untestable.** A raw random call inside the publish path cannot be
  asserted on. Inject the sampler (or the rate) so tests can force a sample or skip one.
- **Expect zero samples at small scale.** At 10% of a handful of publishes a day, early weeks
  will often show no samples. That is arithmetic, not a bug, and it is not evidence that quality
  is fine.

## Why post-hoc

A review on every item makes human attention the throughput limit and puts off publishing until
someone looks. Sampling separates **measuring** quality from **gating** on it. The pipeline
ships, and the sample estimates how often it ships something wrong, broken down by where the
error came from.

## See Also
- [[Online Eval Sampling]] — instance-of (production sampling for a human grader)
- [[Manual Review as Eval Bootstrap]] — extends (the sample becomes the labelled set)
- [[Advance-Only Machine Writes on a Shared Lifecycle]] — related (the same pipeline's publish transition)
