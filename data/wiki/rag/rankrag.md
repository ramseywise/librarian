---
title: "RankRAG"
tags: [rag, pattern]
summary: "RankRAG instruction-tunes one Llama3 model to both rerank retrieved passages and generate answers, using about 50k ranking examples; the 8B model averaged 52.6 over nine benchmarks against 49.6 for ChatQA-1.5 (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-yu-2024-rankrag.md
---

# RankRAG

RankRAG (arXiv-era preprint, Llama3 backbone) uses the generator as its own reranker. Relevance for a question and passage pair is the probability of generating "True". At inference the retriever returns the top N, the model scores them and the top k go into the prompt. Training has two stages: supervised fine-tuning on 128K examples, then a blend of context-rich QA, retrieval-augmented QA (gold passage plus BM25 negatives, five passages), MS MARCO ranking, conversational pseudo-ranking built from 150-word chunks and 4-gram recall, and retrieval-augmented ranking. The ranking part is about 50k pairs.

## Results (self-reported)

- Recall on NQ with the Dragon retriever, top 100 reranked: R@5 80.3 for RankRAG 8B, against 77.8 for RankLLaMA 8B and 78.0 for BGE-Rerank-v2-m3, with about 50k ranking examples against about 503k and about 1.6M for those rerankers.
- Nine general benchmarks, zero-shot, Llama3 backbones, KILT splits for NQ, TriviaQA and HotpotQA. Averages: RankRAG 8B 52.6 and 70B 56.1; ChatQA-1.5 at the same sizes 49.6 and 53.6; GPT-4-0613 42.0.
- Ablation on Llama3-8B: no reranking at inference 49.8 average (PopQA 49.3 against 57.6); dropping retrieval-augmented QA 51.6; dropping retrieval-augmented ranking 51.8; treating each context separately in fine-tuning (RAFT-style) 48.1; first-stage SFT alone 42.2.
- Reranking also helped a weaker retriever: with DPR, NQ R@5 rose from 69.50 to 77.95.
- Using ChatQA-1.5 8B as a reranker, without ranking data in its tuning, gave NQ R@5 of 68.2; the Dragon retriever alone had 74.9.
- Raising N from 20 to 100 added 0.9x to 6.0x time, against 20x to 100x expected.
- GPT-4-0613 TriviaQA EM was 84.8 without retrieval and 75.0 with it.

## Limits

- The paper has no limitations section; the authors say only that it improves single-time retrieval and leaves multi-round RAG to future work.
- Fine-tuning uses a private data blend with a crowd-sourced conversational part; no release of model or code is mentioned.
- KILT and DPR splits differ (2837 against 3610 NQ examples), so NQ and TriviaQA numbers need the split stated before comparing papers.
- Training cost was 32 A100s for 10 hours (8B) and 128 for 16 hours (70B).

## See Also
- [[RAG Reranking]] — prerequisite-for
- [[RAFT Retrieval-Augmented Fine-Tuning]] — related (RankRAG's ablation compares against RAFT-style training)
- [[RA-DIT Dual Instruction Tuning]] — alternative-to
- [[Dense Passage Retrieval (DPR)]] — related
- [[Contriever Unsupervised Contrastive Retrieval]] — related
