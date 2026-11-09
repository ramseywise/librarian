---
title: Self-Controlled Memory Framework
tags: [memory, concept]
summary: Memory stream plus a prompted controller that decides when to retrieve, ranks by recency and relevance and chooses full text or summary; reported on a 105-question dialogue probe, where removing activation memory collapses accuracy (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-wang-2026-scm.md
---

# Self-Controlled Memory Framework

The Self-Controlled Memory framework (SCM; arXiv v4, March 2025) extends an LLM agent past its context window with three parts: the agent LLM, a **memory stream** and a prompted LLM **memory controller**. Each memory-stream entry holds an interaction index, the observation, the response, a summary and an ada-002 embedding. Per turn a six-step loop runs. The controller decides whether to activate memory, retrieves the top-k entries by a rank score that adds a recency score and a relevance score, and chooses for each whether to use full text or its summary (a summary is used only for activated memories longer than 800 tokens, and only once the total passes 2,000 tokens). **Flash memory** keeps the previous turn; **activation memory** holds the retrieved history. No fine-tuning is involved.

## Results (self-reported)

Setup: a probing set for long-term dialogue with 105 questions (49 single-turn and 56 multi-turn), in English and Chinese, spanning up to 200 turns and 34k tokens; ablations on SCM over text-davinci-003.

- Answer accuracy 77.1 for SCM on text-davinci-003 against 68.3 on gpt-3.5-turbo; retrieval recall for memory is about 94 in both cases.
- Removing activation memory leaves 10.5 answer accuracy and 0.0 retrieval recall and multi-turn accuracy.
- Removing the controller (full retrieved content concatenated, truncated at 2,500 tokens) gives 59.3 (-17.8), with multi-turn accuracy down 25.6 points against 7.9 for single-turn.
- Removing flash memory costs little: 72.9 (-4.2).
- In blind human side-by-side summarisation of books (10) and meetings (20), SCM on davinci-003 wins over SCM on turbo and over the RecursiveSum baseline; the numeric win rates appear only in a figure.

## Limits

- Evaluation stops at 200 turns and 34k tokens even though the paper claims unlimited length (the authors concede this), and the approach needs strong instruction-following models.
- The benchmark is small, 18 dialogues; seeds, variance and decoding settings are missing, and the annotator count and any dataset release are not stated.
- The turbo variant underperforms davinci-003, which the authors conjecture is conservatism on privacy questions.
- The PDF prints no venue; the extraction notes a ledger venue (DASFAA 2026) cannot be verified from it.

## See Also
- [[Memory Architecture]] — prerequisite-for
- [[Agent Memory Types]] — prerequisite-for
- [[MemGPT / Letta Virtual Context Memory]] — alternative-to
- [[ExpeL Experiential Learning]] — related
