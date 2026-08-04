---
title: Langfuse Platform
tags: [infra, eval, concept]
summary: Langfuse is an open-source LLM engineering platform for tracing, prompt management, and evaluation — chosen by [client]'s AI teams as the observability standard, with SSO and governance pending before production rollout. Instrumentation patterns vary by framework (lf.trace() for ADK, CallbackHandler for LangGraph, @observe for FastAPI).
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--04-agentic-frameworks--notes--langfuse.md
  - raw/gdrive/2026-05-15-ai-chapter-meeting-1.md
  - raw/gdrive/2026-05-28-ai-chapter-meeting-2.md
  - raw/notion/2026-05-13-compare-langgraph-adk-langfuse-langsmith.md
  - raw/notion/2026-06-01-chat-agent-rfc.md
  - raw/claude-docs/project-g/docs/frameworks/langfuse.md
  - raw/agent-skills/observability/SKILL.md
---

# Langfuse Platform

Langfuse is an open-source LLM engineering platform for observability, tracing, evaluation, prompt management, and analytics. It is purpose-built for LLMs and agentic workflows — unlike general APM tools like Datadog, which are not designed for the trace-level visibility needed when agents call other agents, manage sessions, and run multi-step evaluations.

**[client] adoption status (as of 2026-06):** Legal review complete; contract being finalized. SSO is mandatory before production rollout. SaaS version adopted for testing; self-hosting preferred long-term for data sovereignty. Virtual Assistant and Advisor Production teams have both connected staging environments.

---

## Core Capabilities

### 1. Observability & Tracing
- Traces every request and tool call in an LLM system — inputs, outputs, inter-agent steps, guardrail decisions, execution time, cost
- Session-based tracing: groups all traces for a conversation into one view
- Non-LLM deterministic steps can also be tracked via the SDK (not just model calls)
- OpenTelemetry-native — integrates with frameworks via OTel without custom instrumentation

### 2. Prompt Management
- Prompts stored and versioned in Langfuse platform
- Non-engineers (PMs, domain experts) can update prompts without code changes
- **Langfuse-first approach**: prompts loaded from Langfuse at runtime; fallback to repo version if unavailable. CI check ensures repo stays in sync.
- Enables fast iteration on prompts without code redeploy

### 3. Evaluation & Experiments
- Upload golden datasets and run experiments against them
- Track custom metrics (F1 score, precision, recall, latency) per experiment
- Compare experiments side-by-side
- Does NOT support uploading/running custom Python code in the platform — evaluations must run in your code and push results to Langfuse
- Dashboards and score timelines for monitoring quality over time

### 4. Multi-Project Organization
- Separate work into distinct projects with independent access control
- Unlimited users on all tiers — charged per usage, not per seat

---

## Datadog / Langfuse Split

Langfuse is **not** a replacement for Datadog:
- **Datadog**: system monitoring, APM, infrastructure — uptime, endpoint health, latency at the service level
- **Langfuse**: LLM-agent-specific traces, prompt management, evaluation, quality metrics over time

The key architectural split: Datadog for ops, Langfuse for AI quality. Both are needed; they serve different audiences and answer different questions.

---

## [client]-Specific Decisions

### SaaS vs Self-Hosting
- **Current**: SaaS version chosen for the testing phase (avoids infrastructure management overhead)
- **Preferred long-term**: self-hosted, for PII/data sovereignty — traces may contain sensitive financial data
- Self-hosting requires infrastructure team involvement (upgrades, scaling, access control)

### Compliance & Governance
- PII reduction required before sending data to Langfuse (SaaS is external infrastructure)
- Governance framework being defined: process for onboarding teams to production not yet finalized
- Data deletion compliance pattern: use token-based references (IDs) in golden datasets to point to files in their authoritative storage — never copy raw documents into the observability platform

### SSO Requirement
- SSO is **mandatory** before production use (security team requirement)
- Will be enabled as part of the pro contract (Teams add-on tier)
- Currently using password/Google auth in staging — acceptable for testing only

