---
title: Prototype Pipeline Handoff Signals
tags: [meta, pattern]
summary: Four signals a prototyping pipeline should emit explicitly rather than leave for the operator to notice — a DESIGN.md that has outgrown its frame should hand off to a document split; execute steps for agent work must name their metric and GATED/UNGATED status at step time; the pipeline exit should generate the change-contract skeleton the review stage depends on; and a codebase audit precedes any plan.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/galactus/docs/research/2026-08-29_diskoe-parity_proto-pipeline.md
---

# Prototype Pipeline Handoff Signals

A parity study compared a project built by hand with what the `/proto-*` pipeline would
have produced, and found four places where the pipeline *knew* something had changed and
said nothing.

## 1. DESIGN.md outgrowing its frame → emit a split signal

The hand-built project ended up with four documents (scope / requirements / roadmap /
data-model) after a single design doc produced an **ID namespace collision** — requirement
ids and data-model ids sharing a prefix. The pipeline's `/proto-design` writes one
[[DESIGN.md Artifact]] in a five-layer frame and has no notion of "too big". Proposed:
when a layer exceeds a size or id-count threshold, the skill emits a handoff signal
("this design wants to be N documents") rather than growing the single file until the
collision happens.

## 2. Eval from day one → name the metric at step time

Retroactive evals were cheap in the hand-built project *only because* it had kept pure
functions free of I/O from the start — a design choice, not luck. The pipeline should
make it a requirement: `/proto-execute` for `Track: agent` (see
[[Auditable Track Router]]) requires each step to **name its metric and declare GATED or
UNGATED** when the step is written. Unmeasured metrics stay commented out and report
UNGATED, so a missing eval is a visible line, never an absent one — the review-side
convention described in [[RAG Eval Gate Contract]].

## 3. The review stage depends on a file nothing creates

The `review-contracts` dimension activates only if `SANYI.md` exists. No pipeline step
creates one. Result: the contract review silently never ran on pipeline-built projects —
an unrun-scan-as-clean-scan at pipeline scale ([[An Unrun Scan Is Not a Clean Scan]]).
Proposed fix: a pipeline **exit step generates a skeleton** change-contract file, so the
downstream stage's precondition is produced by the stage before it rather than assumed.
See [[SANYI Change-Contract System]].

## 4. Audit before plan

The hand-built project's first move was a codebase audit (what exists, what is tested,
what is wired); the pipeline goes research → plan with no audit stage. Adding the audit as
the planning skill's first required input is the same move as
[[Capability Parity Audit]] — know the have/partial/gap table before deciding what to build.

## See Also
- [[SANYI Change-Contract System]] — extends (the skeleton the pipeline should emit)
- [[DESIGN.md Artifact]] — extends (when one design doc should become several)
- [[An Unrun Scan Is Not a Clean Scan]] — instance-of
- [[RAG Eval Gate Contract]] — extends (GATED/UNGATED declared at execute time)
- [[Capability Parity Audit]] — extends
- [[Auditable Track Router]] — extends
- [[Three-Doc Spec Split]] — extends (the document split the handoff signal should point at)
- [[UNGATED Metric Convention]] — extends (the convention execute-time naming enforces)
- [[Four-Stage Design Pipeline with Backflow]] — extends
