---
title: RAG Sequence and RAG Token
tags: [rag, concept]
summary: The original RAG recipe fine-tunes a BART generator with a frozen-index DPR retriever, marginalising over retrieved passages per sequence or per token, with an index that can be hot-swapped to update knowledge.
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-2005-11401v4.md
---

# RAG Sequence and RAG Token

Lewis et al.'s Retrieval-Augmented Generation recipe joins a pre-trained seq2seq generator, which acts as parametric memory, to a dense Wikipedia index acting as non-parametric memory. Training is end to end, with the retrieved documents treated as latent variables.

## Mechanism

A DPR bi-encoder (BERT-base) returns the K highest-scoring Wikipedia passages by MIPS, and BART-large conditions on the input concatenated with each passage. RAG-Sequence uses one document for the whole output; RAG-Token may draw a different document per token. Outputs are marginalised over passages. The query encoder and generator are fine-tuned by negative marginal log-likelihood; the document encoder and index stay fixed. Index hot-swapping means replacing the index at test time to update knowledge without retraining.

## Results

Self-reported.
- NQ test EM: RAG-Sequence 44.5 (50 docs, thorough decoding) compared with 41.5 for DPR and 36.6 for T5-11B+SSM; RAG-Token 44.1 (15 docs). T5-large (770M) scores 28.9 EM against 626M trainable parameters for RAG.
- TriviaQA: RAG-Sequence scores 68.0 on the TQA-Wiki test set, where T5-11B+SSM reaches 60.5; on the standard split it scores 56.8 against 57.9 for DPR. CuratedTrec 52.2 and WebQuestions 45.2.
- On NQ, RAG gets 11.8% of questions right even when no retrieved document holds the answer; an extractive model gets 0% there.
- Jeopardy question generation (452 human-judged pairs): human judges rated RAG-Token the more factual in 42.7% of pairs (BART: 7.1%); more specific in 37.4% against 16.8%. FEVER 3-way: RAG-Token 72.5 against BART 64.0; 2-way 89.5.
- With a frozen retriever, NQ dev EM falls from 44.0 to 41.2. A BM25 retriever gives 31.8 there, yet on FEVER-3 BM25 outperforms the learned retriever (75.1 against 74.5).
- Index hot-swap on 82 world-leader questions: matched indices answer 70% (2016) and 68% (2018); mismatched give 12% and 4%.
- More retrieved documents at test time improves RAG-Sequence monotonically; RAG-Token peaks at 10.

## Limits

- Training details (learning rate, batch size, steps, seeds) are missing, so it is not reproducible from the paper; single runs, no variance.
- The retriever starts from a DPR model trained with supervision on NQ and TriviaQA, and its document encoder and index are held frozen.
- Retrieval collapse on tasks like story generation, where the retriever returned the same documents regardless of input.
- Wikipedia (Dec 2018) is imperfect; human factuality raters could research online, and 20.8% of pairs had no majority.
- TriviaQA state of the art holds only on the T5-comparable split.

## See Also
- [[RAG Retrieval Strategies]] — prerequisite-for
- [[Atlas Retrieval-Augmented Few-Shot Learning]] — extends (joint retriever-reader pre-training)
- [[RA-DIT Dual Instruction Tuning]] — related
- [[Generate-then-Read Contextual Documents]] — alternative-to
