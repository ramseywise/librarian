---
title: HITL Annotation Pipeline
tags: [eval, concept]
summary: Human-in-the-loop annotation workflow for conversation data — two-queue structure (random + edge case), inter-annotator agreement as quality gate, and feedback routing to eval dataset vs failure taxonomy.
updated: 2026-04-24
sources:
  - raw/linear/2026-04-24-evaluation-and-improvement.md
  - raw/playground-docs/librarian-stack-audit.md
---

# HITL Annotation Pipeline

## The Two-Queue Structure

CS agents operate two parallel annotation queues with distinct purposes:

**Queue 1 — Random Sampling (~5%):**
Uniform random sample of all conversations, stratified by intent category to ensure coverage across the distribution. Purpose: build the golden eval dataset and detect systematic quality issues.

**Queue 2 — Edge Case / Signal-Based:**
Conversations filtered by friction signals — escalations, thumbs down, low confidence scores. Purpose: build the failure-attribution taxonomy and surface the system's weak spots.

These serve different purposes and route to different outputs:
- Random sample → golden eval dataset (quality baseline, feeds LLM judge calibration)
- Edge cases → failure-attribution taxonomy + edge case eval subset

## Inter-Annotator Agreement as Quality Gate

**CS agents are not ready to annotate until inter-annotator agreement reaches a defined threshold — not just attendance at training.**

The threshold must be agreed before any annotation begins so "ready" is unambiguous. Without this gate, annotation quality cannot be trusted and downstream eval results are unreliable.

Calibration session design:
1. Agents annotate the same sample conversations independently
2. Calculate agreement (Cohen's κ or percentage agreement)
3. Discuss disagreements to align on guideline interpretation
4. Only proceed to solo annotation when the threshold is met

## Annotation Guidelines Design

The tagging schema must be **specific enough that different agents label the same conversation identically**. Ambiguous tags produce noise, not signal.

Design checklist:
- Every tag has a precise definition with worked examples
- Edge cases and decision rules are documented explicitly
- Annotators have a "when in doubt" default
- Guidelines are versioned — changes trigger re-calibration

Common tag taxonomy:
```python
REVIEW_TAGS = {
    "hallucination",
    "retrieval_relevancy",
    "tone",
    "escalation_failure",
    "context_missing"
}
```

Each annotation writes to a structured record with `trace_id`, `confidence_score`, and `tags[]` for downstream harness linkage.

## Feedback Routing

Annotations from random sampling route to two destinations:

1. **Corrected responses or mislabelled escalations** → eval dataset (golden traces)
2. **Conversations where the model underperformed** → failure-attribution queue

Edge case annotations route differently — they're specifically about failure attribution, not quality baseline. Findings feed the failure-attribution taxonomy rather than the golden set directly.

## LLM-as-Judge Calibration

Before LLM judge scores drive quality decisions, calibrate them against human labels:

1. Run the judge on conversations that CS agents already annotated
2. Compare scores — where does the judge agree/disagree with humans?
3. Adjust judge prompt or thresholds until agreement is sufficient
4. Only then trust LLM judge scores at scale

This is critical for edge cases — judge prompts trained on average-case behavior may not generalize to failure modes.

See [[RAG Evaluation]] for the full judge suite architecture.

## See Also
- [[RAG Evaluation]]
- [[Evaluation & Improvement Project (VIR)]]
- [[PII Masking Approaches]]
