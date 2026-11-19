---
title: Neural Abstractive Summarisation 2015-2017
tags: [llm, architecture, comparison]
summary: "Three early neural summarisers compared by mechanism and setup: Rush's attention-based headline model (ABS) on Gigaword, Nallapati's feature-rich, switching-pointer and hierarchical-attention RNNs plus the CNN/Daily Mail set, and Paulus's intra-attention model trained with a mixed maximum-likelihood and self-critical RL loss."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-rush-2015-neural-attention-model-abstractive-sentence.md
  - data/raw/papers/2026-11-07-nallapati-2016-abstractive-text-summarization-using-sequence.md
  - data/raw/papers/2026-11-08-paulus-2017-deep-reinforced-model-abstractive-summarization.md
---

# Neural Abstractive Summarisation 2015-2017

All numbers below are the papers' own and use different setups, so rows are not comparable across papers.

## Rush et al. 2015: the ABS model

The task is a single-sentence headline from an article's first sentence. A feed-forward neural language model (context C = 5) is conditioned on an encoder, which is bag-of-words, convolutional or attention-based, and predicts each summary word. It is trained with minibatch SGD on the negative log-likelihood of about 4 million Gigaword headline-sentence pairs; training took about four days over 15 epochs on a GPU (D = 200, H = 400). Decoding uses beam search. **ABS+** adds five log-linear features (matches of one to three words, and reordering), with weights tuned by MERT.

- ABS+ has the best ROUGE-1 on DUC-2004 (4 references, 75 bytes) above TOPIARY and MOSES+, and on the Gigaword held-out test set.
- Of the encoders, the attention one reaches the lowest validation perplexity, and beam search outperforms greedy decoding on DUC-2003 development data.
- A pure extractive PREFIX baseline (first 75 characters) is strong on DUC-2004 ROUGE-1.
- Limits: the authors say the model remains far from human performance and sometimes reorders words ungrammatically. The output length is fixed in advance. Only ROUGE is reported, and it rewards the extractive features ABS+ uses. Beam size, GPU type and seeds are not stated.

## Nallapati et al. 2016: seq2seq RNNs and beyond

The base model pairs a bidirectional GRU encoder with a GRU decoder that has attention and the **large vocabulary trick**: each mini-batch's decoder vocabulary is limited to words in that batch's source documents, plus the most frequent target words up to a fixed size. Variants add embeddings of TF, IDF, POS and NER features, a generator-pointer switch for out-of-vocabulary words (see [[Pointer-Generator Network and Coverage]]), and word plus sentence hierarchical attention. The paper also proposes CNN/Daily Mail as a multi-sentence summarisation dataset.

- Gigaword internal test set (about 3.8M training examples, beam 5, full-length F1): the best model reaches ROUGE-1 36.40 against 34.97 for the one-sentence baseline.
- On Rush et al.'s test sample the baseline beats ABS+ in full-length ROUGE-1 F1, and copies far less from the source than ABS+. On DUC-2004 the untuned Gigaword-trained model beats ABS+ in ROUGE-2 recall, but the difference is not statistically significant.
- Among the CNN/Daily Mail results the plain attentional baseline comes out on top, ahead of the pointer model (32.12) and hierarchical attention (31.78).
- The authors switched from full-length recall to full-length F1 because recall favours longer summaries, and observe that a summary can be relevant and meaningful while differing from the target, something ROUGE misses.
- Training took 6 to 8 days on one K40 for Gigaword and nearly 18 days for hierarchical attention on CNN/Daily Mail.
- Limits: the best models could not be tested on Rush's sample, which has one source sentence and no annotations. Generated CNN/Daily Mail summaries often repeat a sentence or phrase, and results are called preliminary. Significance is reported only for the best models; single runs. Concurrent work by Chopra et al. reports slightly better Gigaword numbers.

## Paulus et al. 2017: intra-attention and mixed RL

A bidirectional LSTM encoder and a single LSTM decoder use intra-temporal attention over the encoder, intra-decoder attention over earlier output, a copy/generate switch and shared embedding and output weights. Training begins with maximum likelihood (teacher forcing, with the model's own token fed 25% of the time), then starts from the best such model and fine-tunes with a **self-critical** policy gradient, where the greedy output's reward is the baseline for the sampled sequence, so no critic network is needed. The loss is L_mixed = gamma L_rl + (1 - gamma) L_ml, with reward ROUGE-L; rewarding ROUGE-2 gave summaries that almost invariably ran to the length cap and finished mid-sentence. Beam search blocks repeated trigrams at test time, motivated by ground-truth summaries almost never repeating a trigram.

- CNN/Daily Mail (11,490 test articles, full-length ROUGE F-1, beam 5): the RL-only model has the top ROUGE-1 (41.16 in the abstract) but the lowest readability, while the mixed model scores 39.87 and reads best, in a study of 100 test examples with 5 raters each.
- On NYT, intra-attention does not help (shorter summaries), and RL without intra-attention beats maximum likelihood on ROUGE-1.
- Limits: small LSTMs with no parameter counts, compute, steps or seeds; trigram blocking and gamma (0.9984, given without a sweep) are not ablated. The comparison with See et al. is indirect, since preprocessing differs. The human study has no agreement score or significance test, and the RL example ends in degenerate fragments, which suggests metric gaming.

## Limits

- Every row is a single-run, self-reported result on a different dataset, split or ROUGE variant; none of the three papers compares like for like with the others, apart from the CNN/Daily Mail figures, which differ in preprocessing.
- Rush's model is described as superseded by later RNN and Transformer seq2seq systems.

## See Also
- [[Attention for Neural Machine Translation (Bahdanau, Luong, Decomposable)]] — prerequisite-for
- [[MIXER Sequence-Level Training and Exposure Bias]] — prerequisite-for (origin of REINFORCE for sequences and the exposure-bias term)
- [[Pointer-Generator Network and Coverage]] — extends
- [[ROUGE Overlap Metrics for Summaries]] — related (the metric all three report)
- [[XSum Extreme Summarisation]] — related
