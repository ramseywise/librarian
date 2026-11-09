---
title: Syntriever Synthetic Retriever Training
tags: [rag, pattern]
summary: Train a small retriever from black-box LLM output only, in two stages (distil on synthetic positives, queries and hard negatives, then align to the LLM's pairwise preferences); hallucinated positives are relabelled as hard negatives.
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-kim-2025-syntriever.md
---

# Syntriever Synthetic Retriever Training

Syntriever needs no LLM logits. **Stage 1 (distillation):** GPT-4o writes chain-of-thought sub-query text, synthetic positive passages and hard negatives for each training query. A self-verification step flags synthetic positives that do not answer the query and relabels them as hard negatives; the paper says about 15% of HotpotQA positives were relabelled and only a few percent elsewhere. The loss is a soft-nearest-neighbour loss over the query, the labelled passage, a synthetic positive and the sub-query text; synthetic hard negatives only repel. **Stage 2 (alignment):** the LLM compares pairs among the retriever's top K (K=5, N=10 pairs by default) and the retriever is trained with a partial Plackett-Luce loss. The base encoder is E5-base (about 125M parameters). Numbers are the paper's (self-reported).

## Reported results

- **In-domain BEIR (nDCG@10), with every model fine-tuned on the dataset's own training split.** MS MARCO 50.3 against 42.4 for E5; HotpotQA 70.2 against 63.4.
- **Zero-shot on 15 BEIR sets, after training only on synthetic data built from MS MARCO and NQ.** Best on 8, second on 1. Table 2 shows losses, for example Arguana 38.8 against BGE-M3 61.5, Fever 60.2 against 75.3 for BM25, and Touche 19.9 against 36.7 for BM25.
- **Relabelling ablation.** With relabelling added, HotpotQA moves 67.4 to 70.2; FiQA moves from 40.8 to 41.9 and SciFact from 79.7 to 80.5.
- **Alignment.** Distillation alone averages +8.2% over the base retriever; alignment adds up to 8.8%. Partial Plackett-Luce beats Bradley-Terry on FiQA (41.9 against 35.7) and NFCorpus (43.3 against 36.1); the forgetting explanation is the authors' untested hypothesis.
- **Cheaper LLM.** GPT-4o-mini is competitive for distillation data (NFCorpus 42.6 against 41.4) while the stronger model helps more for alignment feedback (HotpotQA 68.6 against 70.2).
- **Noisy labels.** On 1000 samples judged by GPT-4o, 88% of synthetic positives and 84% of ground-truth passages were judged answer-bearing (judge and generator are the same model family).

## Limits

- Only about 125M encoders and English BEIR nDCG@10; latency, recall and end-to-end RAG are all unreported; LLM call cost is conceded but not counted.
- Baselines are published checkpoints while Syntriever trains on each dataset's synthetic data; the "18.6%" gain is relative and sits on in-domain MS MARCO.
- Contamination of BEIR in GPT-4o is not checked. Ablations use 5 datasets, one seed, no variance.

## See Also
- [[Tuning an Embedding Model from Match Labels]] — related
- [[Llama2Vec Unsupervised LLM Adaptation for Dense Retrieval]] — alternative-to
- [[RAG Reranking]] — related
- [[Promptagator Few-Shot Synthetic Retrieval Data]] — alternative-to
- [[Reader-Attention Distillation for Retrievers]] — alternative-to (retriever training signal from a reader)
