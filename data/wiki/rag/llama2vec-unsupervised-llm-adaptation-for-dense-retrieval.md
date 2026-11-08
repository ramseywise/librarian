---
title: Llama2Vec Unsupervised LLM Adaptation for Dense Retrieval
tags: [rag, pattern]
summary: Continued pre-training of LLaMA-2-7B with two label-free tasks (predict the input's own words and the next sentence's words from the final-token embedding) before standard retriever fine-tuning; reported gains over RepLLaMA on MS MARCO and BEIR.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-liu-2023-llama2vec.md
---

# Llama2Vec Unsupervised LLM Adaptation for Dense Retrieval

Llama2Vec adds an unlabelled adaptation step so that an LLM's final-token embedding captures the global meaning of a sentence. Two prompts append special tokens to a sentence and train its embedding to predict (a) the vocabulary of the sentence itself (EBAE) and (b) the vocabulary of the next sentence (EBAR). The two suffixes are masked from each other so one pass yields both, which the authors say saves almost half the compute. Setup: LLaMA-2-7B, DPR-curated Wikipedia, 10,000 steps, batch 256, length 1024, learning rate 1e-5; fine-tuning copies the RepLLaMA recipe: LoRA, contrastive loss and hard negatives mined with ANN search. Numbers below are the paper's (self-reported).

## Reported results

- **MS MARCO passage dev, 7B, hard negatives.** MRR@10 is 43.1 with Recall@1000 at 99.5; RepLLaMA gets 41.2 and 99.4; OpenAI's Ada-002 embedder gets 34.4 and 98.6; BM25 gets 18.4 and 85.3. On DL'19 NDCG@10 it scores 73.4, below RepLLaMA's 74.3, which the authors blame on the small test set.
- **MS MARCO document dev.** MRR@100 47.9 against 45.6 for RepLLaMA, credited to encoding whole documents.
- **BEIR zero-shot (14 datasets, trained on MS MARCO only).** Average NDCG@10 56.4 against 53.9 RepLLaMA, 51.4 Ada-2 and 42.9 BM25; better than BM25 on 13 of 14 sets.
- **Prompt choice per task.** Picking the best of three prompt pairings per dataset gives a 57.4 BEIR average against 56.1 for the default query-next, document-self pairing.
- **Dimension reduction hurts.** MRR@10 falls from 43.1 at 4096 dimensions to about 41 at 768 (linear projection or sparsification).

## Limits

- Tested only on a 7B model and English; no latency, index-size or throughput figures; no hybrid BM25 plus dense experiment; fine-tuned on MS MARCO only, with no ablation of the two adaptation tasks separately.
- Internal inconsistency: BEIR average is 56.4 in Table 3 but 57.4 for the per-task prompt choice in Table 5, and the paper does not reconcile them.
- The extraction reads Table 3 as showing BM25 ahead on Touche (44.2 against 34.2), an inference from flattened columns that the authors do not state.
- Baselines (Ada-002, text-embedding-3) date from late 2023; one baseline, bge-m3, is from the same group.

## See Also
- [[Tuning an Embedding Model from Match Labels]] — related
- [[GritLM (Generative Representational Instruction Tuning)]] — alternative-to
- [[Syntriever Synthetic Retriever Training]] — alternative-to
