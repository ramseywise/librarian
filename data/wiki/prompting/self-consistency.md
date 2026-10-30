---
title: Self-Consistency
tags: [prompting, llm, concept]
summary: Sample several chain-of-thought completions at non-zero temperature and take the majority answer — reasoning paths that converge are more trustworthy than any single greedy path, at N× cost and only when there is a single extractable answer to vote on.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--03-core-techniques.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--06-chaining-and-workflows.md
---

# Self-Consistency

Wang et al. (2022). Replace greedy decoding with **sample N CoT completions → extract each
final answer → majority vote**. Different reasoning paths that converge on one answer are
more reliable than any single path, because an autoregressive model can't backtrack out of
an early error ([[Prompts as Document Completion]]) — sampling gives it several starts.

**Use it** on arithmetic and commonsense tasks with a single extractable answer.
**Skip it** for open-ended generation, where there's nothing to vote on, and when N× cost
isn't affordable.

## Relatives

- **Branch-solve-merge** — fan out to N solvers (high temperature or different assigned
  perspectives), then a merge step *synthesizes* rather than votes.
- **Best-of-n** — N samples, keep the best by a *score* rather than a vote
  ([[Sampling Parameters]]).
- **Voting parallelization** in Anthropic's workflow taxonomy is the same pattern at the
  workflow level ([[Agentic Workflow Patterns]]).
- In ReAct experiments, the best knowledge-task results came from **ReAct ↔ CoT-SC**,
  falling back from one to the other when stuck or unsure ([[ReAct Pattern]]).
- [[Tree of Thoughts]] generalizes from independent samples to a searched tree.

## See Also
- [[Chain of Thought]] — extends
- [[Prompting Technique Selection]] — instance-of
- [[Tree of Thoughts]] — prerequisite-for
- [[Agentic Workflow Patterns]] — instance-of (voting parallelization)
