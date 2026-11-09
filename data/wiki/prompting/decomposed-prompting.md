---
title: Decomposed Prompting (DecomP)
tags: [prompting, pattern]
summary: A decomposer prompt emits tagged sub-questions that a controller routes to separate handlers, which can be few-shot prompts, recursive decomposers or symbolic tools such as retrieval.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-khot-2022-decomposed-prompting.md
---

# Decomposed Prompting (DecomP)

DecomP separates planning from execution. A decomposer prompt, given the question and the sub-answers so far, writes the next sub-question labelled with a handler name in brackets, and ends with an end-of-question token. A symbolic controller sends each sub-question to its handler, appends the answer (referenced by index) to the decomposer's history, and supports operators such as foreach over list answers. A handler may be a separate few-shot prompt, a further decomposer (recursion), or a non-LLM function such as an Elasticsearch retriever. Each hard sub-task therefore gets its own prompt rather than sharing one chain-of-thought prompt.

## Reported results (self-reported unless noted)

- k-th letter concatenation (k=3, space delimiter), text-davinci-002, average of 3 prompts: near-perfect exact match for 3 words against 22.7 for chain-of-thought; at 5 words 97.0 against 6.0 (CoT), 53.3 (CoT with rollout) and 66.0 (least-to-most with rollout).
- List reversal by recursion, text-davinci-001, test lengths 4 to 10 items: 42 exact match at 10 items against 1 for CoT with rollout and 4.5 for plain CoT (the extraction infers the series from legend order).
- CommaQA-E reduced IID split, text-davinci-002: 59.7 against 42.0 for CoT.
- Open-domain QA with code-davinci-002 and retrieval, Decomp-Ctxt: 64.1 F1 on 2WikiMultihopQA against 47.1 for a retrieval baseline without decomposition and 38.1 closed-book (K chosen on a 100-question held-out set). Swapping in Flan-T5-XXL as the QA model gives 63.3 F1.
- Math QA with Wei et al. CoT prompts: swapping the regex answer extractor for a GPT-3 handler gained 14 to 17 points.
- With weaker models every method falls; DecomP stays ahead of CoT until scores near zero on curie.

The extraction notes that letter-concatenation errors were only in sub-task execution, not in the decomposition, and that reversing a list by splitting off the tail stays more stable at length but costs O(n) calls, against O(log n) for halving.

## Limits

- Decompositions and sub-task prompts are written by hand for each task, with no automatic decomposition and with no estimate of how much human effort that takes.
- The models used are GPT-3-era ones and Flan-T5 were used; Flan-T5 cannot write the structured decomposition, so a GPT-3-sized decomposer remains necessary.
- The baselines are variants of CoT plus least-to-most prompting, and no comparison with each task-specific system.
- Partly synthetic tasks; small evaluation sets (100 letters, 300 open-domain QA, 200 to 300 math subsets). Temperature, token limits, retriever settings and seeds are not given; each result averages three prompt choices. No figures are given for the expense or delay of making many sequential calls.

## See Also

- [[Chain-of-Thought Prompting]] — prerequisite-for
- [[Least-to-Most Prompting]] — alternative-to
- [[Prompt Chaining]] — related (fixed pipelines of prompts)
- [[Self-Ask Prompting]] — alternative-to
- [[Branch-Solve-Merge]] — alternative-to
