---
title: "Sentence-BERT Siamese Fine-Tuning"
tags: [data-science, nlp, pattern]
summary: "Sentence-BERT fine-tunes BERT or RoBERTa with pooling in a siamese network so sentence vectors can be compared by cosine similarity, avoiding the cross-encoder's pairwise cost at search time."
updated: 2026-11-20
sources:
  - data/raw/papers/2026-11-07-reimers-2019-sentence-bert.md
---

# Sentence-BERT Siamese Fine-Tuning

The question is whether siamese and triplet fine-tuning of BERT or RoBERTa can yield fixed-size vectors that cosine similarity can compare, so that the cross-encoder's quadratic pairing cost is not paid. The authors expect untuned BERT outputs (mean or CLS) to embed sentences poorly and NLI fine-tuning to fix that, so that similar sentences sit close together (their meaning of *semantically meaningful*).

## Method

A pooling layer sits on top of BERT or RoBERTa, and two tied-weight copies encode the two sentences. Objectives are classification, regression or triplet. The default is a 3-way softmax over SNLI plus MultiNLI for one epoch, on the concatenation (u, v, |u-v|). The triplet loss is max(||sa-sp|| - ||sa-sn|| + epsilon, 0). Once trained, the network is used only to produce embeddings, which are compared by cosine.

## Results (self-reported unless noted)

- Without STS training, averaged BERT outputs fall far under averaged GloVe in unsupervised STS with cosine (mean over 7 STS tasks, bert-base); the CLS vector is worse still.
- SBERT trained only on NLI was evaluated on the same 7 tasks, base and large, with RoBERTa giving only a minor difference. It improves on InferSent and the Universal Sentence Encoder (5.5 points over USE).
- Starting from NLI training before STSb gives SBERT roughly 1-2 extra points and the BERT cross-encoder roughly 3-4 (STSb test, 1,379 pairs). SBERT-NLI-STSb-large was run with 10 seeds, std 0.13.
- Ablation (SBERT-base on STSb dev, trained on SNLI plus MultiNLI, MEAN pooling, averaged over 10 seeds): (u, v, |u-v|) is the best concatenation, adding u*v does not help, and (u, v) alone is far worse. With the regression objective MAX pooling is much worse than MEAN, which contradicts MAX pooling in Conneau et al.'s InferSent.
- On the SentEval transfer tasks, where a logistic-regression classifier is fitted to frozen embeddings, averaged BERT embeddings score 84.94 yet do badly on cosine STS; the extraction attributes the difference to classifier against cosine.
- Wikipedia section triplets: trained with triplet loss for one epoch on about 1.8M triplets, tested on 222,957.
- Speed: finding the most similar pair among 10,000 sentences takes about 65 hours with the BERT cross-encoder and about 5 seconds with SBERT (V100). On CPU (i7-5820K) SBERT-base is slower than InferSent.

## Limits

- Cross-topic argument similarity (AFS): SBERT is about 7 Spearman points below BERT when trained on two topics and tested on a third; the authors suggest more than two training topics may be needed. With 10-fold CV on 6,000 pairs it is nearly on par.
- With both trained on STS, the base cross-encoder scores 88.33 on STSb against 85.35 for SBERT.
- By the authors' own account SBERT is not intended for transfer learning, for which fine-tuning BERT is the better route.
- On SICK-R and TREC, USE scores above SBERT.
- STSb and AFS fine-tuning hyperparameters are not given, nor are parameter counts; there are no significance tests, and an XLNet trial went unreported.

## See Also
- [[SimCSE Contrastive Sentence Embeddings]] — extends
- [[Frozen vs Fine-Tuned Sentence Encoders]] — related
- [[Sentence Embeddings as Features for Classical ML]] — related
- [[Tuning an Embedding Model from Match Labels]] — related
- [[Dense Passage Retrieval (DPR)]] — related (dual-encoder retrieval)
