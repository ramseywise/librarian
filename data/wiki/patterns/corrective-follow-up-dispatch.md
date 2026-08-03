---
title: Corrective Follow-Up Dispatch
tags: [llm, pattern]
summary: Gated subagents that a signal-detection pass failed to trigger get dispatched in a second round when always-on subagents report out-of-dimension signal — treating reviewer observations as a recovery path for missed conditional dispatch.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/Parallax/agents/parallax.md
  - data/raw/claude-docs/Parallax/agents/intent-correctness.md
  - data/raw/claude-docs/Parallax/agents/reliability-operations.md
  - data/raw/claude-docs/Parallax/agents/security-privacy-data.md
  - data/raw/claude-docs/Parallax/agents/architecture-docs.md
  - data/raw/claude-docs/Parallax/agents/accountability-safeguards.md
  - data/raw/claude-docs/Parallax/agents/sanyi-review.md
---

# Corrective Follow-Up Dispatch

Conditional dispatch (see [[Parallel Dimension Scanner Architecture]]) has a failure mode:
if the signal-detection pass misses, the gated dimension never runs and the review is
silently narrower than it appears. Parallax closes this with a second dispatch round
triggered by the reviewers themselves rather than by a better detector.

## The instruction that makes it work

Each always-dispatched subagent (`intent-correctness-review`,
`reliability-operations-review`, `security-privacy-data-review`, `architecture-docs-review`)
carries the same clause in its prompt:

> If you notice agent-system signals (LLM SDK imports, prompt files, agent framework code,
> etc.) not already accounted for, flag this explicitly in your returned output **rather
> than staying silent because it's outside your assigned dimension**.

This deliberately overrides the single-concern discipline that motivates dimension
splitting. The scanner stays focused for *finding* purposes but is licensed to report one
specific class of out-of-scope observation: evidence that another dimension should have
been dispatched.

## Two triggers

The orchestrator dispatches `agent-runtime-tooling-review` and
`accountability-safeguards-review` as a corrective round when either holds:

1. **Explicit flag** — any always-dispatched subagent reports agent-system signals that
   Stage 0 detection missed.
2. **Convergence** — two or more always-dispatched subagents independently flag
   agent-system signal in the same round, even without an explicit miss claim.

The rationale for the second is stated in the source: the regex-based `detect-signals`
fallback "is not exhaustive, and convergent manual signal from multiple reviewers is itself
high-confidence evidence." Independent agreement among agents that were not asked the
question is treated as a stronger detector than the deterministic check designed to answer
it.

Every corrective round obeys the same foreground/single-message dispatch rule as the first
— the constraint applies "to every dispatch round, not just the first."

## Cross-subagent routing

The pattern also chains between gated subagents. When
`accountability-safeguards-review` flags an undeclared safeguard gap and `SANYI.md` exists,
the orchestrator dispatches `sanyi-review` as a follow-up **with that finding as input**,
asking it to draft a candidate contract entry.

This is a deliberate capability split. The safeguards subagent is told to describe the gap
but "do not attempt to draft SANYI.md syntax yourself; you do not have SANYI's contract
format preloaded" — only `sanyi-review` carries the [[SANYI Change-Contract System]] format
in context. The finding travels to the agent that can express it rather than every agent
carrying every schema. The draft remains a recommendation; writing it into `SANYI.md`
requires explicit human approval.

## Why this shape

A missed conditional dispatch is invisible in the output — the report simply lacks a
section, which reads identically to "that dimension found nothing." Making reviewers
responsible for reporting suspected gaps converts a silent omission into a recoverable
one, at the cost of a second round's latency. It is the dispatch-level analogue of the
prose-only-safeguard check in [[Agent Quality Review Checklist]]: don't trust that a
guarantee fired, look for evidence of it.

## See Also
- [[Parallel Dimension Scanner Architecture]] — extends
- [[Deterministic Review Substrate]] — extends
- [[SANYI Change-Contract System]] — extends
- [[Agent Quality Review Checklist]] — extends
- [[Agentic Workflow Patterns]] — instance-of (routing)
- [[Shared Context Brief]] — prerequisite-for (second round reuses the same brief)
- [[Parallax]] — instance-of
