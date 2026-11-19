---
title: Human-Agent Interaction Patterns
tags: [harness, agents, pattern]
summary: "Five patterns for who calls whom between people and agents, with escalation below a confidence threshold, plan confirmation and a credential-holding proxy; the chapter's numbers are invented illustrations."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-agentic-architectural-patterns-ch08-human-agent-interaction-patterns.md
  - data/raw/papers/2026-11-08-agentic-architectural-patterns-ch09-agent-level-patterns.md
  - data/raw/papers/2026-11-07-learning-langchain-ch11-building-with-llms.md
---

# Human-Agent Interaction Patterns

Chapter 8 names five patterns, split by direction: agent to human, human to agent (delegating or calling), agent to agent, and agent to a proxy agent. They differ in who starts the exchange and who holds authority.

## Mechanisms

- **Escalation:** the agent hands off to a person when its confidence falls below a threshold.
- **Plan Confirmation:** the agent shows its plan and waits for approval before acting.
- **Proxy agent:** a separate agent holds the credentials, so the working agent never sees them.
- **Ambiguity handling:** strategic ambiguity (a fuzzy goal) is resolved by the agent through planning, as in delegation, while tactical ambiguity (an unforeseen problem) triggers escalation to the human.
- The book adds a five-level human-adoption ladder, and chapter 9 an agent-level ladder (single-agent baseline, memory, retrieval, structured reasoning, multimodal) with a three-phase rollout and a warning about contextual and retrieval drift.

## Three UX patterns in a LangChain book (ch. 11)

Oshin and Campos ask how to give users an LLM when palette-and-canvas interfaces presume features known beforehand. They sketch three patterns with the components each requires:

| Pattern | What it needs |
|---|---|
| Interactive chatbot | At least a chat model and conversation history; streaming (per token or larger chunks) to mask latency; canvas operations exposed as tools (for example, read the selected text, insert at the end of the document); human confirmation or editing once tools can alter the canvas |
| Collaborative editing | Shared state, a task manager, merging of forks (by hand or with CRDT/OT), concurrency handling (interrupt, cancel, reroute, queue), an undo/redo stack, intermediate output |
| Ambient computing | Triggers, long-term memory, reflection, summarised output, a task manager |

They argue streaming chat may prove to be the LLM era's counterpart of the command line: a niche interface nearest to direct programming access. Ambient computing, in their view, differs from collaborative editing mainly on concurrency, since the LLM runs in the background as the user does something else. Reflection in this setting is a step where the LLM updates its long-term memory, perhaps revising its rules for spotting later events of interest. The authors identify the hard part of ambient alerts as defining "interesting" in advance so that it is useful and practical, and say LLM reasoning can stand in for hand-written rules. They close by advising a rough first build, conversations with users, and iteration.

## Limits

- All figures in chapter 8 are invented for illustration; none is measured.
- Chapter 9 simulates the model in code, so no behaviour is demonstrated.
- No guidance on choosing the escalation threshold.
- Learning LangChain ch. 11 is a conceptual argument with no experiments, code or evaluation; the authors add that these are not the only patterns and it will be a while before things settle.

## See Also
- [[HITL and Interrupt Patterns]] — related
- [[Execution Boundaries and Guardrails]] — related
- [[GenAI Maturity Model for Agentic Systems]] — prerequisite-for
