---
title: LSTMN Intra-Attention Memory Tape
tags: [llm, architecture, concept]
summary: "Cheng et al. replace the LSTM's single memory cell with a tape holding one slot per token, read by intra-attention at each step, so the state update is non-Markov; they test it on language modelling, sentiment and natural language inference."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-cheng-2016-long-short-term-memory-networks.md
---

# LSTMN Intra-Attention Memory Tape

Cheng, Dong and Lapata ask how a recurrent sequence network can handle structured input better by inducing latent relations among tokens and by memorising longer sequences. The LSTMN (Long Short-Term Memory-Network) keeps the contextual representation of each token in a separate memory-tape slot, uncompressed.

## Mechanism

- Hidden and memory tapes have one slot for each token processed. At every step an attention layer scores earlier hidden states, a_i^t = v^T tanh(W_x x_t + W_h h_i + W_h~ h~_{t-1}), and yields a weighted summary [h~_t; c~_t] of earlier hidden and memory vectors, which the LSTM update uses in place of h(t-1) and c(t-1).
- Intra-attention means attending over the network's own earlier hidden states; it serves for addressing memory and for inducing soft relations among tokens.
- On tasks with two sequences, shallow fusion makes both encoder and decoder LSTMNs joined by inter-attention. Deep fusion also writes the inter-attention vector into the target memory via a gate.

## Results (all self-reported)

- Penn Treebank test (memory size 300, embeddings 150): the three-layer LSTMN has the lowest perplexity among compared models, and a one-layer LSTMN does better than one-layer LSTM and RNN baselines.
- SNLI test: deep fusion (450 hidden units, 3.4M parameters) has the top accuracy in the table but far more parameters than the baselines. At hidden size 100 an LSTMN without fusion outdoes a plain LSTM (260k versus 221k parameters), and deep fusion edges out shallow fusion at all hidden sizes.
- Stanford Sentiment Treebank test (two layers, memory 168, GloVe 840B initialisation): the LSTMN beats LSTM baselines on the fine-grained 5-class task but trails T-CNN.
- Qualitatively (four PTB validation sentences), attention falls mostly on recent memories, in line with long-range dependencies being rare, and a few valid lexical relations show up.

## Limits

- Parameter count confounds the SNLI state-of-the-art claim; the authors advise caution and ran no parameter-matched comparison.
- The paper gives no seeds, variance or significance tests; compute, hardware, training time and epochs are also unreported.
- Memory is implemented for reading only, with writing deferred to future work.
- The relations that intra-attention induces are undirected and only weakly induced, with just qualitative evidence of structure.
- Attention is over all prior states and cost scaling is not discussed. The extraction notes it was superseded by the Transformer.

## See Also

- [[Self-Attention Mechanism]] — related (the Transformer, which the extraction says superseded it)
- [[Pointer Sentinel Mixture Models and WikiText]] — related (another LSTM-era use of attention over past states)
