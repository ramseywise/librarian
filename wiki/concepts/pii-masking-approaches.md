---
title: PII Masking Approaches
tags: [infra, eval, concept]
summary: Regex vs LLM-based vs hybrid PII masking for conversation data pipelines — contextual PII is the hard problem; compliance sign-off is a hard gate before data moves.
updated: 2026-04-24
sources:
  - raw/linear/2026-04-24-evaluation-and-improvement.md
---

# PII Masking Approaches

## The Problem

Standard PII (email, phone, national ID) is easy — regex handles it reliably. The hard problem is **contextual PII**: company names, account references, and implicit identifiers that only become sensitive in context. Contextual PII is where masking systems fail and where legal and reputational risk is highest.

## Three Approaches

| Approach | Coverage | Cost | Latency | Risk |
|---|---|---|---|---|
| **Regex** | Explicit PII only | Near-zero | < 1ms | Misses contextual PII |
| **LLM-based** | Explicit + contextual | ~$0.01–0.03/conversation | 200–800ms | Over-masking; cost at volume |
| **Hybrid** | Regex for obvious + LLM for contextual | Medium | Medium | Two-step complexity |

**The key insight:** Regex alone will miss contextual PII. LLM-based masking improves coverage but adds cost and latency. The right approach depends on the legal bar set in compliance sign-off and the volume of data being processed.

## Compliance Sequencing

Before any conversation data can be processed, two things must be confirmed in this order:

1. **Storage destination provisioned** — Snowflake or S3 confirmed to meet data residency requirements.
2. **Legal/Ops written sign-off** — Confirmed masking approach and exact pipeline stage where masking is applied.

The masking layer must not be skippable or bypassable. This is a hard gate — the extraction job cannot run until both are done.

## Validation Requirements

Testing must go beyond obvious fields:

- **Explicit PII:** Email, phone, national ID, name fields
- **Contextual PII:** Company names, account references, product references that imply identity
- **Over-masking check:** Legitimate content that looks like PII (product codes, legal citations) — over-masking corrupts the downstream signal

Get Legal/Ops sign-off only after validation results are reviewed.

## When to Revisit the Approach

At high volume (>10K conversations/day), LLM-based masking becomes expensive. Revisit with a purpose-built NER model (spaCy, flair) — cheaper and faster than an LLM call per conversation at scale, with acceptable contextual PII coverage for most use cases.

## See Also
- [[Evaluation & Improvement Project (VIR)]]
- [[HITL Annotation Pipeline]]
- [[RAG Evaluation]]
- [[Bedrock KB vs LangGraph Decision]]
