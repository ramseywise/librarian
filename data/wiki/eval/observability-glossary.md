---
title: Observability & Evaluation Glossary
tags: [eval, infra, reference]
summary: Canonical vocabulary for agent observability and evaluation — the observability/tracking/tracing/monitoring/alerting hierarchy, offline vs online evaluation modes, heuristic vs LLM-judge metric types, dataset terminology, and rank-based retrieval metrics (MRR/precision@k/recall@k/ndcg@k/hit@k).
updated: 2026-07-14
sources:
  - raw/notion/2026-07-14-evaluation-glossary.md
---

# Observability & Evaluation Glossary

Reference vocabulary for discussing evaluation, monitoring, and production readiness of agent/RAG systems. Distills terms that are frequently used loosely (tracking vs tracing, golden vs ground-truth dataset) into precise, non-interchangeable definitions.

## Concept Hierarchy

- **Observability** is the umbrella concept — the ability to understand a system's internal state from its external outputs.
  - Built on three classical pillars: **traces**, **logs**, **metrics**.
  - **Tracking** is the practice of recording selected events, states, or outcomes over time so they can be measured, compared, or audited later.
  - **Monitoring** is built on top of the pillars and tracked signals — a *consumer* of them, not a pillar itself.
    - **Alerting** is a subset of monitoring — you can monitor without alerting, but not alert without monitoring.

## Observability

Answers: what happened, where, why, and how did one system step affect another. For an agent system this spans the full path from user input to final response — guardrails, retrieval, model calls, tool usage, latency, errors, output quality.

## Tracking vs Tracing

These two terms are frequently conflated but answer different questions:

- **Tracking** — recording that selected events happened, often aggregated across many requests/users over time. Answers: did this event happen, how often, which users/sessions/traces/releases were affected, how did a metric change over time. Examples: user feedback labels (liked/disliked), retrieval outcomes, eval scores attached to a response, product events (escalation, handoff, retry).
- **Tracing** — records the structured path of *one* request through the system: spans, timing, dependencies, parent-child relationships. Answers: how did this single request move through the system.

**Rule of thumb:** tracking tells you what changed over time across a population of requests; tracing shows you the mechanics of one request.

## Three Classical Pillars

| Pillar | What it is | Detail vs cost |
|---|---|---|
| **Traces** | Structured record of a single request's journey (spans, parent-child relationships, timing, per-step metadata) | High detail, moderate aggregation cost |
| **Logs** | Timestamped, discrete event records — usually unstructured/semi-structured | Most detailed signal, hardest to aggregate reliably |
| **Metrics** | Numeric aggregates over time (error rate, tokens/request, failed retrievals, escalations, cost/conversation) | Cheap to store, easy to alert on, least detail |

## Monitoring and Alerting

- **Monitoring** — collecting metrics, logs, and traces and comparing against known-good baselines. Answers: is the system healthy right now.
- **Alerting** — sending automated notifications when a monitored signal crosses a defined threshold (error rate spike, token usage spike, a critical eval metric drop).

## Evaluation Modes vs Execution Environments

These are two independent axes — don't conflate them:

**Modes:**
- **Offline evaluation** — running the agent in a controlled, non-production context. Whether a fixed reference dataset is required depends on the metric: heuristic metrics need none; LLM judges and retrieval metrics need a grounded dataset.
- **Online evaluation / monitoring** — observing and scoring the agent against live production traffic, post-deployment.

**Execution environments** (both are ways of doing *offline* evaluation):
- **Local run** — evaluation run on a developer machine.
- **Managed experiment runner** — offline evaluation executed through a shared platform's UI/experiment runner (e.g. Langfuse experiments) rather than locally.

## Heuristic Metric vs LLM Judge

