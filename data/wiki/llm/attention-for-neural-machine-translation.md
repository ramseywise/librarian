---
title: "Attention for Neural Machine Translation (Bahdanau, Luong, Decomposable)"
tags: [llm, architecture, concept]
summary: "How soft attention entered encoder-decoder translation: Bahdanau's additive alignment over bidirectional annotations, Luong's global and local variants with input feeding, and Parikh's attend-compare-aggregate model that uses attention without a recurrent encoder."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-bahdanau-2014-neural-machine-translation-jointly-learning.md
  - data/raw/papers/2026-11-08-luong-2015-effective-approaches-attention-based-neural.md
  - data/raw/papers/2026-11-08-parikh-2016-decomposable-attention-model-natural-language.md
---

# Attention for Neural Machine Translation (Bahdanau, Luong, Decomposable)

In a plain encoder-decoder the source sentence is compressed into one fixed-length vector (see [[Seq2seq Bottleneck and Attention]] and [[Encoder-Decoder Translation Before the Transformer]]). Bahdanau et al. hypothesised that this single vector limits translation, long sentences above all, and had the decoder soft-search the source for every target word instead.

## Bahdanau: additive alignment (RNNsearch)

- A bidirectional gated-RNN encoder produces an annotation h_j for each source word: the concatenation of its forward and backward states.
- At decoder step i, a small feed-forward alignment network rates every annotation against the preceding decoder state: the score e_ij is v_a transposed times tanh of (W_a s_{i-1} plus U_a h_j). Softmax over j yields weights alpha_ij, and the context vector c_i is their weighted sum of the annotations. The whole system is trained jointly.
- On the WMT'14 En-Fr test set news-test-2014 (self-reported), all sentences: RNNsearch-50 gets 26.75 BLEU where the RNNencdec-50 baseline gets 17.82; RNNsearch-30 gets 21.50 against 13.93 and also beats RNNencdec-50. RNNsearch-50 trained longer reaches 28.45.
- Moses scores 33.30 on all sentences, above every neural model; restricted to sentences with no unknown words, RNNsearch-50* gets 36.15 and Moses 35.63.
- Unlike RNNencdec, RNNsearch-50 holds up for sentences of 50 words and longer (read off a figure).

## Luong: global, local and input feeding

Luong et al. stack an LSTM encoder-decoder with an attention layer and compare designs. Hypothesis: a window over the source can cost less than attending to every word while matching or beating it.

- **Global attention** uses all source states for the context vector c_t, a simplification of Bahdanau's. **Local attention** covers source positions from p_t − D to p_t + D and blends hard and soft attention (variants local-m and local-p).
- The attentional vector combines context and state: h~_t is tanh of W_c applied to the concatenation of c_t and h_t. Scores tried: dot, general (h_t^T W_a hbar_s), concat, and a location-based one. Dot worked best for global and general best for local.
- **Input feeding** concatenates the attentional vector with the inputs at the next step.
- WMT'14 English-German, newstest2014, tokenised BLEU, 4-layer 1000-cell LSTM (self-reported): global (location) attention adds 2.8 BLEU over the baseline with source reversal and dropout; input feeding adds 1.3; unknown-word replacement adds 1.9; local-p with input feeding gains 5.0 over the non-attentional baseline. An 8-model ensemble with unknown-word replacement is reported as state of the art for English-German on both WMT'14 and WMT'15.
- German-English best single system did not match the phrase-based state of the art (29.2) on WMT'15.

## Decomposable attention (Parikh et al.)

For natural language inference the authors hypothesise that aligning local pieces of text and aggregating can suffice. The model has three steps: **Attend** soft-aligns premise and hypothesis words with e_ij = F(a_i)^T F(b_j) using a feed-forward F; **Compare** passes each word with its aligned phrase through a feed-forward network G; **Aggregate** sums the comparison vectors and a classifier H predicts the label. It is parallelisable and uses no word order. An optional intra-sentence attention with a distance-sensitive bias adds minimal order information.

- SNLI test, 3-class accuracy, single model (self-reported): 86.8% with intra-sentence attention (582K parameters), 0.5 points above the previous best; the vanilla model matches the previous best with 382K parameters (excluding embeddings) against 3.4M for LSTMN.

## Limits

- Bahdanau: unknown and rare words are left open and on all sentences the best model (28.45) trails Moses (33.30). Moses used an extra 418M-word monolingual corpus, so the comparison is not like for like. The baseline is the 1000-unit RNNencdec of Cho et al., not the larger Sutskever LSTM. Attention scores every source word for every target word, which the authors say may limit use beyond translation (sentences of 15-40 words). Single runs; beam width not given.
- Luong: the concat alignment function underperformed and the authors say it needs more analysis. Not all architecture and alignment combinations were run. AER and BLEU are not well correlated. Three settings go unstated (window size D, dropout rate, beam width), and runs are single, without seeds.
- Parikh: only SNLI is evaluated. The model cannot use word order and fails on examples that need sequence information or numbers; embeddings are too coarse for some contradictions. Its complexity analysis assumes sentence length below the embedding dimension. Single runs.
- The three papers use different data, models and metrics, so their BLEU figures are not comparable with each other.

## See Also
- [[Seq2seq Bottleneck and Attention]] — prerequisite-for
- [[Self-Attention Mechanism]] — extends
- [[Transformer Architecture]] — extends
- [[Encoder-Decoder Translation Before the Transformer]] — prerequisite-for
- [[Neural Abstractive Summarisation 2015-2017]] — related (attention applied to summarisation)
- [[Diverse Beam Search]] — related (decoding for an attention translation model)
