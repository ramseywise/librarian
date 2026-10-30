---
title: Reflexion
tags: [prompting, llm, concept]
summary: Verbal reinforcement learning — an actor attempts, an evaluator scores, a self-reflection step turns the score into natural-language feedback kept in memory for the retry; it works only when you get a do-over and an objective evaluator, and reinforces confident mistakes with a weak one.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--03-core-techniques.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--06-chaining-and-workflows.md
---

# Reflexion

Shinn et al. (2023). Three components:

| Component | Role |
|---|---|
| **Actor** | Produces actions/text (CoT or ReAct) |
| **Evaluator** | Scores the trajectory — exact match, heuristics, unit tests, or an LLM judge |
| **Self-reflection** | Converts the score into natural-language feedback stored in memory for the next attempt |

Loop: attempt → evaluate → reflect → retry with the reflection in context. HumanEval
pass@1 reached 91% vs. GPT-4's 80% at the time.

## When it works

- **Only when you get a do-over** — useless for irreversible actions.
- **Ideally with an objective evaluator** (tests, compilers, checkers). With a weak
  evaluator it reinforces confident mistakes — the failure [[Verification Loops]]
  addresses by keeping the evaluator separate from the generator.
- Memory is a sliding window, so long retry histories get truncated.

## At the workflow level

Inside a [[Prompt Chaining]] workflow, task-level Reflexion means: check the output with a
validator, tests or a judge; on failure, re-prompt with the requirements, the failed
attempt and the critique. It is much more expensive than tightening the prompt — try that
first. It is the *evaluator–optimizer* pattern in Anthropic's taxonomy
([[Agentic Workflow Patterns]]). For code, compile/lint/test-and-feed-back is the second
biggest lever after context ([[Code Generation Prompting]]).

## See Also
- [[Verification Loops]] — extends
- [[Prompting Technique Selection]] — instance-of
- [[Agentic Workflow Patterns]] — instance-of (evaluator–optimizer)
- [[Loop Detection and the Two-Retry Rule]] — extends (bounding the retry budget)
