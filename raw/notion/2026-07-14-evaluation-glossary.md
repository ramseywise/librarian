# Evaluation Glossary

**Source:** https://app.notion.com/p/108f5c48f02f402f8f750b06b499ec98
**Last edited:** 2026-07-14

This glossary defines the core observability concepts used when discussing evaluation, monitoring, and production readiness for agent systems.

## Concept hierarchy

- **Observability** is the umbrella concept.
  - Its three classical pillars are **traces**, **logs**, and **metrics**.
  - **Tracking** is the practice of recording selected events, states, or outcomes over time so they can be measured, analyzed, or audited later.
  - **Monitoring** is built on top of those pillars and tracked signals.
    - **Alerting** is a subset of monitoring.

## Observability

The ability to understand a system's internal state from its external outputs. Answers: What happened? Where? Why? How did one system step affect another? For an agent system, spans the full path from user input to final response — guardrails, retrieval, model calls, tool usage, latency, errors, output quality.

## Tracking

Recording selected events, states, or outcomes over time so they can be measured, compared, or audited later. Answers: Did this event happen? How often? Which users/sessions/traces/releases were affected? How did a metric change over time?

Examples in an agent system: user feedback labels (liked/disliked/resolved), retrieval outcomes (which sources were returned/cited), evaluation scores attached to a response, product events (escalation, handoff, retry).

**Tracking vs tracing:** tracking records that selected events happened, often across many requests/users. Tracing records the structured path of *one* request through the system (spans, timing, dependencies, parent-child relationships). Tracking tells you what changed over time; tracing shows how a single request moved through the system.

## Three classical pillars

- **Traces** — structured records of a single request's journey (spans, parent-child relationships, timing, per-step metadata). E.g. user query → guardrail → retrieval → LLM → response.
- **Logs** — timestamped, discrete event records, usually unstructured/semi-structured (request received, guardrail decision, retrieval result, error, tool call response). Most detailed signal, hardest to aggregate reliably.
- **Metrics** — numeric aggregates over time (error rate, tokens/request, failed retrievals, escalations, cost/conversation). Cheap to store, easy to alert on, least detail.

## Built on top of the pillars

- **Monitoring** — collecting metrics, logs, and traces and comparing against known-good baselines. Answers: is the system healthy right now? A consumer of the three pillars, not a pillar itself.
- **Alerting** — sending automated notifications when monitored signals cross defined thresholds (error rate exceeds threshold, token usage spikes, a critical eval metric drops). A subset of monitoring — you can monitor without alerting, but not alert without monitoring.

## Evaluation modes and execution environments

**Evaluation modes:**
- **Offline evaluation** — running the agent in a controlled, non-production context. Whether a fixed reference dataset is needed depends on the metric: heuristic metrics (e.g. `satisfaction_rate`) need none; LLM judges and retrieval metrics (`grounding`, `citation_recall`) do.
- **Online evaluation / monitoring** — observing and scoring the agent against live production traffic, post-deployment.

**Execution environments:**
- **Local run** — running evaluation on your own machine, typically via project-g. A way of doing offline evaluation, not a separate mode.
- **Langfuse experiment** — running offline evaluation through the Langfuse UI/experiment runner in shared infra. Also a way of doing offline evaluation.

**Dataset notes:**
- Heuristic metrics need no reference dataset — computed from metadata already on eval records. LLM judges and retrieval metrics require a dataset with expected outputs or retrieved-context passages to compare against.
- A **grounded dataset** is one where expected outputs were validated by humans/a trusted process — anchored to known truth, not synthetically generated or taken at face value from a model output. Distinct from *grounding as a metric* (whether the response is faithful to its retrieved context).

## Evaluation layers and metrics for RAG performance

| Type | Layer | Definition | Metrics |
|---|---|---|---|
| Retrieval Quality | Retrieval Quality (Heuristic) | Did the retriever fetch relevant documents? | Precision@k, Recall@k, F1, MRR, NDCG |
| Retrieval Quality | Retrieval Relevance (LLM-as-judge) | Are retrieved chunks relevant to the question? | Retrieval Relevance |
| Answer Quality | Answer quality for retrieved chunks | Is the answer grounded in the retrieved chunks? | Faithfulness |
| Answer Quality | Answer quality for question | Is the answer useful for the question? | Answer Relevancy, Answer Completeness |
| Answer Quality | Answer quality for GT Answer | Does the answer match the ground truth? | Answer Accuracy |

Notes: retrieval quality can be url- or chunk-level (needs annotation to build an eval set). Faithfulness is also called grounding. Answer completeness matters when a query has multiple sub-questions. VA team's current focus: Retrieval Quality (Heuristic) — Precision@k, Recall@k, F1, at URL level.

## Evaluation metric types

- **Heuristic metric** — computed from metadata/labels/checks already on the eval record. No LLM call, no added model cost, usually safe to run in CI. E.g. `satisfaction_rate`, `citation_recall`, `language_consistency`, `citation_hallucination`.
- **LLM judge** — uses an LLM call to score an output. Useful for quality dimensions hard to measure with simple rules, but costs money per invocation and usually needs a grounded eval dataset. E.g. `grounding`, `completeness`, `answer_relevancy`, `ragas_faithfulness`, `ragas_context_precision`.

