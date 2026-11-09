---
title: HITL Annotation Pipeline
tags: [eval, concept]
summary: Human-in-the-loop annotation workflow for conversation data — two-queue structure (random + edge case), inter-annotator agreement as quality gate, and feedback routing to eval dataset vs failure taxonomy.
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-05-veselovsky-2023-artificial-artificial-artificial-intelligence.md
  - data/raw/linear/2026-04-24-evaluation-and-improvement.md
  - data/raw/claude-docs/playground/docs/archived/librarian-stack-audit.md
  - data/raw/claude-docs/playground/docs/archived/mvp-feedback-eval/plan.md
  - data/raw/papers/2026-11-07-gilardi-2023-chatgpt-outperforms-crowd-workers-text.md
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

## Crowd labels may not be human-written

Veselovsky et al. (arXiv 2306.07899, a work-in-progress preprint, 2023) estimated LLM use among Mechanical Turk workers on one task: summarising 16 medical abstracts into at least 100 words, paid $1 per summary. Of 46 usable summaries from 44 workers, a classifier labelled 21 (46%) synthetic at one threshold and 15 (33%) at a stricter one (self-reported; a range from two thresholds, 95% intervals roughly 31 to 61% and 20 to 45%, no correction for classifier error). The classifier was a fine-tuned e5-base model trained on pre-LLM human summaries and 320 ChatGPT summaries, with 97 to 99% accuracy on held-out data of that task. As a side check, 41 of the 46 summaries involved pasting and all 5 typed without pasting were classed human. The authors conclude that crowd-written text cannot be presumed a human gold standard, and suggest workers may become a filter on model output. GPTZero caught only 6 of 10 ChatGPT summaries the authors generated.

Limits: one task, chosen as easy for LLMs, one platform, a June 2023 snapshot, no ground truth on actual LLM use, and the human training data (2019) differs from the 2023 responses in more than LLM availability.

## LLM annotators against crowd workers (Gilardi et al.)

Gilardi, Alizadeh and Kubli (PNAS, arXiv 2303.15056, 2023) gave the same codebooks to three trained annotators (research assistants), US-based MTurk Masters workers and gpt-3.5-turbo run zero-shot, one chat session per tweet. Four datasets (n=6,183) covered relevance, stance, topic and frame tasks, and accuracy meant agreement with the trained annotators' labels.

- ChatGPT's accuracy exceeded MTurk's by about 25 points on average (self-reported).
- ChatGPT's cost was under $0.003 per annotation, about thirty times cheaper than MTurk (self-reported); the extraction notes the figure is stated without a derivation.
- ChatGPT's accuracy tracked trained-annotator agreement, so it did better on easier tasks, while its margin over MTurk correlated negatively with that agreement, so the margin was larger on harder tasks. Across tasks, intercoder agreement correlated only weakly with accuracy.
- Relevance accuracy was reported for four sets in the text; the 2023 content-moderation sample scored only 59%, and the extraction notes that its prompt had no examples.

The preceding section covers a separate question: whether crowd-written text is human-written at all.

Limits: the gold standard is the trained annotators, and accuracy counts only texts on which they agreed. Only gpt-3.5-turbo was tested, zero-shot, on English text in one topic area (content moderation) plus US Congress tweets; the authors call for multilingual, few-shot, chain-of-thought and other-model work. No significance tests are reported, per-task accuracy appears only in a figure, and the outperformance is claimed against MTurk, not against the trained annotators.

## See Also
- [[Online Eval Sampling]] <!-- auto-linked -->
- [[Conversational Test Fixture Design]] <!-- auto-linked -->
- [[Skill Pipeline Dryrun Testing]] <!-- auto-linked -->
- [[RAG Evaluation]]
- [[PII Masking Approaches]]
- [[Manual Review as Eval Bootstrap]] — related (ad-hoc precursor to systematized annotation)
- [[Append-Only Human Labels]] — extends (how rater judgments are persisted so agreement stays measurable)
- [[Human Agreement Ceiling Protocol]] — extends (κ_HH as the ceiling the judge is scored against, with statistics per scale type)
- [[Taste vs Defect Verdict Split]] — extends (what the annotation row should carry)
- [[Graded-Uncertainty Enrichment Contract]] — related (the three uncertainty levels that decide what reaches the annotators)
- [[Recency-Seeded Label Queue Samples the Thin End]] — extends (seed only judgeable rows, stratify kind × field, rank by rater basis)
- [[Snapshot the Judged Value on the Verdict Row]] — extends (verdict rows for pre-canonical or mutable subjects)
- [[LangSmith Platform]] — instance-of (annotation queues as the review surface)
- [[Silicon Sampling and Algorithmic Fidelity]] — related (a model standing in for human respondents, as here for human labelers)
- [[Dynabench]] — related (human validation of model errors)
- [[ChatGPT Zero-Shot NLP and Annotation Studies]] — related (model versus human labelling)
