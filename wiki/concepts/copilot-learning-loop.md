---
title: Copilot Learning Loop
tags: [eval, memory, infra, pattern]
summary: The operational process for improving agent systems over time — signal capture from real usage, knowledge refinement workflows, and controlled autonomy expansion. Not automatic: requires deliberate instrumentation and tooling.
updated: 2026-04-25
sources:
  - raw/notion/2026-04-09-copilot-why-what-how.md
  - raw/notion/2026-04-07-support-knowledge-agent.md
---

# Copilot Learning Loop

Copilot does not improve automatically. It improves through structured feedback, analysis, and deliberate knowledge refinement. This is an **operational process**, not a technical feature.

---

## Signal Capture

Four categories of signals indicating where improvement is required:

### Direct User Feedback
- Corrections (user manually overrides Copilot suggestion)
- Ratings (thumbs up/down, explicit satisfaction signals)
- Overrides (user ignores suggested action and does something else)

### Behavioral Signals (implicit)
- Ignored suggestions
- Manual reversals after Copilot execution
- Escalation patterns (recurring topics that always escalate)
- Automation acceptance and rejection patterns

### Unresolved or Low-Confidence Conversations
- Questions that cannot be answered
- Conversations with `confidence_score < threshold`
- Conversations that escalate to human support
- Recurring questions indicating missing documentation

### Copilot-Specific Knowledge Signals
- Cases requiring CS/human escalation (show out-of-scope capabilities)
- Answers marked as incorrect
- Conversation threads revealing documentation gaps

---

## Internal Tooling & Analysis

Signal capture is useless without tooling to act on it. Internal tooling must enable:
- Exploration of failure cases and edge scenarios
- Identification of recurring knowledge gaps
- Detection of incorrect or misleading responses
- Validation of patterns before increasing autonomy

**Learning requires visibility. Visibility requires tooling.**

---

## Knowledge Refinement Workflow

For knowledge-based assistance specifically:

1. Support conversations and unresolved queries are systematically processed
2. Domain experts have workflows to correct, extend, or improve answers
3. Knowledge updates are versioned and reintegrated into retrieval systems
4. Improvements must measurably reduce recurrence of the same issue

Knowledge improvement is an operational process — not a one-time exercise.

Metrics for improvement actions: `time from unresolved question → KB update`, `reduction in repeated unanswered intents`, `KB coverage growth per quarter`.

---

## Controlled Autonomy Expansion

Autonomy must expand only where usage data demonstrates:
- **Stability:** the pattern is predictable and consistent
- **Correctness:** the system is right in measurable % of cases
- **Sustained user trust:** users accept rather than override

**Copilot improves through instrumentation, analysis, and controlled iteration — not through assumption.**

Do not increase autonomy based on LLM capability alone. Increase it based on measured evidence from real usage.

---

## Relationship to Evaluation Architecture

The Copilot Learning Loop is the operational layer above the technical [[RAG Evaluation]] architecture:

| Layer | Tool | Purpose |
|---|---|---|
| Real-time signals | Instrumentation + behavioral tracking | Detect issues in production |
| Human review | [[HITL Annotation Pipeline]] | Attribute failures to root causes |
| Automated eval | Golden datasets + LLM judges | Measure improvements quantitatively |
| Knowledge update | Domain expert workflows | Close the identified gaps |
| Regression gate | CI eval floor | Ensure improvements don't regress |

---

## Learning Loop vs RAG Evaluation

| Copilot Learning Loop | RAG Evaluation |
|---|---|
| Operational process | Technical measurement |
| Focuses on: what do we improve next? | Focuses on: how good is the system now? |
| Input: real user signals from production | Input: golden datasets, synthetic tests |
| Output: knowledge update priorities | Output: hit_rate, hallucination rate, MRR |
| Requires: internal tooling, domain expert time | Requires: evaluation harness, LLM judges |

Both are required. Neither alone is sufficient.

---

## Connection to [[Shine Knowledge Agent]]

The Shine knowledge agent's improvement over time depends entirely on a functioning learning loop. Without it:
- The system doesn't know which questions it's failing
- Documentation gaps remain undetected until they become user complaints
- The ≥60% self-service resolution target cannot be improved past its initial value

The learning loop is what makes the 60% target a floor, not a ceiling.

---

## See Also
- [[Shine Copilot Architecture]]
- [[Shine Knowledge Agent]]
- [[RAG Evaluation]]
- [[HITL Annotation Pipeline]]
- [[Evaluation & Improvement Project (VIR)]]
- [[Production Hardening Patterns]]
