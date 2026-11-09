---
title: Retrieval Augmented Thoughts (RAT)
tags: [prompting, pattern]
summary: Zero-shot procedure that drafts a chain of thought, then revises each step in order using retrieval queried from the task, the already revised steps and the current draft step.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-wang-2024-rat.md
---

# Retrieval Augmented Thoughts (RAT)

RAT drafts a zero-shot chain of thought, then walks through it step by step. For step i it builds a retrieval query from the task prompt, the steps already revised and the current draft step, retrieves text, and rewrites the step with that text in context before appending the next draft step. The query comes from a text encoder (code drafts are embedded directly) or from an extra LLM query-generation prompt on writing and planning tasks. The revision prompt tells the model to check correctness, add ignored details, or return the answer unchanged.

## Reported results (self-reported)

- Code, zero-shot, pass@1 relative gain over direct prompting averaged 7.35% for CodeLlama-7b, 9.17% for GPT-3.5 and 13.63% for GPT-4. For GPT-4, average pass@1 was 67.55; the comparison points were 59.45 for direct prompting, 58.10 for CoT, 60.86 for retrieval-augmented generation with one document and 61.50 with five. Setup: HumanEval, HumanEval+, MBPP, MBPP+; corpus of 452k notebook markdown and code pairs; ada-002 embeddings.
- Math, GPT-3.5 with program generation, first 200 samples, three attempts averaged: GSM8K 71.36 against 65.85 direct; GSM-Hard 67.34 against 51.26. Zero-shot CoT scored below direct (54.27 average).
- Embodied planning in Minecraft, GPT-4, 100 tasks: executability 76.67 against 19.33 direct and 49.33 for zero-shot CoT; the 42.78% headline is a human-rated plausibility gain, not executability.
- Creative writing, GPT-3.5, Google search retrieval: win rate 81.01 against 46.67 for direct; plain retrieval variants scored below direct.
- Ablations on GPT-3.5 HumanEval: revised partial thoughts as the query beat whole-CoT queries (59.2 against 53.9 pass@1), and the causal query beat a non-causal one (59.2 against 57.3).

## Limits

- Cost, latency and call counts are not reported; roughly one retrieval and one revision call per step.
- Small test sets: 200 math samples, 100 Minecraft tasks, 9 writing prompts; human ratings without inter-annotator agreement; the Minecraft spread is wide (about 8 points).
- The math rows use program execution, so the CoT row is not pure text reasoning.
- Corpora are notebooks, Minecraft wikis or live search; gains depend on the corpus containing the facts, and other corpora are not shown. Only GPT-3.5, GPT-4 and CodeLlama-7b, versions not given. No comparison with tree-structured methods.
- Internal inconsistencies noted by the extraction: the prompt appendix says Bing where the setup says Google; GSM8K gain is given as 8.36% and 8.37%; a text figure of 18.44% for average GSM gain conflicts with the table's 16.96%. The abstract's per-domain figures mix models and are relative gains.

## See Also

- [[Chain-of-Thought Prompting]] — prerequisite-for
- [[Zero-Shot Chain-of-Thought]] — prerequisite-for (the draft is a zero-shot chain)
- [[RAG Retrieval Strategies]] — prerequisite-for
- [[Chain-of-Verification]] — alternative-to (revision after drafting)
- [[Program-Aided Language Models (PAL)]] — related
