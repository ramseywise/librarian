---
title: Safeguards Architecture — Five Protection Layers
tags: [infra, llm, pattern]
summary: Five-layer runtime safety pipeline for production agents — input guardrails, routing confidence, retrieval quality (CRAG), post-generation grounding check, and escalation routing — each with distinct latency cost and failure mode.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/playground/docs/support-agents/invocation-flow.md
  - data/raw/claude-docs/playground/docs/support-agents/safeguards-architecture.md
  - data/raw/claude-docs/project-g/docs/support-agents/invocation-flow.md
  - data/raw/repos/playground/.claude--docs--support-agents--safeguards-architecture.md
  - data/raw/claude-docs/project-g/docs/support-agents/safeguards-architecture.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--system-design-round--examples--support-agent.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--examples--support-agent.md
---

# Safeguards Architecture — Five Protection Layers

Every production agent passes through up to five protection layers before a response reaches the user. Each layer addresses a different failure class, runs at a different point in the pipeline, and has distinct latency characteristics.

## The Five Layers

```
Layer 1:  Pre-input     — injection + PII guardrail (<1ms, deterministic)
Layer 2:  Pre-retrieval — routing confidence gate (0ms, threshold check)
Layer 3:  Pre-generate  — retrieval quality gate / CRAG (0–300ms)
Layer 4:  Post-generate — structural citation check (<1ms, deterministic)
Layer 5:  Escalation    — friction signal routing (0ms, threshold + regex)
```

## Layer 1 — Input Guardrails

See [[Input Guardrails Pipeline]] for the full 7-stage spec. Key properties:
- LLM-free and deterministic
- Covers: normalisation, size check, domain classification, injection detection, PII redaction
- Latency: <1ms total

## Layer 2 — Routing Confidence Gate

Intent classification produces a confidence score. Below threshold, the query is routed to a safe default (clarification request or generic response) rather than a domain agent.

- Implementations: `_route_intent` threshold (LangGraph), `_llm_classify` fallback (ADK)
- Failure mode caught: low-confidence queries routed to wrong domain agent

## Layer 3 — Retrieval Quality Gate (CRAG)

Pre-generation check on retrieved passages. If top passage confidence is below threshold, the pipeline re-retrieves or falls back.

- See [[CRAG Retry Logic]] for the conditional back-edge pattern
- Implementations: `confidence_gate` in LangGraph, not yet ported to ADK
- Failure mode caught: generation from irrelevant/poor passages

## Layer 4 — Post-Generation Grounding Check

Structural citation verification — no LLM calls, runs in <1ms. Three tiers:

| Tier | Check | On fail |
|---|---|---|
| **1** | Cited URLs/IDs exist in retrieved set | Hard fail → escalation |
| **2** | Claim-level citations declared in response array | Hard fail → escalation |
| **3** | Supporting quotes appear verbatim in cited passage (token overlap) | Soft — log/warn |

Additionally: missing citation guard (KB called but no citations + no `insufficient_information` → hard fail).

**Key design choice:** Use a dedicated `grounding_check` node (LangGraph) or `after_agent_callback` (ADK) — not embedded in format logic. Single responsibility, toggleable via env flag, independently testable.

**Do NOT use LLM-as-judge for runtime grounding.** Semantic grounding evaluation belongs in the offline eval pipeline ([[project-g Eval Architecture]]), not the hot path. Runtime check must be structural and sub-millisecond.

**When the response is streamed**, this layer cannot simply inspect a finished string — see [[Streaming Output Scrubbing]] for the transform-in-transit seam and the carry-window technique that keeps a post-generation guard compatible with token streaming.

### Where the structural check is blind

- **Tier 3 being soft-only lets fabricated quotes through.** The check with the most
  meaning (is the quote verbatim in the passage?) never escalates. A supporting quote
  with zero token overlap still passes. Make `score == 0` a configurable hard fail.
- **Self-rated relevance below threshold only logs.** It should be a configurable gate.
- **The missing-citation guard needs a KB that returns results.** If the KB always
  returns poor passages, the model answers from memory and the guard never fires. A
  retrieval-side gate (CRAG) is the complementary check: grounding rejects bad answers,
  but improves nothing before generation.
