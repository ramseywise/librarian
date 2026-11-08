---
title: Self-Consistency
tags: [prompting, llm, concept]
summary: Sample several chain-of-thought completions at non-zero temperature and take the majority answer — reasoning paths that converge are more trustworthy than any single greedy path, at N× cost and only when there is a single extractable answer to vote on.
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--03-core-techniques.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--06-chaining-and-workflows.md
  - data/raw/papers/2026-11-06-mirzaei-2026-sample-more-reflect-less.md
  - data/raw/papers/2026-11-06-li-2024-more-agents-all-you-need.md
  - data/raw/papers/2026-11-06-li-2025-rethinking-mixture-agents.md
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

## Sample more or reflect (small-model study)

Mirzaei et al. (2026) compared self-consistency with reflection-style methods at equal token cost, using Qwen2.5 at 1.5B, 3B and 7B, with 150 questions drawn from each of GSM8K and MATH-500. Across 36 comparisons, none favoured the reflection method over self-consistency and 10 favoured self-consistency significantly (Holm correction within each setting) (self-reported). At 1.5B the Reflexion variant never fired, so that cell says little about reflection itself.

## Limits

Small question sets, three small models, and several internal count inconsistencies noted in the extraction; do not extend the result to frontier models.

## See Also
- [[Chain-of-Verification]] — related (the model checks its own draft with isolated questions)
- [[Chain of Thought]] — extends
- [[Prompting Technique Selection]] — instance-of
- [[Tree of Thoughts]] — prerequisite-for
- [[Agentic Workflow Patterns]] — instance-of (voting parallelization)
- [[Prompting Reasoning Models]] — alternative-to
- [[SelfCheckGPT]] — related (uses agreement across samples to flag hallucinated sentences)
- [[Branch-Solve-Merge]] — extends (samples different sub-problems instead of the same one k times)
- [[DeepConf Confidence-Filtered Voting]] — extends (confidence-filtered and early-stopped voting)
- [[Adaptive Branching MCTS]] — related (repeated sampling is its width-only baseline)
- [[MAKER Million-Step Decomposition]] — extends (first-to-ahead-by-k voting at each step)
- [[Self-MoA Single-Model Aggregation]] — extends (an aggregator model synthesises the samples instead of a vote; includes the sample-and-vote results of Agent Forest)
- [[TUMIX Tool-Use Mixture]] — related (heterogeneous tool-using agents, voted)
- [[Logic-of-Thought]] — related (combined with self-consistency in its experiments)
