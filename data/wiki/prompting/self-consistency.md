---
title: Self-Consistency
tags: [prompting, llm, concept]
summary: Sample several chain-of-thought completions at non-zero temperature and take the majority answer — reasoning paths that converge are more trustworthy than any single greedy path, at N× cost and only when there is a single extractable answer to vote on.
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--03-core-techniques.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--06-chaining-and-workflows.md
  - data/raw/papers/2026-11-06-mirzaei-2026-sample-more-reflect-less.md
  - data/raw/papers/2026-11-08-barkley-2024-investigating-role-prompting-external-tools.md
  - data/raw/papers/2026-11-06-li-2024-more-agents-all-you-need.md
  - data/raw/papers/2026-11-06-li-2025-rethinking-mixture-agents.md
  - data/raw/papers/2026-11-08-hu-2024-rankprompt.md
  - data/raw/papers/2026-11-08-prabhu-2024-pedal.md
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

## Prompting versus tools and abstention (8B study)

Barkley and van der Merwe (2024) ran an 8B Llama-3 instruct model quantised to Q6_K, served through Ollama and LangChain, three runs per setting. Self-consistency at temperature 0.8 was best on GSM8K: 83.89 for SC-CoT against 77.08 for a control (self-reported). On TriviaQA, a Chat Protect method reached 82.49% on the 571 of 1000 questions it answered and cut hallucinated answers from 399.67 to 100 (self-reported). A ReAct agent on Llama-3.1-8B scored 60.23 against 83.47 for a prompting setup on GSM8K. Limits: one 8B model, no statistical tests, agent and prompting setups differ, and abstaining methods are not comparable without their Correct counts.

## Selecting among samples without a vote (RankPrompt, PEDAL)

Hu et al. (2024) sample 5 few-shot chains (temperature 0.7) and ask the same model to compare them step by step, using one auto-built comparison exemplar kept only if it reached the right answer. They report gains over CoT and majority voting on 8 reasoning tasks with gpt-3.5-turbo and 5.2% to 9.2% over CoT on three BBH tasks with gpt-4, and, on AlpacaEval, agreement with human preference of 74.33% (self-reported). The extraction left most per-method averages blank. Limits: only proprietary models, single runs, and the CoT baseline is one greedy sample, so compute is not matched. ARC gains are tiny (87.42 against 87.57 for the exemplar-free variant).

Prabhu (2024) builds several prompts from differently seeded exemplars, takes one greedy answer per prompt, then has the model pick the most consistent one. On SVAMP with Llama-3-8B-Instruct it scores 74.11 against 70.22 greedy and 72.99 for universal self-consistency, using 197.72 output tokens against 923.56; on Qwen2-7B-Instruct universal self-consistency is more accurate (self-reported). Limits: two small datasets (300 and 345 items), gains within seed noise on some cells (ARC Qwen2 +0.39), the cost count covers output tokens only and PEDAL uses more input tokens, and the comparison with single-chain CoT is interpolated, not run.

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
- [[Medprompt]] — extends (a shuffled-choice ensemble on top)
- [[Aggregation of Reasoning (AoR)]] — extends
- [[Direct-Indirect Reasoning (DIR)]] — extends
- [[CoT-Decoding]] — alternative-to
- [[Chain-of-Thought Prompting]] — related (the sampled chains it votes over)
- [[Multi-Expert Prompting]] — alternative-to
