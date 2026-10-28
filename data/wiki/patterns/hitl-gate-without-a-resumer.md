---
title: HITL Gate Without a Resumer
tags: [patterns, rag, pattern]
summary: An interrupt() gate only earns its place when someone actually resumes the run; in an autonomous pipeline every gate collapses to auto-escalate, sequential gates compound the fire rate, and thresholds should be calibrated to a target escalation rate rather than a score value.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/playground/docs/research/rag/rag-integration-strategy.md
---

# HITL Gate Without a Resumer

From a playground research doc (2026-04) that reviewed a LangGraph support-RAG agent
before deciding how to wire it into a domain-routed virtual assistant. The agent had two
confidence gates built on `interrupt()`: one after retrieval, one after reranking. Each
paused the run so a caller could refine the query, proceed or escalate.

## The mechanism

An `interrupt()` gate is a promise that **something will resume the run**. That
something is a supervising human or a consuming agent that knows how to inject a refined
query. In a customer-facing autonomous chatbot nobody resumes. The gate then degrades to
whatever the fall-through path is, which in this case was escalation. So:

- **In supervised mode** (a human reviewing a support queue), two gates are smart: one
  chance to intervene before the expensive rerank, one after.
- **In autonomous mode**, both gates produce the same outcome, which is escalate. The graph
  carries wiring and latency for a branch that never does anything useful. The leaner
  graph has one `confidence_gate` after reranking, and a low-confidence route goes
  straight to escalation.

The deciding question is not about architecture: *is there a resumer consuming the
interrupts?* If yes, keep the gates. If no, replace them with auto-escalation and pass the
confidence score up in the response payload. The calling layer (the VA) can then decide
to escalate without needing any HITL resumption logic.

## Sequential gates compound

Two independent gates that each fire 15% of the time fire about 28% of the time
combined. The two signals are correlated in practice, because weak retrieval usually means
a weak rerank as well, so the real rate is lower. It is still enough to matter for
high-volume support. Each gate you add makes it more likely that at least one fires.

## Calibrate to an escalation rate, not a score

The gate thresholds (RRF 0.4, sigmoid cross-encoder 0.25) had no corpus-specific
justification. RRF scores depend on corpus size and `rrf_k`, and with a passthrough
reranker the sigmoid is never applied, so the second threshold meant something different
depending on the backend. The fix:

1. Build a golden set of 50–100 representative questions.
2. Pick a target such as "auto-escalate at most 10% of queries".
3. Tune the thresholds until the golden set hits that rate.

Measure the real escalation rate before tuning. Above about 15% means calibration is
urgent. Below about 3% means the gates add complexity without any visible value.

## Related latency rules from the same review

- **Gate the post-answer evaluator on low confidence.** Running it on every answer adds
  300–700ms to answers that were already confidently right, and its only useful outcomes
  ("refine", "escalate") need a doubtful answer in the first place. Skip it above a
  confidence threshold, or run it async and fire-and-forget after streaming.
- **Choose at most one optional LLM stage** (query transform, LLM planner or post-answer
  evaluator) inside a sub-2s budget. Any two together push the tail over budget.
- **Cap CRAG retries at 1.** Each self-correction iteration costs 2–3s.
- **Streaming is the main UX lever.** First tokens arrive in about 200–400ms, so 1.5s of
  generation still feels fast.
- **Merging the two policy nodes costs telemetry.** Two stages show *where* quality
  breaks (retrieval or rerank). Keep them while the system is still being tuned.

## See Also
- [[Borderline-Band Sufficiency Probe]] — extends (the same graph's gates, hardened with an LLM tiebreak in the uncertain band)
- [[Confidence That Is Not a Probability]] — prerequisite-for (why fixed score thresholds drift)
- [[Retrieval Service Returns Documents, Not Answers]] — extends (the thin-tool alternative that has no gates at all)
- [[HITL Gradient]] — alternative-to (measuring where human involvement stops paying)
- [[CRAG Retry Logic]] — extends (the retry loop whose cap matters for latency)
- [[Golden Set Mechanics]] — prerequisite-for (the calibration set)
