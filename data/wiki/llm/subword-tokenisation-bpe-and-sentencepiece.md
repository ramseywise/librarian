---
title: "Subword Tokenisation: BPE and SentencePiece"
tags: [llm, pretraining-and-data, concept]
summary: "BPE learns a fixed vocabulary of variable-length character sequences by repeated merges so an NMT model needs no back-off dictionary; SentencePiece trains BPE or a unigram LM directly from raw text and makes tokenisation lossless."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-sennrich-2016-neural-machine-translation-rare-words.md
  - data/raw/papers/2026-11-07-kudo-2018-sentencepiece.md
---

# Subword Tokenisation: BPE and SentencePiece

## BPE for open-vocabulary translation (Sennrich, Haddow and Birch, 2016)

Sennrich et al. ask which segmentation of rare words lets an NMT model handle unseen words with no back-off dictionary. They hypothesise that splitting rare words into suitable subword pieces is enough for the network to translate them transparently, including words never seen in training.

Byte pair encoding (BPE), adapted from a data-compression algorithm, starts from characters and works over the word-frequency dictionary: count adjacent symbol pairs, merge the most frequent pair, repeat (Algorithm 1). The number of merges is the only hyperparameter. **Joint BPE** learns the encoding on the union of source and target vocabularies, in practice by concatenating both sides of the training set. The models are attention-based GRU encoder-decoders (Groundhog) trained on WMT15 English-German and English-Russian.

Reported results (self-reported, newstest2015, ensembles of 8):

- English-German BLEU, best to worst: character-bigram system C2-50k 25.3; then joint BPE with a 90k vocabulary (J90k) at 24.7, and BPE-60k at 24.5; the back-off dictionary baseline WDict 24.2; WUnk 22.8. The abstract's "up to 1.1 BLEU" on English-German comes from C2-50k, not BPE.
- English-Russian: J90k improves on WDict by 1.3 BLEU and 2.0 CHRF3.
- Unigram F1 on rare words: English-German goes 36.8% (WDict) to 41.8% (J90k); English-Russian goes 26.5% to 29.7%.
- German side of the training data (about 100m tokens): BPE with 59 500 merges gives 112m tokens, 63 000 types and 0 UNK on newstest2013, against 1 750 000 types unsegmented; joint BPE (89 500 operations) gives 111m tokens, 82 000 types and 32 UNK; single characters need 550m tokens over 3000 types, and character bigrams 306m tokens over 20 000 types.
- Of 100 rare German training tokens inspected (outside the 50 000 most frequent types), 56 were compounds and 21 were names.
- In the rank-by-frequency F1 plot (Fig 2), the C2-3/500k system declines for words ranked 50 000 to 500 000 and C2-50k does not; the authors read this as support for a smaller vocabulary with more words built from subwords.

## SentencePiece (Kudo and Richardson, 2018)

The question is whether a subword tokenizer and detokenizer can train directly from raw sentences, be lossless and language independent, and still match pre-tokenised subword quality. The library (C++, Python, TensorFlow) implements BPE and a unigram LM, with Normalizer, Trainer, Encoder and Decoder components.

- **Lossless tokenisation:** `Decode(Encode(Normalize(text))) = Normalize(text)`; whitespace is escaped as a meta symbol, so detokenising is `''.join(tokens).replace('_', ' ')`.
- Vocabulary size is specified at training time; Unicode normalisation (default NFKC) is compiled into a self-contained model file; an on-the-fly API enables subword regularisation.
- The SentencePiece paper claims (self-reported) that straightforward BPE segmentation costs O(N^2) in input length N, whereas its binary-heap algorithm costs O(N log N).
- KFTT English-Japanese, GNMT 6x512 LSTM: SentencePiece unigram with an 8k shared vocabulary beat the 80k/80k word model (Moses and KyTea tokenisers) in both directions (self-reported). Pre-tokenisation gave a marginal, non-significant gain on ja-en and hurt on en-ja.
- Speed on raw Japanese (KFTT, 440k sentences, vocabulary 16k, no pre-tokenisation): segmentation 5.9 s against 216.2 s for subword-nmt, about 380 times faster; training 217.3 s against 528.0 s (self-reported). BPE and unigram LM are comparable in speed.

## Limits

- Sennrich et al.: the vocabulary size is "somewhat arbitrary", chosen mainly for comparison with prior work; the optimal size is left open. The single-system figures are the best of 8 on dev, models differ by up to 1 BLEU, and no significance tests are run. The two metrics disagree on the top English-German system: BLEU picks C2-50k, CHRF3 picks J90k. BPE-60k suffers from inconsistent source and target segmentation.
- Only two language pairs and one pre-Transformer architecture; rare and out-of-vocabulary words are just 9 to 11% of the test sets, which could mean BLEU undersells the effect. No dropout was used.
- Kudo and Richardson: one language pair and one small corpus, no seeds or variance; training settings beyond layer and node counts are deferred to GNMT; the word model uses an 80k vocabulary against 8k, so vocabulary size is confounded with segmentation method. Only a subset of NFKC is implemented, and speed numbers are for 2018 Xeon hardware.

## See Also
- [[Back-Translation with Monolingual Data]] — related (uses BPE with 89 500 merges)
- [[Neural Probabilistic Language Model]] — related
