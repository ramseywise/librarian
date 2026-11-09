---
title: Human-Agent Interaction Patterns
tags: [harness, agents, pattern]
summary: "Five patterns for who calls whom between people and agents, with escalation below a confidence threshold, plan confirmation and a credential-holding proxy; the chapter's numbers are invented illustrations."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-agentic-architectural-patterns-ch08-human-agent-interaction-patterns.md
  - data/raw/papers/2026-11-08-agentic-architectural-patterns-ch09-agent-level-patterns.md
---

# Human-Agent Interaction Patterns

Chapter 8 names five patterns, split by direction: agent to human, human to agent (delegating or calling), agent to agent, and agent to a proxy agent. They differ in who starts the exchange and who holds authority.

## Mechanisms

- **Escalation:** the agent hands off to a person when its confidence falls below a threshold.
- **Plan Confirmation:** the agent shows its plan and waits for approval before acting.
- **Proxy agent:** a separate agent holds the credentials, so the working agent never sees them.
- **Ambiguity handling:** strategic ambiguity (a fuzzy goal) is resolved by the agent through planning, as in delegation, while tactical ambiguity (an unforeseen problem) triggers escalation to the human.
- The book adds a five-level human-adoption ladder, and chapter 9 an agent-level ladder (single-agent baseline, memory, retrieval, structured reasoning, multimodal) with a three-phase rollout and a warning about contextual and retrieval drift.

## Limits

- All figures in chapter 8 are invented for illustration; none is measured.
- Chapter 9 simulates the model in code, so no behaviour is demonstrated.
- No guidance on choosing the escalation threshold.

## See Also
- [[HITL and Interrupt Patterns]] — related
- [[Execution Boundaries and Guardrails]] — related
- [[GenAI Maturity Model for Agentic Systems]] — prerequisite-for
