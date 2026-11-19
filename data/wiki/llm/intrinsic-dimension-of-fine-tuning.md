---
title: Intrinsic Dimension of Fine-Tuning
tags: [llm, fine-tuning, concept]
summary: "Aghajanyan et al. fine-tune pretrained language models inside a small random subspace and find the smallest size reaching 90% of full accuracy (d90) falls during pretraining and with model size, about 200 parameters for RoBERTa-Large on MRPC (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-aghajanyan-2021-intrinsic-dimensionality-explains-effectiveness-language.md
---

# Intrinsic Dimension of Fine-Tuning

Aghajanyan, Gupta and Zettlemoyer (2021) ask why a model with hundreds of millions of parameters can be tuned with ordinary gradient descent on a few hundred or thousand labelled examples. They propose that pretraining implicitly shrinks the intrinsic dimension of the average NLP task, read as the task's minimal description length, and that a smaller one generalises better. Results are the authors' own (self-reported). The method comes from [[Intrinsic Dimension of Objective Landscapes]].

## Mechanism

Tuning happens in a d-dimensional subspace: pretrained weights plus a fixed random projection (Fastfood) of d trainable numbers. d90 is the smallest d that reaches 90% of full fine-tuning performance. DID uses the projection with no regard for layers; SAID, the structure-aware variant, spends some subspace parameters on per-layer scales. SAID beats DID in the BERT/RoBERTa comparison on MRPC and QQP, tying only for RoBERTa-Large on QQP.

## Results

- On MRPC, RoBERTa-Large gets to 90% of full fine-tuning with roughly 200 trainable parameters under SAID. A task could then be kept as those numbers plus a random seed, layered over the pretrained weights.
- A RoBERTa-Base pretrained anew for 200k updates (batch 1k) has SAID d90 shrinking steadily over 10k-update checkpoints, on MRPC, QQP, Yelp, SST-2, MNLI and ANLI. A few early checkpoints have no d90.
- Over 18 public models (families: T5, XLM-R, XLNet, Albert, Electra, BART, RoBERTa, BERT; several sizes each), MRPC d90 drops as parameters grow, across pretraining methods too. Inside a narrow size window, method counts: RoBERTa ahead of others near 1e8 parameters.
- Lower d90 goes with better evaluation accuracy and a smaller relative generalisation gap over RoBERTa checkpoints (plots only, no coefficients).
- A compression-based bound puts test loss within O(sqrt(d/m)) of training loss, independent of total parameter count D. It holds only for subspace-trained models.

## Limits

- d90 is a ceiling set by random projections; the authors suspect the real intrinsic dimension is far lower.
- The bound does not cover models trained normally, and the authors do not show that standard SGD works in this subspace.
- Holding pretraining fixed while varying size was infeasible, so the size trend blends methods.
- Only sentence classification is covered, with no model past T5-3B.
- Optimiser, batch size, steps, learning rates, seeds and variance go unreported, and no code is linked.
- The appendix said to hold per-dataset size trends contains only the proof; some Fig 2 points are missing; correlations appear in plots only.

## See Also
- [[Parameter-Efficient Fine-Tuning Methods]] — related (few trainable parameters; the paper cites adapters)
- [[Intrinsic Dimension of Objective Landscapes]] — prerequisite-for
- [[Bottleneck Adapters for Parameter-Efficient Transfer]] — related
- [[LoRA Low-Rank Adaptation]] — extends (applies the low-rank idea to weight updates)
