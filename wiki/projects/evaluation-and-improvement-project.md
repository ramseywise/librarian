---
title: Evaluation & Improvement Project (VIR)
tags: [eval, rag, infra, project]
summary: Shine's Q2 2026 project to establish data ingestion, feedback loop, and offline eval for the HC Virtual Assistant — 43 issues across 5 milestones targeting 2026-06-30.
updated: 2026-04-24
sources:
  - raw/linear/2026-04-24-evaluation-and-improvement.md
---

# Evaluation & Improvement Project (VIR)

**Team:** Businesshealth-Virtual-Assistant (VIR)
**Status:** In Progress
**Timeline:** Q2 2026 (started 2026-04-23, target 2026-06-30)
**Linear:** https://linear.app/shine-co/project/evaluation-and-improvement-8efa7c4bc235

## What This Project Is

Establish the foundation to understand, measure, and continuously improve system performance for the HC Virtual Assistant. Three tracks:

1. **HC Data Ingestion** — Billy help center → Bedrock KB. Blocks MVP.
2. **HC Feedback Loop** — CS agent HITL annotation workflow. Seeds the eval dataset.
3. **HC Evaluation** — Historical BKH + Intercom data for offline eval. Does not block MVP.

**Q3 dependency:** Full HC/VA evaluation blocked until MVP launches with observability. Q3 priority is comparing against BookKeeping Hero (BKH) baseline.

## Five Milestones

| Milestone | Target | What ships |
|---|---|---|
| M1: Access & Onboarding | 2026-05-08 | All credentials confirmed, CS team sessions done, RAG scope clear |
| M2: RAG Sources Ingested | 2026-05-22 | Billy crawled + ingested to Bedrock KB, annotation guidelines agreed |
| M3: Historical Data Cleaned | 2026-06-05 | Intercom extraction done, GDPR + PII masking confirmed, first CS annotation batch |
| M4: BKH Baseline | 2026-06-12 | BookKeeping Hero performance baseline documented from EDA |
| M5: Human Validated Dataset | 2026-06-26 | ~50 conversation golden eval set, stratified by Danish market intents |

## Key Decisions Embedded in This Project

**Bedrock KB for data ingestion:** Billy domains (billy.dk/support, /billypedia, /pris) crawled via AWS and ingested into Bedrock Knowledge Base for MVP. See [[Bedrock KB vs LangGraph Decision]] for the migration path.

**PII masking before any data lands:** Raw Intercom conversations contain PII. Legal/Ops must confirm the masking approach and storage destination before the extraction job runs. See [[PII Masking Approaches]].

**One-time extraction, not continuous sync:** The Intercom historical data pull is explicitly scoped as one-time for MVP. Continuous sync is deferred until data quality and value are validated.

**~50 conversation golden eval set:** Stratified by high-impact Danish market intents, seeded from BKH explicit feedback signals and CS annotations. Foundation of the offline eval harness. See [[RAG Evaluation]].

**Inter-annotator agreement as quality gate:** CS agents are not considered ready to annotate until agreement reaches a defined threshold — not just attendance. See [[HITL Annotation Pipeline]].

## Ingestion Pipeline Shape

```
Billy domains (billy.dk/support, /billypedia, /pris)
  → AWS Web Crawler (VIR-102)
  → Content audit + domain expert review (VIR-106, VIR-107)
  → Bedrock KB ingestion + validation (VIR-104)

Intercom historical conversations
  → API extraction one-time job (VIR-112)
  → PII masking layer (VIR-115, VIR-116, VIR-117)
  → EDA (VIR-133)
  → CS annotation batches (VIR-124, VIR-125)
  → Golden eval dataset (VIR-131, VIR-132)

BookKeeping Hero data
  → CSV export (VIR-100)
  → EDA for pre-launch baseline (VIR-101)
  → Explicit feedback signals (thumbs up/down) → seed eval dataset
```

## Q3 Stretch Goals

Low priority for Q2 — sequencing blocks these until post-MVP:
- Support ticket clustering (VIR-136) — intent distribution from historical Intercom
- Coverage benchmarking (VIR-135) — validate RAG grounding pre-launch
- Automated data correctness validation (VIR-134) — ongoing Bedrock KB health monitoring
- Failure-attribution taxonomy (VIR-137) — structured classification of failure modes
- LLM-as-judge grader (VIR-138) — automated quality scoring, calibrated against human labels

## See Also
- [[Bedrock KB vs LangGraph Decision]]
- [[RAG Evaluation]]
- [[PII Masking Approaches]]
- [[HITL Annotation Pipeline]]