- **Schema coupling fails silently.** A bare `catch {}` around claim parsing swallows
  errors when the `citations`/`claims` keys change. At the very least, log them.
- **Failures that only reach the console** never feed dashboards or the eval pipeline.

## Layer 5 — Escalation Routing

Aggregates signals from all prior layers plus explicit user requests:
- Direct escalation regex ("talk to a human")
- Grounding failures (Layer 4 hard fail)
- Repeated low-confidence routing (Layer 2)
- Coverage gaps detected by Layer 3

**Gap:** Currently regex-only in most implementations. Not yet wired to aggregate grounding failures or low-confidence signals as compound escalation triggers.

## Confirm Gate for Write Operations

A `confirm: bool` field in the response schema gates nothing unless the write path uses
it. The two-phase design:

- **Phase 1:** asked to edit a record, the agent does **not** call the write tool. It
  summarizes the intended change, sets `confirm: true` and stores the planned tool call
  as `pending_action` in session state.
- **Phase 2:** the next user turn contains an affirmation after a `confirm: true` reply,
  so the agent executes the stored `pending_action`.

The approval lives in session state across turns, not in the model's memory of the
previous message.

## Latency Budget

| Path segment | Typical cost |
|---|---|
| Input guardrails (L1) | <1ms |
| Retrieval + rerank | 500–1500ms |
| LLM generation | 800–2000ms |
| Grounding check (L4) | <1ms |
| Score delta guard (skip second LLM) | saves 1–2s |

## Metrics Unlocked by Instrumentation

Runtime grounding logging (Layer 4) enables metrics impossible with offline-only eval:

| Metric | What it reveals |
|---|---|
| `grounding.hallucination_rate` | % citing un-retrieved passages |
| `grounding.missing_citation_rate` | % KB-answered turns with no sources |
| `grounding.escalation_rate` | % rewritten to escalation |
| `grounding.zero_score_claims` | % fabricated claims (no token overlap) |

## TS/Python Parity Status

Full parity achieved on: sanitize, PII redaction, injection detection, score delta guard, word-boundary quote check, grounding subpackage, typed GroundingResult.

Gaps: context caching (TS only), multi-language escalation (Python: 7 langs, TS: 9 langs).

## See Also
- [[Input Guardrails Pipeline]] — prerequisite-for
- [[Bounding Agents Rather Than Trusting Them]] — prerequisite-for (the design stance these layers implement)
- [[CRAG Retry Logic]] — instance-of (Layer 3)
- [[project-g Eval Architecture]] — extends (offline complement to runtime layers)
- [[Grounding Claim Methodology]] — extends (the eval-side semantic grounding)
- [[HITL and Interrupt Patterns]] — alternative-to (Layer 5 escalation)
- [[Streaming Output Scrubbing]] — extends (Layer 4 under token streaming)
- [[Payload Security Defects at Canon]] — related (defects in the shipped payload, not the runtime layers)
- [[AIE Code-Test Flaw Taxonomy]] — instance-of (the hand-rolled subset of these layers, under a timebox)
- [[Multi-Agent Context]] — extends (sub-agent isolation as a containment boundary for untrusted content)
- [[Execution Boundaries and Guardrails]] — related (part of; the five layers sit inside the harness's boundary layer)
- [[Canary Testing for Permission Boundaries]] — extends (testing that a deny rule actually fires)
- [[Agent Security Risk Taxonomy]] — related (the risk classes these layers mitigate, and why mitigation distributes)
- [[Score-Delta Retry Guard]] — prerequisite-for (the score delta guard in detail)
- [[Prompted Reflection vs Graph-Gated CRAG]] — extends (in-flight reflection does not replace Layer 4 grounding)
- [[Warranted vs Executed Escalation]] — extends (score-floor escalation enforcement and how escalation is graded)
- [[System Design Interview Study Guide]] — instance-of (the support-agent worked example rehearses these layers)
- [[The Augmentation Gate]] — instance-of (Layer 3, the retrieval quality gate)
