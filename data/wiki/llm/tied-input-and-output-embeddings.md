---
title: "Tied Input and Output Embeddings"
tags: [llm, architecture, pattern]
summary: "Weight tying sets a language or translation model's input embedding and output (pre-softmax) embedding to one matrix; Press and Wolf (2017) report lower perplexity and far fewer parameters in LSTM language models and about half the size in NMT with similar BLEU."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-press-2017-using-output-embedding-improve-language.md
---

# Tied Input and Output Embeddings

A neural language model has an input embedding U and an output embedding V, the topmost weight matrix before the softmax. Press and Wolf ask whether V is a valid word embedding and whether tying it to U (weight tying, WT: U = V) helps. Their hypothesis: the shared matrix behaves like the output embedding and overfits less. The original Transformer shares the embedding and pre-softmax weights and cites this paper for it ([[Transformer Architecture]]).

## What they find

- Output vs input embedding quality (Simlex999): in word2vec skip-gram on text8 the output embedding is only slightly worse than the input, and the tied embedding is not competitive (0.17). In a small NNLM on PTB the input embedding is far worse than the output (tied 0.14).
- In the large NNLM, output and tied embeddings are highly correlated, and input and tied less, so the tied matrix evolves more like the output embedding.
- Tying the large LSTM LM on PTB (Zaremba large, with dropout) lowers test perplexity and cuts parameters from 66M to 51M; the tied model has higher training perplexity, i.e. less overfitting. A recurrent highway network with Bayesian dropout plus WT reports the best PTB test result (32M down to 24M parameters).
- Projection regularization (PR) inserts a matrix P before V, h3 = V P h2, with lambda ||P||² added to the loss (lambda = 0.15). For small models without dropout, WT plus PR was tried on PTB (4.65M to 2.69M parameters), text8, BBC and IMDB.
- NMT (DL4MT, attention model): decoder weight tying gives about 28% fewer parameters with similar BLEU. Three-way weight tying (TWWT) ties the decoder input embedding, decoder output embedding and encoder input embedding, giving about 52% fewer parameters with similar BLEU: 80M against 168M parameters on WMT14 EN-FR and 79M against 165M on WMT15 EN-DE. Up to 90% of BPE subwords between English and French (85% for German) are shared.

All results are self-reported.

## Limits

- Short paper with single runs and no seeds or significance tests; the NNLM hyperparameters are left to Zaremba et al. 2014; the models are LSTM and RHN era, on PTB-scale data (sizes not given).
- The authors argue weight tying is unsuitable for word2vec, where it lowers embedding quality, and projection regularization gives no gain for the large dropout models.
- The analysis assumes the input word differs from the target for simplicity.
- NMT tying does not improve BLEU, only equals it: EN-DE decoder WT test BLEU fell from 16.79 to 16.54 (119M parameters).

## See Also
- [[Transformer Architecture]] — prerequisite-for
- [[Neural Probabilistic Language Model]] — prerequisite-for
- [[Encoder-Decoder Translation Before the Transformer]] — related
