---
title: Pointer-Generator Network and Coverage
tags: [llm, architecture, pattern]
summary: "See et al.'s summariser mixes a vocabulary distribution with the attention distribution through a learned switch p_gen so it can copy source words, and adds a coverage vector with a coverage loss to stop repetition; on CNN/Daily Mail it reaches ROUGE-1 39.53 but stays below the lead-3 baseline."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-see-2017-get-point.md
  - data/raw/papers/2026-11-07-nallapati-2016-abstractive-text-summarization-using-sequence.md
---

# Pointer-Generator Network and Coverage

See, Liu and Manning (ACL 2017) ask whether an attentional sequence-to-sequence summariser can get facts right, cope with out-of-vocabulary words and avoid repeating itself when writing multi-sentence news summaries. They hypothesise that copying by pointing improves factual accuracy and out-of-vocabulary handling, and that a coverage vector removes repetition.

## Mechanism

The baseline is a single-layer bidirectional LSTM encoder and an LSTM decoder with Bahdanau attention.

- **Pointer-generator.** A soft switch p_gen in [0, 1], computed from the context vector, decoder state and decoder input, weights generating from the vocabulary against copying from the source. The final distribution runs over an extended vocabulary: the probability of word w is p_gen times its vocabulary probability plus (1 - p_gen) times the attention summed over source positions holding w.
- **Coverage.** The coverage vector accumulates the attention given to each source position at all earlier decoder steps. A coverage loss, lambda times the sum over source positions of min(attention, coverage), joins the negative log-likelihood. It is switched on only for a brief last phase of training (lambda = 1) of 3,000 iterations, about 2 hours or 1% of the whole training time.
- The extra parameters are tiny: 1,153 for the pointer and 512 for coverage, on a 21,499,600-parameter baseline.

## Results (self-reported)

Setup: CNN/Daily Mail non-anonymised test set (11,490 pairs), 256-dimensional LSTM, 50k vocabulary, beam 4.

- Pointer-generator with coverage: ROUGE-1 39.53; without coverage 36.44; the 50k-vocabulary sequence-to-sequence baseline 31.33. Coverage adds about 3 ROUGE-1 points (derived).
- Even the best model stays under lead-3, whose ROUGE-1 is 40.34 on the same data.
- The authors estimate a margin of at least 2 ROUGE points over the previous abstractive system after correcting for anonymised against original text (not strictly comparable).
- Whole article sentences are copied by the final model in 35% of cases, against 1.3% for reference summaries.
- Mean p_gen rises from about 0.30 early in training to about 0.53, but is only about 0.17 at test time, when the model mostly copies.
- It also trains faster, in under 230,000 iterations (12.8 epochs) where the baseline needs about 600,000 (33 epochs), on one Tesla K40m at batch size 16.
- Cutting articles to their first 400 tokens scored significantly higher ROUGE than keeping 800.
- Qualitatively, the baseline fabricates facts, replaces rare words with common ones and emits UNK; the pointer-generator copies facts almost always correctly (Figure 1 example only).
- Coverage with no coverage loss visibly did nothing for repetition, and turning coverage on from the first iteration got in the way of the main objective (text only, no numbers).

## Earlier switching pointer (Nallapati et al., 2016)

[[Neural Abstractive Summarisation 2015-2017]] describes Nallapati's switching generator-pointer: a switch probability P(s_i = 1) from a sigmoid over the decoder state, the previous output embedding and the context, deciding whether to generate or point to a source position for rare words. Its overall improvement was not significant, and on CNN/Daily Mail it did not beat the plain attentional baseline (words-lvt2k-ptr 32.12 ROUGE F1).

## Limits

- The ROUGE comparison with Nallapati et al. uses a different (anonymised) data version.
- On ROUGE the best model loses to lead-3 and to the best extractive model, and it is far less abstractive than the references.
- Scoring is ROUGE and METEOR alone, with no human check of factuality, so the accuracy claims rest on qualitative examples.
- One run, no seeds; compute for coverage and the ablations is given only in prose; the supplementary examples are not in the PDF.
- Dated: LSTM sequence-to-sequence with 2017 baselines.

## See Also
- [[Attention for Neural Machine Translation (Bahdanau, Luong, Decomposable)]] — prerequisite-for
- [[Neural Abstractive Summarisation 2015-2017]] — prerequisite-for
- [[Pointer Sentinel Mixture Models and WikiText]] — related (another copy-or-generate mixture)
- [[XSum Extreme Summarisation]] — related (the pointer-generator copies far less when trained there)