### Legal Status
- Legal review complete as of May 2026
- Contract finalization in progress (aligning with [client]'s requirements)
- Until contract signed, production data is not permitted

---

## Langfuse vs Patronus AI ([client] context)

| Dimension | Langfuse | Patronus AI |
|---|---|---|
| Deployment | SaaS + self-hosted | Self-hosted (on-premise, used by Advisor Production inside SHI) |
| LLM-as-judge | Available but not required | Pre-packaged LLM-as-judge evaluators |
| Framework fit | Framework-neutral, OTel-native | Similar feature set |
| Maturity | More mature, larger ecosystem | Startup (direct contact with team in San Francisco) |
| [client] decision | Adopted (legal cleared) | Being discontinued — doesn't fit current SHI context |

---

## Langfuse vs LangSmith

See [[Observability — LangFuse vs LangSmith Decision]] for the original RAG-focused decision.

The [client] VA team conducted a more comprehensive evaluation for an AWS-hosted, ADK-compatible, high-compliance accounting system:

| Platform | Weighted Score | Best when |
|---|---|---|
| **Langfuse** | **8.58 / 10** | AWS-hosted, ADK-compatible, Datadog-aligned, high-compliance |
| LangSmith | 7.92 / 10 | LangGraph-first architecture with deep HITL debugging needs |

Langfuse wins on: security/data sovereignty, AWS fit, Datadog integration, cost/scalability, framework agnosticism, prompt governance.
LangSmith wins on: LangGraph-native HITL trace quality, evaluation workflow maturity.

Pricing: Langfuse = unlimited users + usage-based ($29–$199/mo). LangSmith = $39/user/month + per-trace overages (~6× more expensive at scale).

---

## Integration Patterns

### Chat Agent ([client] Banking)
- Traces sent to Langfuse after each turn
- Prompts loaded from Langfuse versioned registry (Langfuse-first approach)
- Banking Context Classifier prompt managed in Langfuse
- Redirection rate tracked as a Langfuse runtime metric

### Advisor Production / Agentic CPA
- Langfuse connected to staging for observability
- In-house evaluation solution being built for deterministic metrics (not using Langfuse evaluation layer)
- Patronus AI being discontinued in favor of Langfuse for observability

---

## Instrumentation Patterns by Framework

**Key principle:** Use native instrumentation per framework — no unified adapter layer. Native depth (ADK tool call sequences, LangGraph node transitions) is worth the cross-platform query cost.

### ADK — `lf.trace()` + ContextVar
ADK's runner loop is not a regular Python call stack — `ContextVar` propagation is more reliable than `@observe` decorators. Create the trace in `main.py`, set it on `_lf_trace_ctx`, read it inside tool functions to create child spans.

```python
# main.py — before runner.run_async()
_lf_token = _lf_trace_ctx.set(_lf_trace)
try:
    async for event in _runner.run_async(...):
        ...
finally:
    _lf_trace_ctx.reset(_lf_token)

# agent.py — inside tool function
lf_trace = _lf_trace_ctx.get()
if lf_trace:
    span = lf_trace.span(name="bedrock-kb-retrieve", input={"queries": queries})
    ...
    span.end(output={...}, metadata={...})
```

### LangGraph — `CallbackHandler`
```python
from langfuse.callback import CallbackHandler

handler = CallbackHandler(public_key=..., secret_key=..., session_id=session_id)
result = await graph.ainvoke(state, config={"callbacks": [handler]})
```
Every node, edge, and LLM call is captured automatically. Add extra metadata via
`handler.trace.update(metadata={...})` after the invoke.

### Mixed-platform agents
When one agent needs coverage on both platforms — built with LangGraph, but the rest of the
system standardizes on Langfuse — **export via the OTEL collector (Langfuse → LangSmith)
rather than double-instrumenting.** Two independent instrumentation paths on one agent
produce two trace trees that must be reconciled by hand, which is the same adapter cost the
no-unified-layer principle above avoids.

### FastAPI/standard Python — `@observe` decorator
```python
from langfuse.decorators import observe, langfuse_context

@observe(name="agent_turn")
async def _run_turn(query: str, session_id: str = "") -> dict:
    langfuse_context.update_current_observation(session_id=session_id)
    ...
    asyncio.create_task(push_online_scores(trace_id=langfuse_context.get_current_trace_id(), ...))
```

## Online Scoring — Attaching Grader Results Post-Hoc

Run graders offline against completed traces and write scores back via the API:

```python
langfuse.score(trace_id=trace_id, name="grounding", value=result.score, comment=result.explanation)
```

**Standard score keys for RAG support agents.** Heuristic tier — no LLM call, so free to run
on every trace:

| Key | Grader | Range | Tier |
|---|---|---|---|
| `citation_hallucination` | `CitationHallucinationGrader` | 0 / 1 | Tier 1 — response URL ∉ retrieved set |
| `missing_citation` | `MissingCitationGrader` | 0 / 1 | Tier 2 — substantive response, no citations |
| `citation_recall` | `CitationRecallGrader` | 0–1 | Golden URL recall (alias: `source_match`) |
| `language_consistency` | `LanguageConsistencyGrader` | 0 / 1 | Tier 4 — query language ≠ response language |

LLM tier — costed per trace, so these are the ones that get sampled rather than run
exhaustively:

| Key | Grader | Range |
|---|---|---|
| `grounding` | `GroundingGrader` | 0–1 |
| `answer_relevancy` | `AnswerRelevancyGrader` | 0–1 |
| `completeness` | `CompletenessGrader` | 0–1 |
| `escalation_correct` | `EscalationGrader` | 0 / 1 |
| `routing_accuracy` | intent label match | 0 / 1 |

The split is a **cost gate, not a quality ranking** — the heuristic graders are binary
structural checks that happen to be free, which is why they can gate every response while
the LLM graders run on a sampled slice. See [[Online Eval Sampling]] for how that slice is
chosen. The tier column maps onto [[Grounding Claim Methodology]].

Keeping score *keys* stable across agents is what makes cross-agent comparison possible at
all — a renamed key silently breaks every historical comparison, since the platform has no
way to know two keys meant the same thing.

## Datasets and Experiment Runs

Datasets group input/output examples for systematic evaluation. Items carry the expected
output and arbitrary metadata:

```python
langfuse.create_dataset(name="quality-eval-v1", description="...")

langfuse.create_dataset_item(
    dataset_name="quality-eval-v1",
    input={"query": row["query"]},
    expected_output={"expected_urls": row["expected_urls"],
                     "expected_answer": row.get("expected_answer")},
    metadata={"task_id": row["task_id"], "gt_confidence": row.get("gt_confidence")},
)
```

Items can also be added from the UI — open a trace → **"Add to dataset"**. That path is the
one that matters operationally: it turns an interesting or failing production trace into a
regression fixture without leaving the tool, which is the mechanism behind the rolling
discovery rows in [[Eval Suite Maintenance]].

Each run against a dataset creates an experiment. Tag it with your own `run_id` so platform
results join back to your experiment-tracking records:

```python
run_id = str(uuid.uuid4())
git_commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()

dataset = langfuse.get_dataset("quality-eval-v1")
for item in dataset.items:
    with item.observe(run_name="rag-chunking-v4", metadata={"run_id": run_id}) as trace_id:
        output = await handle_request(item.input["query"], session_id=run_id)
```

Compare runs in the Experiments tab, filtering by `experiment_name` or `run_id` and diffing
grader scores column by column. The platform stores the *scores*; it does not store the
retrieval configuration that produced them — that is what
[[Experiment Tracking Schemas]] exists to pin, and `run_id` is the join key between the two.

## Remote Prompt Management

```python
instruction = get_langfuse_prompt(
    prompt_name="agent_instruction",   # Langfuse prompt name
    fallback=LOCAL_PROMPT,             # local fallback when Langfuse is off
)
```

The fetch is called inside a lazy factory (cached for process lifetime — no per-request fetch). Langfuse must be initialised via `configure_runtime()` before the agent is constructed.

## Annotation Queues (HITL Path)

Route low-confidence grader outputs to Langfuse annotation instead of file-based queues:

```python
queue = langfuse.create_annotation_queue("uncertain-cases")
for trace_id, score in grader_results.items():
    if score < 0.6:
        langfuse.add_trace_to_queue(queue_id=queue.id, trace_id=trace_id)
```

Reviewers label in the UI; export completed labels as JSONL for regression fixtures.

## PII Redaction via Mask Hook

The Langfuse SDK accepts a `mask` function at client initialization applied to all trace data before any network call. This is the single interception point for PII redaction in agentic pipelines. For a production French-language financial agent implementation, see [[Presidio PII Redaction for Langfuse]].

## ADK Two-Layer Tracing

When using Google ADK v1.x, two instrumentation layers combine into a single trace tree: ADK's OpenTelemetry auto-instrumentation (LLM calls, tool executions) + manual `@observe` decorators (retrieval steps, custom spans). Critical operational additions: session ID grouping, RAG path tagging, retrieval quality as a first-class Score. See [[Langfuse ADK Tracing Patterns]] for patterns and the gap checklist.

## See Also
- [[Langfuse ADK Tracing Patterns]]
- [[Presidio PII Redaction for Langfuse]]
- [[Observability — LangFuse vs LangSmith Decision]]
- [[AI Engineering Chapter @[client]]]
- [[[client] Chat Agent]]
- [[Input Guardrails Pipeline]]
- [[RAG Evaluation]]
- [[Observability and Runtime Patterns]]
- [[Observability & Evaluation Glossary]]
- [[Experiment Tracking Schemas]] — complements (run_id joins platform scores to the config that produced them)
- [[Online Eval Sampling]] — depends-on (which traces get the costed LLM graders)
- [[Eval Suite Maintenance]] — implements (add-from-trace as the regression-fixture path)
- [[LangSmith Platform]] — alternative-to (same capabilities in the LangChain ecosystem; auto-instrumented for LangGraph, manual for ADK)
