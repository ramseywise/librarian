---
title: GTR Large Dual Encoders
tags: [rag, concept]
summary: GTR scales a T5 dual encoder to 4.8B parameters while keeping a fixed 768-d embedding, and reports that zero-shot BEIR retrieval improves with encoder size rather than being capped by the dot-product bottleneck.
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-ni-2022-large-dual-encoders-generalizable-retrievers.md
---

# GTR Large Dual Encoders

GTR (Ni et al., EMNLP 2022) tests the belief that a fixed-size dot-product bottleneck caps dual encoders. It holds the embedding at 768 dimensions and scales only the encoder.

## Mechanism

The dual encoders are built on the T5 encoder in sizes from Base to XXL (110M to 4.8B parameters) with mean pooling and cosine similarity. Training has two stages: pre-training on 2B community QA pairs, then fine-tuning with hard negatives, using either MS Marco or NQ (RocketQA negatives for MS Marco).

## Results

Self-reported, BEIR zero-shot over 18 datasets with MS Marco excluded from the average, unless noted.
- Scaling from Base up to XXL moves average NDCG@10 from a level under BM25 to one over it; Recall@100 follows the same trend.
- For a pre-trained GTR-XXL, fine-tuning on only 10% of MS Marco does at least as well zero-shot as fine-tuning on everything, although in-domain results fall. Without pre-training the XXL model trails full GTR, and pre-training alone is far behind.
- Raising the bottleneck from 768 to 4096 gives minimal gain, while model size helps consistently (fine-tuned on MS Marco only, six out-of-domain datasets, values read from a figure).
- Latency at batch size 1 and input length 128 rises from 17 ms (Base) to 34 (Large), 96 (XL) and 349 ms (XXL).
- NQ fine-tuning scores under MS Marco fine-tuning, with the gap shrinking as models grow; GTR-Base tuned on NQ outperforms DPR.

## Limits

- XXL still loses to BM25 on five BEIR tasks, including Trec-Covid, BioASQ, Signal-1M, Trec-News and Touche.
- No distillation study; English only; the community QA data is not released; no seeds or variance.
- The bottleneck ablation skips pre-training and covers 6 datasets; the comparison against the Izacard et al. model uses 15 datasets.

## See Also
- [[RAG Retrieval Strategies]] — prerequisite-for
- [[Contriever Unsupervised Contrastive Retrieval]] — alternative-to (concurrent pre-training approach)
- [[HyDE Hypothetical Document Embeddings]] — related (HyDE was also run on GTR-XL)
- [[ModernBERT Encoder Backbone]] — related (a newer encoder backbone evaluated on BEIR)
- [[INSTRUCTOR Instruction-Finetuned Embeddings]] — extends
