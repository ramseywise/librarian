---
title: "Lost in the Middle"
tags: [context, concept]
summary: "Models given a long prompt use information at its start and end better than information in the middle; GPT-3.5-Turbo with 20 documents scored 75.8% with the answer first but 53.8% at index 9, below its closed-book 56.1% (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-building-ai-agents-llms-rag-kgs-ch06-advanced-rag-techniques-information-retriev.md
  - data/raw/papers/2026-11-07-liu-2023-lost-middle.md
  - data/raw/papers/2026-11-08-wu-2024-efficient-recipe-long-context-extension.md
  - data/raw/papers/2026-11-08-xiong-2024-artificial-needles-real-haystacks.md
  - data/raw/papers/2026-11-08-machlab-2024-llm-context-recall-prompt-dependent.md
---

# Lost in the Middle

The position of relevant information in a long input changes how well a model uses it. The original study calls the better use of the beginning primacy bias and of the end recency bias.

## The original study

Six models were prompted as-is with k NaturalQuestions-Open passages, only one of which held the answer, and its slot was varied; a synthetic UUID key-value task was used likewise. Accuracy counts a gold answer appearing in the output, greedy decoding.
- GPT-3.5-Turbo, 20 documents (about 4K tokens): 75.8% when the answer came first, 53.8% when it was at index 9, which is under its closed-book score of 56.1% (self-reported). With 30 documents in the 16K variant: 73.4% first against 50.5% at index 9.
- Extended-context models did almost the same as base versions when the input fit both windows. Placing the query before and after the key-value pairs let a 16K model solve a 300-pair task perfectly, against a worst case of 45.6%.
- Instruction tuning shrank one 30B model's worst-case gap from nearly 10% to about 4%. Llama-2 7B showed only recency bias; 13B and 70B showed a U shape.
- In open-domain QA, raising retrieved documents from 20 to 50 gave GPT-3.5-Turbo a gain of only about 1.5%.
- A new protocol reports the gap between the best and worst position.

## Follow-ups

- Position-index fine-tuning (CREAM) fine-tunes Llama-2-7B at 4K with middle positions drawn from a truncated Gaussian, and beat PoSE by over 20% on average on the key-value task (self-reported). Middle accuracy stayed far below the edges, notably at 140 keys (8.0 at one middle position), and the authors concede decoder-only models inherently show the U shape.
- Fine-tuning on synthetic numeric key-value retrieval, with an answer template, flattened the U-shaped curve of GPT-3.5 Turbo and removed one 7B model's primacy bias on 20-document QA, with TriviaQA essentially unchanged for the 7B model (+0.11) while three long-context baselines lost 2.19 to 6.33 points (self-reported). It did not help when distractors were retrieved to be relevant.
- A needle recall study with GPT-4 Turbo as judge found recall depends on the needle: a needle that conflicts with training knowledge was recalled far worse than a made-up one at haystacks up to 128k, while another needle was recalled perfectly. Among 7B-class models, one version was unreliable beyond roughly 1k tokens and its successor recalled much better after three simultaneous changes that were not ablated.

## Reordering as a mitigation

A chapter on advanced RAG recommends placing the strongest passages at the start and end of the prompt and the weakest in the middle, as a response to this effect. The chapter reports no measurement of that reordering.

## Limits

- The original study uses one QA dataset and a synthetic task, exactly one relevant document, greedy decoding only, a GPT-4 run on a 500-example subset, API model versions that have since been retired, a single run per setting with no significance tests, and hypothesized mechanisms.
- The follow-ups are single runs on 7B-scale or API models; the needle study scores with a model judge that can misscore and uses near-trivial single-fact questions. Several fine-tuning results are curves with no tables. CREAM's PoSE numbers in one table come from a different base model. The synthetic fine-tuning study gives inconsistent epoch counts (3 in one section, 2 in the appendix).

## See Also
- [[Why Context Is Finite]] — prerequisite-for
- [[Long-Context Prompting]] — prerequisite-for
- [[NeedleBench]] — related
- [[LongBench]] — related
- [[Context Failure Modes]] — related
- [[NoiserBench Beneficial and Harmful RAG Noise]] — related (gold-in-the-middle noise study)
