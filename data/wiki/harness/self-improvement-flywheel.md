---
title: Self-Improvement Flywheel
tags: [harness, agents, pattern]
summary: "A four-stage loop (generate, evaluate, learn, deploy) with the R5 operational model, planner-plus-scorer, synthetic data and coevolution, from a pattern book whose cost figures are uncited."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-agentic-architectural-patterns-ch11-advanced-adaptation-building-agents-learn.md
---

# Self-Improvement Flywheel

Chapter 11 proposes that agents improve by cycling through four stages: generate outputs, evaluate them, learn from the results, and deploy the update.

## Mechanisms

- **R5 operational model:** Relax covers context and latency limits; Reflect adds checkpoints with self-critique; Reference tracks where information came from; Retry handles errors adaptively; Report measures factuality, consistency and process quality.
- **Hybrid Planner plus Scorer:** a planner proposes steps and a scorer rates them; a named step score is used for ranking.
- **Preference-controlled synthetic data** feeding preference tuning and parameter-efficient tuning.
- **Coevolution:** two agents improve against each other. The book names collusion and runaway divergence as failure modes.
- Red teaming and a tokenomics discussion on cost.

## Limits

- The training-token cost multiple and the per-ticket cost comparison are invented or uncited.
- The promised tuning pseudocode is absent.
- No evidence the flywheel improves anything.

## See Also
- [[Post-Training for Agents]] — related
- [[Self-Refine]] — related
- [[Direct Preference Optimization]] — related
- [[GenAI Maturity Model for Agentic Systems]] — prerequisite-for
