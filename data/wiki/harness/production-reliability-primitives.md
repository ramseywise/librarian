---
title: Production Reliability Primitives
tags: [llm, agents, infra, pattern]
summary: "Four unglamorous mechanisms that keep a Stage 2–3 harness running under real traffic — per-step checkpointing, cross-provider fallback, fail-fast on ambiguity, and confidence-routed quarantine."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness--notes--08-maturity-and-failure-modes.md
---

# Production Reliability Primitives

The maturity ladder in [[Harness Maturity and Failure Modes]] says *what* to build. These are
the mechanisms that keep a Stage 2–3 harness running **once real traffic hits it**. All four
come from one production case study, and **all four are unglamorous**.

## Resume From the Failed Node

State persisted **after every step** means a failure resumes from that step instead of
restarting the workflow. The reported implementation checkpoints agent state to Postgres via
a LangGraph checkpointer, with application-level state (logs, intermediate steps, citations)
kept separately in DynamoDB.

Three payoffs, in **ascending order of importance**:

1. **Cost** — completed steps aren't re-executed or re-billed.
2. **Latency** — recovery is proportional to *what remains*, not what was attempted.
3. **User-initiated retry becomes viable** — a user can retry a failed query and the system
   continues from the failure point.

The third is the real one. Without checkpointing, *"retry"* means *"start the multi-minute
workflow over,"* **which nobody does twice**.

This is state externalization (see [[Long-Horizon Execution]]) arriving for a different
reason: not context-window survival, but **failure recovery**. The same mechanism buys both —
**a good sign it's the right primitive.**

## Cross-Provider Model Fallback

When a model fails after its retries, fall back to **a different model, ideally on a
different provider**. Retrying the same endpoint cannot fix a provider outage — and
**provider availability is outside your control, so it must be designed around rather than
monitored**.

The enabling detail is boring and load-bearing: every model sits behind **a single
OpenAI-compatible endpoint**, which is what makes swapping one for another a **config change
rather than an integration**.

> **Uniform interface first, fallback policy second.**

Extends the retry table in [[Agent Retry Taxonomy]] — this is what the *Fatal* row escalates
to when the failure is the provider rather than the request.

## Fail Fast on Ambiguity

Rather than trial-and-error across every data source, the system **asks a clarifying question
when intent is ambiguous** — and offers AI-suggested sources the user can accept, adjust, or
override.

> **A clarifying question is cheaper than a wrong execution, but only if it's rare.**

**Both halves matter.** The gate must trigger on genuine ambiguity and stay silent when
intent is clear, or it becomes **friction users learn to click through** — the same
false-positive economics that killed the SQL reviewer in [[Verification Loops]].

Note the default: **the machine proposes, the domain expert disposes.** This is the
*search → ask → act* protocol from [[Execution Boundaries and Guardrails]] with a concrete
UI.

## Confidence-Scored Automation With a Quarantine Lane

For a metadata-enrichment pipeline, each extracted field is scored and **routed by
confidence**: high-confidence fields apply automatically, low-confidence fields are
**quarantined for human review**.

This is the generalizable shape for **HITL at volume**. Full automation is unsafe and full
review doesn't scale, so **the threshold decides which regime each item lands in** — and
human attention concentrates where the model is *uncertain*, which is where it's most likely
wrong.

The threshold is a tunable knob, and **moving it as measured accuracy improves is the ratchet
running in the direction of less human work.**

## See Also
- [[Iterative Harness Simplification]] <!-- auto-linked -->
- [[Runtime Topology and Checkpointer Alignment]] <!-- auto-linked -->
- [[Harness Maturity and Failure Modes]] — part-of
- [[Long-Horizon Execution]] — complements
- [[Agent Retry Taxonomy]] — extends
- [[Execution Boundaries and Guardrails]] — complements
- [[Harness Engineering]] — instance-of
