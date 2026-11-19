---
title: Pointer Sentinel Mixture Models and WikiText
tags: [llm, architecture, concept]
summary: "Merity et al. mix a softmax vocabulary distribution with a pointer over the last 100 hidden states, gated by a sentinel element in the attention softmax, and release the WikiText-2 and WikiText-103 corpora."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-merity-2016-pointer-sentinel-mixture-models.md
---

# Pointer Sentinel Mixture Models and WikiText

Merity, Xiong, Bradbury et al. ask two things: whether blending an RNN softmax with a pointer into recent context, controlled by a sentinel, handles rare and unseen words better than an ordinary softmax LSTM, and what benchmark can probe long-range context. Their hypothesis is that the pointer can reproduce rare words and free up hidden-state capacity.

## Mechanism

- A pointer sentinel-LSTM adds pointer-sum attention across the last L = 100 hidden states. Under pointer-sum attention a word's probability is the total attention on every position where that word occurs.
- The sentinel is one extra element in the attention softmax. It closes off the pointer's search space and hands whatever probability mass is left to the RNN's vocabulary softmax. The output mixes the two distributions, g times the vocabulary one plus (1 - g) times the pointer one; the gate g is the sentinel's entry (index V+1) in a = softmax([z; q^T s]), and the pointer distribution is the other entries a[1:V] rescaled by 1 / (1 - g).
- The mixture adds H^2 + 2H parameters, against 8H^2 + 4H for one LSTM layer, at any depth because the pointer reads only the final layer.

## Results (all self-reported, single runs)

- Penn Treebank (Mikolov preprocessing, 10k vocabulary, two-layer medium LSTM, 650 hidden units, 21M parameters): test perplexity 70.9, the best in the paper's table. Gal's large variational LSTM using MC dropout (66M parameters) scores 73.4, so the pointer model uses about a third of its parameters. The RNN part alone (zoneout plus variational LSTM, 20M, BPTT L = 100) gets 80.6.
- WikiText-2 (same hyperparameters as the PTB best, 21M): 80.8 test perplexity.
- Gains grow as words get rarer (10 equal frequency buckets, PTB), shown in a figure and qualitative examples.

## WikiText corpora

- WikiText-2 holds 2,088,628 training tokens, a 33,278-word vocabulary and 2.6% out-of-vocabulary tokens. WikiText-103 holds about 103M training tokens with a 267,735-word vocabulary. For comparison, Penn Treebank has 929,590 training tokens, a 10,000-word vocabulary and 4.8% out-of-vocabulary tokens.
- According to the paper, WikiText-103 is roughly a hundred times the size of PTB and a tenth the size of the One Billion Word Benchmark. Other wiki pages report results on it, for instance [[Transformer-XL Segment Recurrence]] and [[Adaptive Input Representations]].

## Limits

- The pointer sentinel was run only at medium size and has no WikiText-103 results; on WikiText-2 the large Gal model exhausted the memory of a 12GB K80, so that setting has no large baseline.
- Every result is one run, without seeds or significance tests, and the optimiser and learning rate go unstated.
- The evidence for the rare-word benefit is a figure plus qualitative examples; the sentinel is not ablated against other gates in a controlled way.
- Table 2 flags some parameter counts with a double dagger; those are estimates. The results are LSTM-era and long superseded by Transformers.

## See Also

- [[Transformer-XL Segment Recurrence]] — related (evaluates on WikiText-103)
- [[Adaptive Input Representations]] — related (evaluates on WikiText-103)
- [[LSTMN Intra-Attention Memory Tape]] — related (another LSTM-era use of attention over past states)
- [[Pointer-Generator Network and Coverage]] — related (copy-or-generate mixture for summarisation)
