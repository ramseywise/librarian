---
title: Closed-Book QA with T5
tags: [rag, concept]
summary: "Closed-book QA fine-tunes a T5 model to answer from the question alone; accuracy scales with size and salient span masking, and exact match undercounts correct answers."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-roberts-2020-how-much-knowledge-can-you.md
---

# Closed-Book QA with T5

Closed-book QA fine-tunes a pre-trained text-to-text model to emit the answer with no external documents or context. The contrasting **open-book** setting retrieves from an external source. The study fine-tunes T5 and T5.1.1 up to 11B parameters on Natural Questions, WebQuestions and TriviaQA, optionally after 100,000 extra steps of **salient span masking** (SSM; one entity or date per sentence is hidden).

## Results

Setup: T5 sees only the question, scoring is normalised exact match, decoding is greedy, and the checkpoint is picked on validation. All self-reported.

- T5.1.1-XXL + SSM scores 35.2 on open-domain Natural Questions dev and 42.8 on WebQuestions (open-book DPR: 42.4). On TriviaQA dev it gets 51.9, under open-book DPR's 57.9; on the TriviaQA test leaderboard for the Wikipedia domain it gets 61.6.
- Original T5 on Natural Questions rises from 25.9 (Base) to 32.6 (11B); TriviaQA dev from 23.8 to 42.3.
- SSM adds to T5-11B: Natural Questions 32.6 to 34.8. T5.1.1-XXL without SSM scores 32.8.
- Multi-answer Natural Questions validation recall for T5-11B + SSM is 36.2, above the best dataset baseline (33.2) and below the state of the art (51.9).
- The authors inspected 150 Natural Questions validation misses by hand and found just 62.0% to be true negatives (20 phrasing mismatches, 20 incomplete annotations, 17 unanswerable). From this they extrapolate an adjusted accuracy of 57.8.
- Extra span-corruption pre-training on Wikipedia made virtually no difference, while pre-training on Wikipedia from scratch was dramatically worse. Multitask fine-tuning added 0.5 on Natural Questions and was slightly worse on the other sets.

## Limits

- State-of-the-art results need the largest models (about 11B), which is costly.
- No indication of which information was used; the model hallucinates realistic answers when unsure; facts cannot be updated or removed.
- The tasks measure trivia-style knowledge, not reasoning.
- Exact match undercounts correct answers; the 57.8 adjustment rests on a 150-example inspection.
- The paper omits dataset sizes, hardware, compute, seeds and tokenizer.

## See Also
- [[RAG Retrieval Strategies]] — prerequisite-for
- [[Fusion-in-Decoder]] — extends (adds retrieval to closed-book generative QA)
- [[REALM Retrieval-Augmented Pre-Training]] — related
- [[Dense Passage Retrieval (DPR)]] — related (open-book comparison)
- [[RAG vs Long Context: Evaluation Evidence]] — related
