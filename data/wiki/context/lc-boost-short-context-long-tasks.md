---
title: LC-Boost Short-Context Processing of Long Inputs
tags: [context, pattern]
summary: "LC-Boost has a short-context LLM walk a long input chunk by chunk, choosing actions such as retrieve, append and merge to accumulate evidence before answering; with a 4K working context it led on multi-document QA but not on code completion, and cost more tokens on aggregation tasks (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-qian-2024-long-llms-necessity-long-context.md
---

# LC-Boost Short-Context Processing of Long Inputs

The 2024 preprint (under review) asks if a short-context LLM can handle long-context tasks by choosing which parts of the input to access and use, with no long-context model needed. The authors expect most such tasks to be short-context solvable, meaning oracle short contexts inside the input are enough to answer them.

## Mechanism

LC-Boost splits the long input into chunks. A short-context model (GPT-3.5-turbo-16K, limited here to a 4K working context) first reads a task-understanding prompt and picks a processing strategy. It then loops over chunks, choosing from a discrete set of actions (Retrieve, Move, Append, Merge, Answer, Aggregation), accumulating extracted evidence, and finally answers. Retrieve uses a BGE reranker or embedding retriever. The actions come from a fixed set because predicting them freely proved unstable on GPT-3.5.

## Results (self-reported)

Twelve datasets, mostly LongBench, with GPT-3.5-turbo-16K as the base.

- Multi-document QA: 56.4 against 49.1 for the next best baseline (DeepSeek-v2), with a 4K context.
- Better than its own base model on single-document QA and the synthetic tasks, and a small gain on summarization. It did not win code completion, where Yi-9B-200K scored higher.
- On a self-constructed whole-context reasoning set (32 queries, average length 39,420), 47.7 against 32.9 for GPT-3.5-turbo-16K.
- Token use on NarrativeQA was a third of brute force, but on GovReport it was higher (112%).
- A pilot study reports LC-Boost at 4K matching or beating GPT-4-128K brute force on all LongBench task groups; the text gives no values, only bar heights.
- In an ablation, dynamic action selection beat fixed strategies, especially for single and multi-document QA, except for few-shot SAMSum (values appear only in Figure 3).
- Yi-9B-200K scored 72.1 on code yet 14.6 on few-shot tasks; the authors infer that long-context adaptation may harm general ability.
- One case, counting single-author ACL 2023 papers from a 45K context: LC-Boost answered 8, which the paper marks correct; other models answered 11, 0 and 1.

## Limits

- The authors concede some tasks may need the whole context, where LC-Boost may fail. Only GPT-3.5 was used as base, because the open-source models lacked zero-shot instruction following.
- The extraction notes there are no seeds, variance or significance tests, and that chunk size, top-k and decoding settings go unstated, as does any code release. The self-constructed set has 32 queries.
- The extraction notes that the theory depends on assumptions, namely independent chunks and optimal compression, which seldom hold in practice.
- The extraction notes that the energy comparison pits Llama2-7B-128K against Llama2-7B-chat-4K, different models, and includes multi-GPU effects; the text gives no numbers.

## See Also
- [[Long-Context Prompting]] — related (the brute-force alternative this compares with)
- [[Context Retrieval Strategies]] — related
- [[RAG vs Long Context: Evaluation Evidence]] — related
- [[MemWalker Summary-Tree Navigation]] — related (another way for a bounded window to traverse long text)