## Metric tiers

**North star metrics** — highest-level outcome metrics, both heuristic (no dataset/LLM call needed):
- `satisfaction_rate` = `n_liked / (n_liked + n_disliked)`. Threshold `0.70`. Tracking/comparison, not a regression gate.
- `weighted_resolution_score` = `(resolved × 1.0 + resolved_with_friction × 0.4) / denom`, `denom = resolved + resolved_with_friction + unresolved`. Threshold `0.50`.

**Primary metrics** — main quality gates: `proxy_retrieval_recall`, `citation_recall`, `grounding`, `answer_relevancy`, `completeness`, `ragas_context_precision`, `ragas_faithfulness`, `tool_trajectory`, `routing_accuracy`, `agent_behavior`. Most likely to require LLM calls and a grounded dataset.

**Secondary metrics** — deeper diagnosis, not first-line gates: `citation_hallucination` (heuristic — response cites URLs not in retrieved set), `missing_citation` (heuristic), `language_consistency` (heuristic — Danish query → non-Danish response drift), `f1_correctness` (heuristic), `boundary_adherence` (heuristic), `source_relevance` (LLM judge), `known_response_rate` (heuristic — 1 − unknown_rate), `resolution_rate`/`resolution_with_friction_rate`/`unresolved_rate` (heuristic), `proxy_retrieval_recall_full` (heuristic, noisy), `retrieval_accuracy`/`retrieval_specificity`/`retrieval_f1`/`retrieval_f2` (heuristic), `escalation` (LLM judge), `intent_coverage` (LLM judge), `epa` — Empathy/Professionalism/Actionability (LLM judge), `conciseness` (LLM judge), `deepeval_escalation` (LLM judge).

## Dataset terminology

Avoid treating **golden dataset**, **ground-truth dataset**, and **historical output snapshot** as interchangeable.

- **Primary eval / ground-truth dataset** = `data/datasets/intercom_retrieval_eval.jsonl` — used for retrieval-quality metrics and sampled LLM answer-quality grading.
- **Historical VA output snapshot** = `data/datasets/bkh/va_response.jsonl` — used for `eval-all-bkh` side-by-side comparison only. This replaces older wording that described it as "the current golden dataset for answer quality."

**Golden URLs** — URL-level ground truth inside a retrieval eval dataset: the expected source URLs the agent should retrieve/cite for a query. Retrieval/citation-ranking metrics need expected URLs; claim-coverage metrics need `gt_claims`; escalation metrics need ground-truth escalation labels.

### Metrics needing expected URLs
- `citation_recall` — expected source URLs vs. response citations
- `mrr` — Mean Reciprocal Rank, averages `1/rank` across queries (rank = position of first expected URL; `0.0` if none found). Strongest for single-URL cases.
- `precision@k` — fraction of top-k retrieved results that are expected URLs
- `recall@k` — fraction of all expected URLs appearing in top-k. Especially useful for multi-URL cases.
- `ndcg@k` — position-aware ranking metric; relevant results get more credit higher in top-k. Complements MRR for multi-URL queries.
- `hit@k` — did any correct URL appear in top-k

### Metrics needing pre-extracted `gt_claims`
- `coverage` — which ground-truth claims are covered in the response
- `recall` — claim-level recall in retrieved context

`gt_claims` are pre-extracted, human-authored factual statements a correct answer should contain, passed as `list[str]` to the `coverage`/`recall` graders.

### Metrics needing ground-truth escalation labels
- `escalation` — agent's escalation decision vs. ground truth, compared against `failure_reason` and `contact_support` labels stored on each trace.

## Grounding and citation hallucination

- **Grounding** (`grounding`) — LLM judge checking whether factual claims in the response are supported by retrieved context. Deeper than a citation check; requires an LLM call; mainly offline.
- **Citation hallucination** (`citation_hallucination`) — heuristic grader checking what fraction of cited URLs were actually in the retrieved set. Cheap, fast, CI-safe. `1.0` = no hallucinated citations.
- **Operational grounding signal** (`grounding.hallucination_rate`) — production-monitoring view of the same issue family; tracks % of live responses citing unretrieved passages.

In short: `citation_hallucination` is the cheap offline check, `grounding` is the deeper LLM-based judgment, `grounding.hallucination_rate` is the live monitoring signal.

## Tooling split: Datadog vs. Langfuse

- **Datadog** — infrastructure and system-level observability: logs, metrics (latency, error rates, system health), monitoring, alerting, APM tracing/log aggregation for the deployed `va-agents` service. Classical engineering stack: is the system up, healthy, performing?
- **Langfuse** — AI/agent-specific observability and evaluation: traces (full chain of a user query through the agent — retrieval, LLM call, response), agent-level tracing/scoring for `project-g` and `va-agents`, monitoring of agent quality (not infra health), evaluation (experiments, prompt-version comparison, scoring against datasets). Dan's analogy: "Langfuse is MLflow for agents."

Complementary roles: Langfuse is the LLM-aware observability layer for agent-level tracing/scoring/evaluation; Datadog is the traditional application/infra observability layer for monitoring, APM, and log aggregation.
