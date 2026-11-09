---
title: ADAPT-LLM Learned RET Token
tags: [rag, concept]
summary: "ADAPT-LLM fine-tunes Llama-2 7B on data labelled by where its own zero-shot answers fail, so it emits a RET token when it needs retrieval; on PopQA it edged out always-retrieve by 0.9 to 1.6 points while still asking for context on most questions."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-labruna-2024-when-retrieve.md
---

# ADAPT-LLM Learned RET Token

ADAPT-LLM (Labruna et al., 2024) teaches a language model to judge on its own whether a question calls for an external retriever. The hypothesis is that fine-tuning on data labelled by where the model's own zero-shot answers fail will make it emit a special `<RET>` token exactly when extra context is needed.

## Mechanism

Llama-2 7B is first tested zero-shot on a QA training set. Each question it answers correctly keeps the gold answer as the target of a parametric prompt. Each question it gets wrong becomes two training instances: a parametric prompt whose target is `<RET>`, and a context prompt with the gold passage and the answer. The model is then LoRA-fine-tuned. At inference time, a generated `<RET>` sends the question to Contriever for the top passage, which goes into a second prompt.

## Results (self-reported)

Setup: Llama-2 7B, LoRA-tuned on NQ or SQuAD, tested on the 14,282-question PopQA set with the top Contriever passage and exact match scoring.

- ADAPT-LLM trained on either SQuAD or NQ beats always-retrieve, by 0.9 to 1.6 points per the extraction's limits; the never-retrieve configuration trails the others by about 14 points.
- It requests context for most PopQA questions (82-87% by the extraction's note), so the retrieval saved is modest. Where it asks, accuracy with context is far above what the never-retrieve model manages without it; on the remaining questions it answers from its own memory, and the NQ-trained model does so accurately.
- The authors replicated the popularity-score rule (cut-off 707,000) on Llama-2 7B. It retrieves for nearly every question and scores about as well as ADAPT-LLM (on a 25% test split of PopQA). The SQuAD-trained model equals or beats it with less retrieval; the NQ-trained one scores 35.30% against 36.81% for the popularity rule.
- Gold passages outperform the top-1 Contriever passage by a wide margin on SQuAD dev and NQ dev, so the retriever is the bottleneck.

## Limits

- One 7B model, one test set (PopQA), a single top-1 passage; no seeds, variance or significance tests; cost and latency are not measured.
- Labels come from one zero-shot pass of the base model, and how well calibrated the RET decision is goes unstudied. The paper does not explain why SQuAD transfers better than NQ (the authors guess dataset scale).

## See Also
- [[PopQA and Popularity-Gated Adaptive Retrieval]] — prerequisite-for
- [[Self-RAG Reflection Tokens]] — alternative-to
- [[RL for Retrieval Policies]] — related
- [[Agentic RAG — Advanced Patterns]] — related
