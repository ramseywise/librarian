---
title: Contriever Unsupervised Contrastive Retrieval
tags: [rag, concept]
summary: Contriever trains a BERT-base bi-encoder with no labels by contrasting two random crops of one document with a MoCo queue of negatives, then serves as pre-training for supervised, few-shot and multilingual retrieval.
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-izacard-2021-unsupervised-dense-information-retrieval-contrastive.md
---

# Contriever Unsupervised Contrastive Retrieval

Contriever (Izacard et al.) asks whether a dense retriever can be trained with no supervision and still match BM25, and whether that makes a useful starting point for later fine-tuning.

## Mechanism

The model is a BERT-base bi-encoder with shared weights, scoring by dot product over mean-pooled last-layer outputs, and it is trained with an InfoNCE loss. Positive pairs are two independently cropped spans of the same document; negatives come from a MoCo momentum-encoder queue. The paper also trains mContriever on 29 languages.

## Results

All figures are self-reported.
- Unsupervised (Wikipedia plus CCNet, no labelled data), BEIR: beats BM25 on 11 of 15 datasets at Recall@100, yet average Recall@100 and average nDCG@10 stay below BM25. The authors tie the gap to Trec-COVID and Touche-2020.
- Unsupervised Natural Questions Recall@100: 82.1 against 78.3 for BM25; TriviaQA ties BM25.
- After MS MARCO fine-tuning (in-batch negatives, hard negatives 10% of the time): best average BEIR nDCG@10 among the dense bi-encoders in the comparison table; sparse Splade v2 (50.6) is higher. The highest average nDCG@10 in that table comes from adding a cross-encoder re-ranker over the top 100.
- Few-shot, no MS MARCO: beats BM25 on SciFact (729 training queries) and by 12.8 points on FiQA (5,500 queries).
- Ablations (200k steps, English Wikipedia, batch 2,048): random cropping beats the inverse Cloze task; MoCo and in-batch negatives differ little; CCNet alone scores best. The same MS MARCO fine-tune on plain BERT scores lower, so the extraction reads the gain as coming from pre-training.
- Multilingual: unsupervised mContriever beats BM25 on Mr. TyDi Recall@100 but trails on MRR@100; with English MS MARCO fine-tuning it reaches the best Mr. TyDi Recall@100 reported and beats CORA on cross-lingual MKQA. A model pre-trained on just the 11 Mr. TyDi languages does better than one trained on all 29.

## Limits

- Unsupervised, it loses to BM25 on average nDCG@10 and on Trec-COVID and Touche-2020; dense retrievers handle long documents poorly by the authors' account.
- Fine-tuning is simple (no distillation, simple negative mining), so the authors expect headroom.
- No seeds, variance or significance tests; parameter count, compute and wall clock are not stated.
- More pre-training languages degraded results.

## See Also
- [[RAG Retrieval Strategies]] — prerequisite-for
- [[HyDE Hypothetical Document Embeddings]] — extends (uses Contriever as its encoder)
- [[Atlas Retrieval-Augmented Few-Shot Learning]] — extends (initialises its retriever from Contriever)
- [[ANCE Global Hard Negatives for Dense Retrieval]] — alternative-to (labelled training with hard negatives instead of unsupervised crops)
- [[GTR Large Dual Encoders]] — alternative-to (scale plus 2B QA-pair pre-training instead of unsupervised crops)
