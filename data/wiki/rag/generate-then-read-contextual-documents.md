---
title: Generate-then-Read Contextual Documents
tags: [rag, pattern]
summary: GenRead replaces the retriever with an LLM that writes background documents for a question, using clustering-based prompts for diversity; it matches or beats retrieval on some QA sets but not NQ, and merging both sources scored highest.
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-yu-2022-generate-rather-than-retrieve.md
---

# Generate-then-Read Contextual Documents

GenRead (Yu et al., ICLR 2023) tests whether an LLM can stand in for the retriever of a retrieve-then-read pipeline by producing the context documents itself. The authors hypothesise that such generated documents hold the answer more frequently and fit the question more closely than retrieved ones.

## Mechanism

text-davinci-002 (175B) writes a background document per question. Zero-shot, one greedy document is read by the same model. Supervised, it writes K=10 documents using clustering-based prompts and a FiD reader fine-tuned from T5 (770M or 3B) reads them. The clustering prompt clusters question-document embeddings into K groups, samples demonstrations from each cluster and generates one document per cluster, to raise answer coverage.

## Results

Self-reported.
- Supervised, FiD-xl, 10 generated documents: beats DPR-FiD on TriviaQA and WebQ, loses on NQ. The best setting on all three combines retrieved and generated documents, giving TQA 74.3, WebQ 56.2 and NQ 54.0.
- Clustering prompts beat nucleus sampling on average EM.
- Zero-shot, greedy: adds 6.9 EM on average over the no-document prompt across NQ, TriviaQA and WebQ. On NQ it falls below DPR + InstructGPT but is near Google + InstructGPT.
- Generated documents beat retrieved ones on TriviaQA Recall@1, but NQ answer coverage is lower than DPR's because generation is less diverse.
- Among InstructGPT sizes, just the largest generator outperforms DPR-FiD; Codex scores highest and OPT is below InstructGPT but near DPR.
- Cost: generating 10 documents costs fewer FLOPs than DPR only when there are fewer than about 2473 questions (DPR encoding 21M documents once at 2.3e17 FLOPs vs 9.6e13 per question).
- Of 100 inspected NQ predictions, 29 traced to annotation mistakes (13 temporal, 16 incomplete answers); the authors estimate time-dependent answers in about 16.5% of NQ questions.

## Limits

- Knowledge cannot be updated or moved to a new domain without retraining the LLM, unlike swapping a retrieval index.
- Generated documents can hallucinate and are less diverse than retrieved ones.
- Three LLMs only; 10 documents rather than 100, so comparison to published FiD mixes document counts.
- No seeds or variance; closed API model hinders reproduction; training-data overlap with the QA benchmarks is unexamined.

## See Also
- [[RAG Retrieval Strategies]] — prerequisite-for
- [[HyDE Hypothetical Document Embeddings]] — related (generated text used to retrieve rather than to read)
- [[Query2doc LLM Query Expansion]] — related
- [[RAG Sequence and RAG Token]] — alternative-to (retrieval-based baseline compared in the paper)
