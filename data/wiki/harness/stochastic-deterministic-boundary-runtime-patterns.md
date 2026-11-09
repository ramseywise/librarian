---
title: Stochastic-Deterministic Boundary Runtime Patterns
tags: [harness, pattern]
summary: A position paper that names the contract between an LLM proposer and a deterministic verifier, commit step and typed reject signal as the core of a production agent runtime, with six composable patterns.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-srinivasan-2026-methodology-selecting-composing-runtime-architecture.md
---

# Stochastic-Deterministic Boundary Runtime Patterns

Srinivasan (independent researcher, arXiv preprint, May 2026, not peer reviewed) names the stochastic-deterministic boundary (SDB) as the primitive of production agent runtimes. It has four parts: a proposer (the LLM), a verifier (a deterministic check), a commit (the durable write) and a reject signal (a typed response returned to the proposer).

## Structure

- **Concerns and patterns:** Coordination, State and Control, with six patterns: Hierarchical Delegation, Scatter-Gather plus Saga, Event-Driven Sequencing, Shared State Machine, Supervisor plus Gate, and Human in the Loop.
- **Gate and kill switch:** the paper says the gate is a deterministic rule check and policy belongs in code or a fast rule engine. The kill switch revokes a cancellation token in about a second, with cancellation checked at every tool boundary.
- **Method:** a five-step selection process ending in a six-line architecture decision record. The thesis that architectural momentum becomes the main reliability lever as per-call variance shrinks is called a metaphor, not a derived model.

## Reported numbers (author-classified)

- An audit of 5 open-source frameworks found logic for verifying and committing at 19 of the 21 places where an LLM output turns into an action.
- Of 21 published post-mortems, the author classified 15 (71.4%) as localised to the boundary, and 17 of the fixes (81%) made it stronger.
- Quoted second-hand from Promptfoo: moving from GPT-4o to GPT-4.1 reduced resistance to prompt injection from 94% to 71%.
- A cited issue in openai-agents-js reported rejected tool calls as completed, so the model hallucinated success.
- The reference application is a demo built on 100 renewal scenarios drawn from the IBM Telco Churn dataset, and it reports no measured results.

## Limits

- No benchmark, deployed system or measured reliability gain; no ablation, with alternatives argued in prose.
- The author built all five worked cases and classified the failures; the paper admits construction bias and no independent replication. The audit sample is tiny and its detail sits in a companion repository.
- Observed on contemporary models only; replay divergence is asserted, not measured; sandboxing and security isolation are out of scope.

## See Also
- [[Execution Boundaries and Guardrails]] — related (gates and kill switch)
- [[Verification Loops]] — related
- [[Production Reliability Primitives]] — related
