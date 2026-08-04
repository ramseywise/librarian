---
title: Heuristic Pipeline Metrics
tags: [eval, infra, observability]
summary: Automated measurement of operational health — latency, error rate, token usage, retrieval recall — that runs alongside every eval rung and is explicitly never sufficient alone, since a fast cheap wrong answer still fails.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/skills/project-discovery/reference/eval-approaches.md
---

# Heuristic Pipeline Metrics

Automated measurements of system *behavior*: latency (how fast?), error rate (how
reliable?), token usage (how expensive?), retrieval recall (how complete?). These measure
operational health, not answer quality.

**Use when** monitoring production health; detecting degradation before users complain;
tracking cost and performance over time; or alongside any other eval approach.

**Avoid as the only evaluation** — the governing caveat is blunt: *"a fast, cheap wrong
answer still fails."* Also unavailable pre-deployment, since there's no traffic to measure.

## Why it sits outside the ladder

The [[Eval Ladder]] rungs all measure *quality* and progress with project maturity. These
metrics measure *health* and run continuously at every rung. They're orthogonal — a system
can be green on latency and error rate while answering wrongly, and a system can be
accurate while too slow to use.

Their diagnostic value is strongest in combination: a quality regression with flat
operational metrics points at the model or prompt; one accompanied by latency and error
spikes points at infrastructure.

## Scaffold mapping

- Always available in the eval suite — latency and token tracking are built into the
  pipeline.
- `optional_features: [promptfoo]` adds HTTP-level performance testing.

## See Also
- [[Manual Review as Eval Bootstrap]] <!-- auto-linked -->
- [[Eval Ladder]] — complements (orthogonal health axis)
- [[User Feedback Loops]] — complements (separates engagement shift from regression)
- [[RAG Eval Metrics Suite]] — extends (retrieval-specific metrics)
- [[Observability & Evaluation Glossary]] — related
