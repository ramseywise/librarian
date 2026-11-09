---
title: Robustness and Fault-Tolerance Pattern Ladder
tags: [harness, agents, pattern]
summary: "A five-level ladder of 17 resilience patterns for agent systems, from hardcoded behaviour to mesh defence, with a retry-restart-fallback-escalation chain; the code contradicts the prose in several places."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-agentic-architectural-patterns-ch07-robustness-fault-tolerance-patterns.md
  - data/raw/papers/2026-11-08-agentic-architectural-patterns-ch10-system-level-patterns-production-readiness.md
---

# Robustness and Fault-Tolerance Pattern Ladder

Chapter 7 groups 17 patterns into five levels. Level 1 is hardcoded behaviour. Level 2 adds parallel consensus, a watchdog and adaptive retry. Level 3 adds auto-healing, a fallback model, checkpointing, rate limiting and delayed escalation. Level 4 adds a causal graph, trust decay and canary releases. Level 5 adds mesh defence, envelope isolation and majority voting.

## The failure chain

A fault is handled in order: retry the call, restart the component, fall back to another model, then escalate to a human. Each step is tried only when the cheaper one fails.

## System-level companions

Chapter 10 adds registry, compliance monitoring, authentication and authorisation, and event-driven reactivity. Its rollout order is secure first, registry last. Safeguards named include default-deny, OAuth client credentials, a dead-letter queue and idempotent handlers.

## Limits

- Prose and code disagree: the watchdog timeout is 10 seconds in code and 5 in prose; the trust decrement is 0.1 in one place and 0.2 in another.
- The firewall example defaults to allow, the subprocess sandbox does not block filesystem listing, and the trust code has no decay despite the name.
- Majority voting assumes errors are independent, which models from one family may not satisfy.
- The authorisation code accepts a bare role name in place of a real token, and the performance-indicator section appears cut off.

## See Also
- [[Production Reliability Primitives]] — related
- [[Idempotent Retries and Request IDs]] — related
- [[Loop Detection and the Two-Retry Rule]] — related
- [[GenAI Maturity Model for Agentic Systems]] — prerequisite-for
