---
imported_hash: 96addbef72e3e727
title: 'AI-engineering system design: interviewer rubric and personas'
summary: How an AI-engineering system design round gets scored, and three ways an interviewer can run it.
order: 77
kind: reading
section: System design round
source: sisyphus/interviewing/rounds/system-design-round/interviewer-personas.md
---

# AI-engineering system design: interviewer rubric and personas

How an AI-engineering system design round gets scored, and three ways an interviewer can
run it. Use this for mock rounds: an agent (or a friend) plays the interviewer by taking
the **rubric + flow** below, adding **one persona**, and filling in the **session config**.
The persona changes the tone. It never changes the rubric.

Condensed from the prompt pack in
[alexeygrigorev/ai-system-design-interview-studio](https://github.com/alexeygrigorev/ai-system-design-interview-studio)
(`ai_engineering_interviewer_prompts/01–06`), imported 2026-10-29.

**Scope.** This is applied AI engineering. It isn't generic backend design and it isn't ML
research. The question being tested: can you take an ambiguous AI product or platform
problem and design a reliable, safe, observable, cost-aware production system around it?

---

## Session config

| Variable | Values |
|---|---|
| Level | junior · mid · senior · staff |
| Duration | 30 · 45 · 60 min |
| Topic | a [topic brief](#topic-briefs) below, or any prompt from [questions.md](questions.md) or [walkthroughs/](walkthroughs/); if none is given, the interviewer picks one |
| Feedback mode | `end_only` · `midpoint_and_end` · `coaching_after_sections` |
| Constraints (optional) | enterprise customers · private documents · human approval before external actions · low latency · low cost · regulated domain · multilingual |

Topic pool from upstream: RAG customer support, internal knowledge assistant, AI coding
assistant, document extraction, email triage and drafting, sales-call summarization, AI
data analyst, workflow automation, agentic travel booking, support agent with tools,
private-document search, eval/monitoring platform, multimodal support, healthcare intake,
enterprise copilot.

---

## Rubric: 11 dimensions

Each dimension lists the evidence the interviewer listens for (✓) and the red flags (✗).

| # | Dimension | ✓ Strong signals | ✗ Weak signals |
|---|---|---|---|
| 1 | **Product and task framing.** Users, task, v1 scope, out of scope, what stays human, risk level | Clear user workflow; separates UX from backend; names high-risk actions; sets automation boundaries; practical v1 | "Use GPT" before clarifying; AI as magic; nothing about refusal or escalation |
| 2 | **Success metrics and launch criteria** | Product metrics and AI quality kept separate; offline vs online; guardrail metrics; **no-launch thresholds** | Only "accuracy"; no launch criteria; ignores cost, latency or safety |
| 3 | **System architecture.** UI, API, authN/Z, orchestration, context building, retrieval, model, tools, storage, ingestion, eval, monitoring, escalation, feedback | Request flow *and* ingestion flow; components separated; state location explicit; sync vs async; retries, fallbacks, rollback | "LLM + vector DB"; can't explain runtime behavior or component failure; the model is the whole system |
| 4 | **Model and AI approach.** Prompting, structured output, function calling, RAG, fine-tuning, embeddings, reranking, classifiers, rules, agents, HITL, hybrid | Starts simplest; justifies each choice; **knows when not to use an LLM or an agent**; deterministic code for deterministic work; smaller models and routing; validates outputs | Always the biggest model; agents for simple flows; fine-tunes where retrieval fits; RAG without retrieval quality; no output validation |
| 5 | **Context engineering and retrieval.** Sources, ingestion, chunking, metadata, hybrid search, reranking, context budget, permissions, freshness, deletes, conflicts, citations | Permission-filtered retrieval; retrieval quality evaluated separately from generation; handles staleness; chunking and reranking reasoned | "Put docs in a vector DB" and stop; no ACLs; no retrieval eval; no plan for stale or conflicting docs |
| 6 | **Agent and tool design** (if relevant) | Exact tool list; typed schemas; low-risk vs high-risk split; policy check before execution; stopping conditions; safe traces; human approval for irreversible actions | "The agent decides"; unrestricted tools; no stop condition; no tool-failure handling |
| 7 | **Evaluation and testing.** Golden sets, offline/online, human review, regression, version comparison, red-teaming, injection tests, error analysis, A/B | Retrieval and generation evaluated separately; regression gate before prompt, model or index changes; tests hallucination, refusal, injection; knows LLM-as-judge limits; pass/fail thresholds | "Test it manually"; user ratings only; no regression or safety testing |
| 8 | **Production readiness.** Latency budget, throughput, cost/task, tokens, caching, queues, rate limits, timeouts, provider outage, routing, deploy, rollback, versioning, incidents | p95/p99 named; cost controlled; provider failover; monitors quality, safety, latency and cost; **versions prompt, model, retrieval and index**; rollback | No latency or cost; no fallback; uptime-only monitoring; no versioning |
| 9 | **Safety, security, privacy** | AuthZ *before* retrieval and tool calls; model output treated as untrusted; tool calls validated; PII-safe logging; escalation; red-teams likely attacks | Trusts the model; retrieved docs bypass permissions; prompts and responses logged carelessly; ignores malicious users |
| 10 | **Trade-off reasoning.** Quality/latency, cost/capability, automation/review, RAG/fine-tune, agent/workflow, freshness/index cost, safety/friction, v1/platform | Compares alternatives; says what's deferred; names the riskiest assumption; **revises when challenged** | One "obviously correct" answer; can't simplify or prioritize |
| 11 | **Communication and ownership** | Structured; states assumptions; concrete mechanisms; end-to-end flow; course-corrects; clean summary | Rambling; buzzwords; too theoretical; too model-centric *or* too infra-centric |

### The five "don't accept" rules

The interviewer pushes back every time one of these appears without detail:

- **"Use RAG"** → what gets indexed, how is it chunked, what are the permissions, how is retrieval evaluated?
- **"Use an agent"** → which tools, what state, what policy, what happens on failure?
- **"Monitor it"** → which metrics, what alerts?
- **"Human in the loop"** → when, why, and how?
- **Buzzwords in general** → give the concrete mechanism.

---

## Interview flow: 11 phases

1. **Opening.** A realistic, vague prompt.
2. **Clarification.** Answered realistically, without over-specifying.
3. **Metrics.** Success, guardrails, launch criteria.
4. **High-level architecture.** Request flow, data flow, boundaries.
5. **AI approach.** Model, prompting, RAG vs fine-tune, tools, agents, rules, baselines.
6. **Context and data.** Sources, ingestion, chunking, retrieval, freshness, permissions, data quality.
7. **Tools and agents** (if relevant). Schemas, approval gates, state, stopping, failure.
8. **Evaluation.** Offline, online, golden sets, red-team, human review, regression, thresholds.
9. **Production.** Latency, cost, scale, caching, provider failure, monitoring, deploy, rollback, incidents.
10. **Safety and privacy.** Hallucination, injection, leakage, permissions, abuse, escalation.
11. **Wrap-up.** Summarize the design, name the riskiest assumption, define v1, list future work.

**Adaptive follow-up.** After each answer, the interviewer silently classifies it as one
of: strong · missing detail · too vague · too model-centric · too infra-centric · unsafe ·
over-engineered · under-scoped · not production-ready · stuck · off-topic. Then they pick
*one* move: ask for a mechanism, the request flow, the data flow, metrics, safety, cost or
latency, eval, a fallback, an alternative, or a simplification, or move to the next phase.
One question at a time, kept short. No ideal answer revealed mid-round. Applied judgment
counts for more than ML theory.

---

## Seniority calibration

| Level | Bar |
|---|---|
| Junior | Basic LLM/RAG, simple architecture, API integration, basic eval, aware of hallucination, willing to fall back to a human |
| Mid | Owns a feature end to end; clear RAG or tool architecture; practical eval; deployment awareness; latency and cost trade-offs; debugging mindset |
| Senior | Strong decomposition; careful choice of approach; production realism; eval design; safety and security; cost and latency control; **prioritization** |
| Staff | Platform thinking; reusable eval infrastructure; cross-team interfaces; governance; incident planning; data feedback loops; principled trade-offs |

---

## Personas

| | Supportive coach | Neutral evaluator | Adversarial challenger |
|---|---|---|---|
| Warmth / guidance / pressure | high / med-high / low | med-low / medium / medium | low / low / high |
| Interrupts | rarely | for pacing | whenever you're vague or dodging |
| Hints | gradual ladder | minimal, only when blocked | rare and narrow, only after you've had to reason |
| Maps to skill stance | `coach` | `mock` | `mock` with pressure (adversarial) |

### Supportive coach

Collaborative problem solving. Helps you structure the ambiguity but leaves every design
decision with you.

- **Hint ladder:** (1) restate it more simply, (2) point at the dimension, (3) offer two directions, (4) give a small example, (5) hand control back.
- **Soft challenges:** "Can you make that more concrete?" · "What situation might break that?" · "What does the agent add over a simpler workflow?"
- **Over-engineering:** "What would you build in the first four weeks?" · "Can we solve 80% without a full agent?"
- **Too model-centric:** "What does the user see?" · "What happens when the model is wrong?"
- **Never:** completes the design, praises weak answers, lectures, removes all pressure.
- **Feedback:** strengths first, then the highest-impact gaps.

### Neutral evaluator

A realistic round. You lead, silence is allowed to sit, and nobody rescues you early.

- **Sequence:** requirements → metrics and guardrails → architecture → AI approach → retrieval/tools → eval → deploy and monitor → risks → what you'd build first.
- **Precision probes:** "Why that approach?" · "What's the simpler baseline?" · "What changes at 10× traffic?" · "Fallback if the provider is down?" · "What metric stops launch?"
- **When you're vague:** "Define that metric." · "What does the API return?" · "What's in the vector DB?" · "What would you alert on?"
- **When you go deep too early:** "Hold that. High-level first."
- **Feedback:** short and evidence-based. "You met the bar on… / The main missing area was…"

### Adversarial challenger

Technical scrutiny under pressure. It's harsh but professional: no insults, no sarcasm,
and it stops pushing once you've given a reasonable answer.

- **Premise challenges:** "Why does this need an LLM?" · "Why not rules / search plus templates / a classifier / human approval / an offline batch?" · "Why the largest model?"
- **Interrupts:** "Pause. What exactly is stored?" · "You said 'guardrails.' Which ones, and where?" · "You said 'human fallback.' When exactly?"
- **Stress tests:** provider down · stale index · 20× traffic · a prompt change regresses quality · token cost doubles overnight · a tool call partially succeeds · "a user asks for another customer's data, what blocks it?"
- **Narrow hints only:** "Split eval into retrieval and answer quality. What do you measure?" · "Cost is too high. Name two levers."
- **Fair play:** doesn't change the problem unfairly or nitpick irrelevant details, and doesn't penalize you for not knowing a particular vendor when the design is sound.
- **Feedback:** biggest gap first, then strengths. "You lost signal when… / You handled pressure well when…"

**What it tests:** staying calm, admitting uncertainty, and revising the weak part
visibly. That's the same recovery move as in the [README](readme.md) prep checklist.

---

## Final feedback template

Feedback is based only on what was actually said.

1. Overall assessment
2. Strongest signals
3. Weakest signals
4. Missed AI-engineering considerations
5. Scores 1–5: framing · metrics · architecture · model/context · agent/tools (if relevant) · eval · production · safety · trade-offs · communication
6. Seniority signal
7. Pass/no-pass for the configured level
8. One concrete practice recommendation
9. One answer rewritten the way it could have been stronger

---

## Topic briefs

Sixteen prompts, each with the constraints the interviewer reveals during clarification
(from upstream `src/questionBank.ts`). Pick one for the **Topic** slot, keep the constraints
hidden, and hand each one over only when the candidate asks the question it answers. Nine of
these have a full walkthrough in [walkthroughs/](walkthroughs/readme.md).

**`enterprise-rag`**: Document Q&A Assistant / RAG system for private enterprise documents.

- Answers must include citations and say when retrieved context does not contain the answer.
- Document access must respect user, group, tenant, and source-system permissions.
- Inputs include PDFs, slides, wikis, tables, and long reports where document-wide context matters.
- Evaluation should cover retrieval quality, faithfulness, answerable/unanswerable cases, and regressions.

**`million-user-chat`**: AI chat feature scaled to 1M daily users, with cost, latency, and reliability tradeoffs.

- Optimize time-to-first-token, p95 latency, token cost, and provider rate limits.
- Use model tiering, caching, prompt compression, and fallback routing where quality allows.
- Track LLM-specific metrics: cost, latency, hallucination reports, safety blocks, and user satisfaction.
- Streaming responses are required; graceful degradation is preferred over hard failure.

**`coding-assistant`**: AI coding assistant for a large engineering organization.

- Repo indexing must preserve code ACLs and redact secrets before model or embedding calls.
- Autocomplete needs low latency; chat, code review, and larger edits can use slower stronger models.
- Tool actions such as creating commits, opening PRs, or modifying files require explicit user approval.
- Quality should be evaluated with internal test suites, compile success, acceptance rate, and defect rate.

**`hospital-voice-assistant`**: Hospital voice assistant that handles noise, privacy, latency, and domain vocabulary.

- The system must handle noisy rooms, accents, interruptions, and medical vocabulary.
- PHI handling, audit logs, EHR permissions, and retention policies are mandatory.
- Low-confidence transcription or clinical uncertainty must trigger clarification or clinician handoff.
- The assistant must not invent clinical facts or make unsupported diagnoses.

**`legal-contract-generation`**: Legal contract generation system with compliance and human approval requirements.

- Generated clauses must come from approved templates, playbooks, or cited legal knowledge sources.
- Human legal approval is required before external delivery or signature workflow entry.
- The system must keep versioned prompts, templates, outputs, redlines, and reviewer decisions.
- Risk summaries should identify unsupported, missing, or non-standard clauses instead of hiding uncertainty.

**`candidate-sourcing`**: AI-powered candidate sourcing system.

- Ranking must be explainable to recruiters and checked for protected-class proxy bias.
- Candidate data requires consent, retention limits, deletion support, and source attribution.
- The model can draft outreach, but recruiters approve messages before sending.
- Evaluate qualified-candidate precision, recruiter acceptance, diversity impact, and false negatives.

**`upload-processing`**: Upload-processing system for 10K monthly user files, including bank payslips, IDs, and references.

- Extract structured fields with OCR/multimodal models and attach confidence plus source evidence.
- Financial and identity data must be encrypted, redacted from logs, and governed by retention policy.
- Low-confidence extraction, mismatch, or fraud signals must route to human review.
- The pipeline can be asynchronous; correctness and auditability matter more than instant response.

**`doctor-insurer-billing`**: Doctor-to-insurer billing automation based on patient notes.

- Clinical notes contain PHI and must follow healthcare privacy, access, and audit requirements.
- Billing codes must be linked to supporting evidence from notes, not free-form model guesses.
- Payer-specific rules, missing documentation, and confidence thresholds affect submission eligibility.
- A billing specialist or clinician approves claims before final insurer submission.

**`fraud-detection`**: Fraud detection system with model monitoring and escalation.

- Decisions need explainable risk factors and escalation paths for analyst review.
- False positives harm legitimate users, so thresholds must vary by action value and risk.
- Models must be monitored for drift, adversarial behavior, label delay, and feedback-loop bias.
- LLMs may summarize evidence for analysts, but should not be the sole source of fraud decisions.

**`conversation-memory`**: ChatGPT-style cross-conversation memory with privacy controls.

- Memory is opt-in and users can inspect, edit, delete, and disable stored memories.
- Store structured memories with provenance, timestamps, sensitivity labels, and TTL where appropriate.
- Retrieval must isolate users and tenants and avoid surfacing stale or sensitive memories unexpectedly.
- Evaluate personalization benefit separately from privacy leaks and hallucinated memories.

**`agentic-workflow`**: Multi-step agentic workflow for meeting scheduling or code review.

- Tool calls need typed schemas, scoped credentials, idempotency, retries, and audit traces.
- Irreversible actions require human approval before execution.
- The orchestrator enforces max steps, termination conditions, and loop detection.
- Evaluate task completion, tool selection accuracy, safety/refusal behavior, and cost per completed task.

**`policy-detection`**: Content and policy violation detection system.

- Support inline low-latency checks plus async human review for borderline cases.
- Policies are versioned and category-specific; decisions need appeal and audit support.
- Measure precision, recall, severity calibration, and fairness across languages or dialects.
- Defend against adversarial evasion without exposing bypass details to users.

**`unified-query-engine`**: Unified query engine across email, calendar, documents, and chat.

- Federated retrieval must preserve source-system ACLs and connector rate limits.
- Answers need source links and must distinguish retrieved facts from inferred summaries.
- The system must handle time, people, entities, conflicting sources, and freshness requirements.
- PII leakage prevention and query audit logs are mandatory.

**`llm-search`**: Real-time LLM-powered search engine.

- Responses must be grounded in fresh retrieved sources with visible citations.
- Latency budget must cover search, reranking, generation, streaming, and cache lookup.
- The system needs source-quality scoring to reduce spam, hallucination, and stale answers.
- Popular queries should use caching, but time-sensitive queries must bypass stale cached answers.

**`image-generation-pipeline`**: Scalable image-generation pipeline for millions of users.

- Use async GPU job queues with prioritization, batching, retries, and progress updates.
- Prompt and output safety checks are required before images are delivered.
- Model versions, seeds, parameters, and outputs should be traceable for rollback and debugging.
- Cost controls include quotas, abuse detection, model tiering, and storage/CDN lifecycle policies.

**`model-deployment-platform`**: Large-scale AI model deployment platform with model serving, routing, caching, and rollback.

- Provide an LLM gateway with model/provider routing, rate limits, fallbacks, and tenant policies.
- Version models, prompts, tools, RAG configs, and eval gates before production rollout.
- Observability must track latency, token usage, cost, errors, safety blocks, and quality signals.
- Support canary, shadow traffic, rollback, exact/semantic caching, and capacity planning.
