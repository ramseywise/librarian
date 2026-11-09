---
title: SimCSE Contrastive Sentence Embeddings
tags: [foundations, pattern]
summary: "SimCSE fine-tunes BERT or RoBERTa with an in-batch contrastive loss, using two dropout masks of the same sentence as the unsupervised positive pair and NLI entailment/contradiction pairs when labels exist."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-gao-2021-simcse.md
---

# SimCSE Contrastive Sentence Embeddings

SimCSE updates every parameter of a pre-trained BERT or RoBERTa using a cross-entropy loss over in-batch negatives, with temperature-scaled cosine similarity. In the **unsupervised** form, a sentence is run through the encoder twice under different dropout masks and the two outputs form the positive pair; dropout is the only augmentation. In the **supervised** form NLI entailment pairs are positives and contradiction hypotheses are hard negatives. The authors tie the gains to **alignment** (distance between positive pairs) and **uniformity** (spread over the hypersphere): pre-trained embeddings are well aligned but **anisotropic**, occupying a narrow cone.

## Results

All numbers are self-reported unless noted; STS is averaged over 7 tasks with Spearman correlation.

- Unsupervised SimCSE-BERTbase (1M Wikipedia sentences) averages 76.25, against 72.05 for the earlier best, CT-BERT. Supervised SimCSE-BERTbase (SNLI+MNLI) averages 81.57; supervised SimCSE-RoBERTalarge 83.76. Supervised SBERTbase, taken from its paper, averages 74.89.
- Raw BERTbase first-last average embeddings score 56.70, below averaged GloVe (61.32).
- STS-B dev ablations (BERTbase, unsupervised): removing dropout cuts 82.5 to 71.1, and using the same dropout mask on both sides gives 43.6. It beats a next-sentence objective (67.4) and deleting one word (75.9). Dropout 0.1 is best; 0.5 gives 71.0.
- Supervised, STS-B dev: NLI entailment positives give 84.9 versus QQP 81.8, Flickr30k 81.4 and ParaNMT 78.7. Lexical overlap is 39% for NLI pairs, 60% for QQP and 55% for ParaNMT. Contradiction hard negatives lift 84.9 to 86.2; neutral hypotheses add nothing (85.3). A dual-encoder variant hurts (84.2).
- With temperature tau=0.05 the score is 86.2, with tau=1 it is 64.0, and a plain dot product gives 85.9.
- Flow and whitening post-processing improve uniformity at the expense of alignment, whereas SimCSE improves uniformity and keeps alignment. Across batch sizes 64-512, results were insensitive once the learning rate was tuned.
- The paper reports that published STS evaluations use inconsistent protocols; SBERT's average is 74.85 under one aggregation and 73.55 under another.

## Limits

- Evaluation rests mainly on STS and SentEval, with no retrieval benchmark (BEIR, passage retrieval) beyond one qualitative Flickr30k caption example. STS gains need not transfer: flow and whitening hurt transfer tasks.
- Ablations use STS-B dev, which also selects checkpoints and hyperparameters.
- The extraction notes single runs, English only, and sentences rather than queries against passages.
- Hardware, compute, optimizer, schedule and maximum sequence length not stated.
- The anisotropy argument is asymptotic in the number of negatives and assumes positive similarities.

## See Also
- [[Contrastive Self-Supervised Pretraining]] — prerequisite-for
- [[Frozen vs Fine-Tuned Sentence Encoders]] — related
- [[Tuning an Embedding Model from Match Labels]] — related
- [[Dense Passage Retrieval (DPR)]] — related (contrastive dual encoder with supervised pairs)