- **Heuristic metric** — computed from metadata/labels/checks already on the eval record. No LLM call, no added model cost, usually safe to run in CI (e.g. `satisfaction_rate`, `citation_recall`, `language_consistency`, `citation_hallucination`).
- **LLM judge** — uses an LLM call to score an output. Useful for quality dimensions hard to capture with rules, but costs money per invocation and usually needs a grounded eval dataset (e.g. `grounding`, `completeness`, `answer_relevancy`).

See [[RAG Eval Metrics Suite]] for a full worked taxonomy of runtime vs offline metrics along this same runtime/offline and heuristic/judge split.

## Dataset Terminology

Avoid treating **golden dataset**, **ground-truth dataset**, and **historical output snapshot** as interchangeable:

- A **grounded dataset** is one where expected outputs were validated by humans or a trusted process — anchored to known truth, not synthetically generated or taken at face value from a model's own output. This is distinct from *grounding as a metric* (whether a response is faithful to its retrieved context — see [[Grounding Claim Methodology]]).
- **Golden URLs** — URL-level ground truth inside a retrieval eval dataset: the expected source URLs an agent should retrieve/cite for a query.
- Retrieval/citation-ranking metrics need expected URLs; claim-coverage metrics need pre-extracted `gt_claims` (human-authored factual statements a correct answer should contain); escalation metrics need ground-truth escalation labels.
- A **historical output snapshot** (production responses captured for side-by-side comparison) is not the same thing as a grounded golden dataset — conflating the two overstates the reliability of comparisons run against it.

## Grounding, Citation Hallucination, and Their Live Monitoring Analogue

Three related but distinct checks in the same "is the answer supported by evidence" family:

- **Grounding** — LLM judge checking whether factual claims in the response are supported by retrieved context. Deeper than a citation check; requires an LLM call; mainly offline. See [[Grounding Claim Methodology]] for the underlying claims-based mechanism.
- **Citation hallucination** — heuristic grader checking what fraction of cited URLs were actually in the retrieved set. Cheap, fast, CI-safe. `1.0` = no hallucinated citations.
- **Operational grounding signal** (`grounding.hallucination_rate`) — the production-monitoring view of the same issue family: tracks the percentage of *live* responses citing unretrieved passages.

In short: citation hallucination is the cheap offline check, grounding is the deeper LLM-based judgment, and the hallucination-rate signal is the live monitoring counterpart.

## Rank-Based Retrieval Metrics (Need Expected URLs)

| Metric | Definition |
|---|---|
| `mrr` | Mean Reciprocal Rank — averages `1/rank` across queries (rank = position of first expected URL; `0.0` if none found). Strongest for single-URL cases. |
| `precision@k` | Fraction of top-k retrieved results that are expected URLs |
| `recall@k` | Fraction of all expected URLs appearing in top-k. Especially useful for multi-URL cases. |
| `ndcg@k` | Position-aware ranking metric — relevant results earn more credit the higher they rank in top-k. Complements MRR for multi-URL queries. |
| `hit@k` | Did any correct URL appear in top-k (binary) |

Claim-level counterparts (need pre-extracted `gt_claims` rather than expected URLs): `coverage` (which ground-truth claims are covered in the response) and `recall` (claim-level recall in retrieved context).

## Tooling Split: Infra Observability vs LLM/Agent Observability

A recurring split across teams adopting both a classical APM stack and an LLM-specific platform: the APM stack (e.g. Datadog) owns infrastructure/system-level observability (logs, metrics, monitoring, alerting for the deployed service); the LLM platform (e.g. Langfuse) owns AI/agent-specific observability (traces of the full chain — retrieval, LLM calls, tool use — plus evaluation and prompt-version comparison). See [[Langfuse Platform]] for the concrete Langfuse/Datadog split and [[Observability — LangFuse vs LangSmith Decision]] for the platform selection decision.

## See Also
- [[Observability and Runtime Patterns]]
- [[RAG Eval Metrics Suite]]
- [[Grounding Claim Methodology]]
- [[Synthetic Dataset Generation for RAG Eval]]
- [[Langfuse Platform]]
- [[LLM Grader Calibration Insights]]
