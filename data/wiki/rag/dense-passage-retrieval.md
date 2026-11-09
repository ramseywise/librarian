---
title: Dense Passage Retrieval (DPR)
tags: [rag, pattern]
summary: "DPR trains two BERT encoders on question-passage pairs with in-batch and BM25 hard negatives, so a dot-product index over passages can replace BM25 for open-domain QA."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-karpukhin-2020-dense-passage-retrieval-open-domain.md
---

# Dense Passage Retrieval (DPR)

DPR asks whether a dense retriever can be trained from existing question-passage pairs alone, with no retrieval-specific pretraining, and still beat BM25. Two independent BERT-base uncased encoders (one for questions, one for passages) map text to 768-dimensional [CLS] vectors scored by dot product. The 21M Wikipedia passages (100 words each) are embedded ahead of time and served from a FAISS index. For end-to-end QA, an extractive BERT reader that also scores passages reranks the top-k.

## Training recipe

The loss is negative log-likelihood over one positive passage and a set of negatives. Two kinds of negative matter. **In-batch negatives** reuse the gold passages of the other questions in the mini-batch, so each question gets B-1 negatives for free out of one BxB matrix of scores. One BM25 hard negative per question is added on top.

- In-batch negatives raise top-20 accuracy on Natural Questions dev over training against 7 gold negatives without them, and accuracy keeps rising as the in-batch count grows (127 versus 7) (self-reported).
- One BM25 hard negative per question gives a substantial top-20 lift on Natural Questions dev; adding a second brings nothing more (self-reported).
- With only 1,000 training examples, DPR already outperforms BM25 on Natural Questions dev (self-reported).
- Distant supervision (a BM25 positive instead of the gold context) costs about 1 point (self-reported).
- L2 and triplet losses did not beat dot product with NLL on Natural Questions dev (self-reported).

## Results

- Measured at top-20, DPR leads BM25 by 9 to 19 absolute points on every dataset except SQuAD (range from the abstract) (self-reported). On SQuAD, BM25 wins; the authors attribute this to high lexical overlap between questions and passages and to a narrow set of articles.
- Training on several datasets greatly helps the smallest one (TREC) but hurts SQuAD, which is left out of that training (51.6 versus 63.2 for single-dataset) (self-reported).
- A linear combination BM25 + 1.1 x DPR helps on TREC and SQuAD (SQuAD 71.5 versus 63.2) and costs a little on Natural Questions (76.6 versus 78.4) (self-reported). Setup: single-dataset DPR.
- Per CPU thread, DPR serves roughly 42 times more queries per second than Lucene BM25 (in-memory FAISS HNSW against a file-based Java BM25, top 100 each). Building the index is far costlier: 8.8 hours of embedding on 8 GPUs and 8.5 hours of FAISS work, against about 30 minutes for Lucene (self-reported).
- Reading 10 passages instead of the optimal 50 costs under one exact-match point on Natural Questions (self-reported).

## Limits

- Retrieval is scored by whether the top-k text contains the answer string, not by relevance judgments.
- A qualitative appendix suggests the encoders may be unable to capture rare but salient phrases.
- Single runs, no seeds or variance; training hardware, warmup and weight decay not stated.
- Table 3 ablations use older hyper-parameters than the headline tables, which use better ones from the code release.
- The authors say it is unclear how much more inference time the reader needs compared with the earlier ORQA system.

## See Also
- [[RAG Retrieval Strategies]] — prerequisite-for
- [[ORQA and the Inverse Cloze Task]] — prerequisite-for
- [[Fusion-in-Decoder]] — extends (uses DPR passages for Natural Questions and TriviaQA)
- [[Reader-Attention Distillation for Retrievers]] — alternative-to (trains the retriever without question-passage labels)
- [[REALM Retrieval-Augmented Pre-Training]] — alternative-to
- [[BM25 and the Lexical Gap]] — prerequisite-for
- [[SimCSE Contrastive Sentence Embeddings]] — related
- [[Chain-of-Note]] — related
