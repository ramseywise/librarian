---
title: GenAI Maturity Model for Agentic Systems
tags: [harness, agents, reference]
summary: "A pattern-language book orders enterprise GenAI adoption into maturity levels and later collapses them into three roadmap stages; the numbering is inconsistent across its own chapters, and no outcome is measured."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-agentic-architectural-patterns-ch01-genai-enterprise-landscape-maturity-agent-fo.md
  - data/raw/papers/2026-11-08-agentic-architectural-patterns-ch02-agent-ready-llms-selection-deployment-adapta.md
  - data/raw/papers/2026-11-08-agentic-architectural-patterns-ch03-spectrum-llm-adaptation-agents-rag-fine.md
  - data/raw/papers/2026-11-08-agentic-architectural-patterns-ch12-practical-roadmap-implementing-agentic-patte.md
  - data/raw/papers/2026-11-08-agentic-architectural-patterns-ch16-conclusion-charting-agentic-ai-journey.md
---

# GenAI Maturity Model for Agentic Systems

The Packt book by Arsanjani and Bustos on agentic architecture is a pattern language. It describes how a team should climb from plain model use to coordinated agents, and it reports no measured results. The ladder is a planning vocabulary, not an empirically validated scale.

## The level ladder

Chapter 1 numbers adoption from level 0 to level 6: data (0), model and prompt (1), retrieval-augmented generation (2), tuning (3), grounding and evaluation (4), single agent (5), multi-agent (6). The reasoning is that each rung supplies something the next one needs: an agent without grounded, evaluated retrieval has nothing reliable to act on. Chapter 3 restates the idea as six agentic levels and separates a plain tool from an agent wrapped as a tool, and it treats retrieval, parameter-efficient tuning, in-context learning and grounding as the adaptation spectrum below the agent rungs.

## Model choice and operations below the agent rungs

Chapter 2 treats model selection, serving, security and operations as preconditions. It separates a model's effective context from its advertised context, suggests an orchestrator model with smaller worker models, lists four prompt-injection mitigations, and advises version-controlling prompts as part of agent operations.

## Collapse into a roadmap

Chapter 12 folds the six levels into three stages: foundational, production-ready and self-improving. Its advice is to start every workflow as a minimal agent at the lowest level and move up only when a trigger appears, such as scale, fault isolation or team velocity (more than three or four specialized agents is given as an illustration). Chapter 16 aligns three maturity scales in a table of five phases and contrasts prompt-first with pattern-first development.

## Why it matters

The useful part is the rule of starting small and escalating on evidence. It is consistent with the staged adoption ideas on the harness pages, though here the triggers are described in prose rather than quantified.

## Limits

- No experiment backs any level boundary; the chapters are design advice.
- Numbering is inconsistent: a table in chapter 6 places single agent at level 5 and multi-agent at level 6, while that chapter's summary says levels 4 and 5. Chapter 13 labels one agent as level 3, 4 and 5 in different places, and chapter 16 labels one case study agent both level 4 and level 2.
- Figures in chapter 16 (a drafting-time cut, a share of practitioners, a duration) are given without a source or setup.

## See Also
- [[Harness Maturity and Failure Modes]] — related (another staged-adoption view)
- [[MLOps Maturity Levels and CT vs CI/CD]] — related (a maturity ladder in a neighbouring field)
- [[Agentic Coordination Patterns Catalog]] — extends
- [[Robustness and Fault-Tolerance Pattern Ladder]] — extends
