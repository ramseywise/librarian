---
title: Borderline-Band Sufficiency Probe
tags: [patterns, rag, pattern]
summary: Retrieval and rerank scores are uncalibrated ordinal signals whose thresholds drift with corpus and model; keep the fast score gates and spend a cheap LLM "is this context sufficient?" call only inside a two-threshold uncertainty band, logging stable reason codes.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/playground/docs/archived/rag-architecture-refactoring-plan.md
---

# Borderline-Band Sufficiency Probe

From a RAG architecture refactoring plan in the playground repo (2026-04). The plan
hardened an 11-node LangGraph support-RAG graph instead of shrinking it.

## The problem with score-only policy

The graph routed on thresholds: after the retrieval ensemble and again after reranking,
a score decided between answer, HITL gate and escalate. But embedding and cross-encoder
scores are **not calibrated probabilities**. They are ordinal ("A is more relevant than
B"), and any fixed threshold drifts whenever the corpus or the model changes. A raw
cutoff of 0.4 means nothing stable.

## The mechanism

Don't replace the score gates. Narrow where they are trusted:

1. **Keep fast score gates at the extremes.** Clearly high scores continue. Clearly low
   scores escalate. No LLM call either way.
2. **Define an uncertainty band** using two thresholds, or percentile bands derived from
   a held-out set rather than raw values read as probabilities.
3. **Inside the band only**, call a cheap LLM **sufficiency probe** that asks: does this
   context actually answer the question?
4. **Put it behind a mode flag:** `RAG_POLICY_MODE=scores_only|hybrid`, with the band
   edge configured (`RAG_POLICY_HYBRID_BORDER_LOW`). Score-only stays the default until
   the cost and latency envelope is confirmed.
5. **Log every decision**: the raw scores, the thresholds, the route chosen, and a
   **reason code from a stable enum**, so dashboards can count routes over time.

The LLM cost is paid only on the minority of queries where the score is actually
ambiguous.

## Companion decisions from the same plan

- **A context-builder contract.** Select, dedupe, order and trim to a token budget, and
  return the chunk ids used so citations stay exact. It was kept inside the answer node
  at first: a **named, unit-tested module mattered more than a new graph node**.
- **The post-answer evaluator ships as an option, default off**, to keep a second LLM
  call out of the hot path. Batch judges cover evaluation in the meantime.
- **Both HITL gates (retrieval and rerank) were kept** for compliance and product trust,
  even though one was arguably redundant. A single-gate variant stays documented in case
  the metrics justify it later.

## See Also
- [[Confidence That Is Not a Probability]] — extends (the same "scores aren't probabilities" diagnosis, applied to routing)
- [[CRAG Retry Logic]] — extends (adds an LLM tiebreak to score-based routing)
- [[RAG Reranking]] — related (the rerank scores being gated)
- [[Hedging Belongs in the Gate, Not the Answer]] — related (the gate is where uncertainty should live)
- [[HITL Gate Without a Resumer]] — related (what the same graph's two HITL gates do when nobody resumes them)
