---
title: "Encoder-Decoder Translation Before the Transformer"
tags: [llm, architecture, concept]
summary: "The 2013-2017 line of neural translation models that the Transformer replaced: Kalchbrenner and Blunsom's convolutional-source recurrent decoder, Sutskever's reversed-source LSTM, Gehring's fully convolutional ConvS2S and Google's residual 8-layer GNMT with wordpieces."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-kalchbrenner-2013-recurrent-continuous-translation-models.md
  - data/raw/papers/2026-11-07-sutskever-2014-sequence-sequence-learning-neural-networks.md
  - data/raw/papers/2026-11-08-gehring-2017-convolutional-sequence-sequence-learning.md
  - data/raw/papers/2026-11-07-wu-2016-google-s-neural-machine-translation.md
---

# Encoder-Decoder Translation Before the Transformer

Four systems show how neural translation moved from rescoring phrase-based output to standalone encoder-decoder models. All four are evaluated on WMT data with BLEU unless noted; all numbers are the authors' reports on their own systems (self-reported).

## Recurrent Continuous Translation Models (Kalchbrenner and Blunsom, 2013)

A recurrent language model produces the French output one word at a time, conditioned on a continuous representation of the English source built by a convolutional sentence model. RCTM I adds one source vector to every hidden layer; RCTM II inverts a truncated 4-gram convolutional model to the target length, giving one vector per target position, with a Poisson length model. No alignments or phrase units are used.

- Trained on 144,953 news-commentary En-Fr pairs: RCTM II perplexity is more than 43% below alignment-based models and 40% below RCTM I (WMT-NT 2009-2012 test sets, q=256).
- Permuting the source words raises RCTM II perplexity on WMT-NT 2009 from 86 to 174, which the authors take as sensitivity to word order.
- It was used to rescore cdec 1000-best lists: 19.8 BLEU against 19.9 for cdec on WMT-NT 2009, and 21.7 against 21.8 on WMT-NT 2012. No standalone decoding BLEU is reported.

## Sutskever et al., 2014: deep LSTM with reversed source

Two 4-layer LSTMs: the encoder reads the source into a fixed vector and the decoder is a conditional LSTM language model, p(y|x) = prod_t p(y_t | v, y_<t). Decoding is left-to-right beam search. Training used 12M WMT'14 En-Fr pairs with an 80k target vocabulary; the network has 384M parameters and took about ten days on 8 GPUs.

- An ensemble of five reversed-source LSTMs decoded with beam 12 scores 34.81 BLEU on ntst14; rescoring the SMT 1000-best with it gives 36.5. The SMT baseline is 33.30.
- Reversing the source sentences (not the targets) took test BLEU from 25.9 up to 30.6 and test perplexity from 5.8 down to 4.7. The authors believe reversal shortens the minimal time lag between source words and their targets, without a full explanation.
- Perplexity fell by close to 10% with every added LSTM layer. Gradient norm is clipped to 5.
- Per a figure, the authors see no BLEU loss for sentences shorter than 35 words and a small loss for the longest.

## ConvS2S (Gehring et al., 2017)

Both encoder and decoder stack one-dimensional convolution blocks using gated linear units (see [[GLU Variants and GELU]]) and residual connections. Inputs are word plus absolute position embeddings, and every decoder layer has its own dot-product attention over the encoder output (multi-step attention). Scaling by sqrt(0.5) and a matching initialisation preserve variance.

- Margins reported: +1.9 BLEU over the winning WMT'16 En-Ro entry (BPE 40K, 20+20 layers); +0.5 over GNMT's wordpiece LSTM on En-De (15+15 layers); +1.6 on average over the likelihood-trained GNMT on En-Fr.
- Generation on WMT'14 En-Fr dev: 9.3 times faster on a K40 than GNMT on a K80, with 2.25 higher BLEU; 17 times faster per CPU core. These compare against GNMT figures quoted from Wu et al. on other hardware.
- Ablations on En-De: removing both position embeddings costs only 0.5 BLEU; attention in all five decoder layers gives the best validation perplexity and costs about 4% more training time than one attention layer; kernel width 3 with 13 encoder layers gave the best BLEU.

## GNMT (Wu et al., 2016)

An 8-layer encoder (one bidirectional layer) and 8-layer decoder LSTM with residual connections and attention from the bottom decoder layer to the top encoder layer. Wordpiece segmentation (shared 8K-32K vocabulary) handles rare words; beam search ranks candidates with a score that divides the log-probability by a length term lp(Y) and adds a coverage term cp(X;Y); inference runs quantised on TPU.

- A single WPM-32K model averages 38.95 BLEU over 8 trained models on WMT En->Fr newstest2014 (best one 39.37); a word model scores 37.90 and a character model 38.01. En->De: 24.61 for wordpiece against 23.12 for the word model.
- Adding the length and coverage terms (alpha=0.2, beta=0.2) lifts En->Fr dev-set BLEU by 1.1, 30.3 to 31.4.
- Refining with RL on a GLEU reward raises the En->Fr single-model average to 39.92 from 38.95 and an 8-model ensemble from 40.35 to 41.16, but human side-by-side scores did not move (4.46 before, 4.44 after; PBMT 3.87, human translation 4.82; 500 sentences).
- Human evaluation on production data shows more than 60% fewer translation errors than the phrase-based system (500 sentences per language pair, single models).
- Quantised decoding on a TPU runs 3.4 times faster than on CPU at the same BLEU (31.21 against 31.20, En->Fr dev set).
- Without residual connections, stacked LSTMs are fine to 4 layers, marginal at 6 and bad past 8 (anecdotal, no table). Adam for 60k steps then SGD converged better than either alone.

## Limits

- Kalchbrenner and Blunsom: a small experiment (145k pairs); BLEU differences from cdec are small with no significance tests; hyperparameters not stated; no alignment or attention mechanism. Sutskever: fixed 80k target vocabulary and a fixed-size sentence vector; the plain LSTM ensemble stays below the top WMT'14 system (37.0); the authors have no complete explanation for reversal and did not verify that a standard RNN would train on reversed sources; single test set; training times are for 2014 hardware.
- ConvS2S: the speed comparison takes GNMT's figures from Wu et al., who used other hardware (K80, 88-core CPU, TPU), so CPU speeds do not compare directly; training is costly (En-De took 18.5 days on one GPU; En-Fr about 37 days on eight); the En-Fr model's effective context is only 25 words and the position embeddings impose a maximum sentence length; dropout rate, epochs and parameter counts are not stated; best single runs of a mixture-of-experts LSTM exceed its best runs on En-De.
- GNMT: RL gains in BLEU did not show in human scores (the authors suspect the small sample and a BLEU/quality mismatch); RL slightly lowered En->De BLEU (24.67 to 24.60); the production evaluation uses simple isolated sentences; human translations themselves reach only about 5 of 6; hyperparameters are not fully listed and the parameter count, code and weights are not given.
- The 60% error reduction is stated for isolated simple sentences in the abstract.
- These models were later replaced by the Transformer ([[Transformer Architecture]]); the extraction for ConvS2S marks that as inferred.

## See Also
- [[Attention for Neural Machine Translation (Bahdanau, Luong, Decomposable)]] — related (the attention these systems build on)
- [[Transformer Architecture]] — extends
- [[Back-Translation at Scale]] — extends
- [[Seq2seq Bottleneck and Attention]] — prerequisite-for
- [[Sequence-Level Knowledge Distillation]] — related (distilling translation models)
- [[XSum Extreme Summarisation]] — related (T-ConvS2S extends ConvS2S)
