---
title: "Seq2seq Bottleneck and Attention"
tags: [data-science, concept]
summary: "Encoding a whole input into one vector bottlenecks long inputs; letting the decoder weight all encoder states at each step fixed date normalisation (0.032 to 1.000 whole dates), and removing the recurrence from this idea gives self-attention."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--notes--05-sequence-models.md
  - data/raw/papers/2026-11-08-fundamentals-of-deep-learning-ch07-models-sequence-analysis.md
---

# Seq2seq Bottleneck and Attention

## The bottleneck

A sequence-to-sequence model encodes the input into one vector and decodes from it; that vector is the bottleneck, and decoders do fine on short input and poorly on long. Attention lets the decoder look back at all encoder states at each step, weighted by a learned score: alpha = softmax(e) over input positions.

## Date normalisation test

Task: rewrite dates such as "3 may 1979" as "1979-05-03", with synthetic dates. Without attention: 0.774 per character and 0.032 of whole dates correct. With attention: 1.000 and 1.000 on held-out dates after six epochs. The weights are readable: year digits look at the year, month digits at the "m" of "may", day digits at the "3" and the space beside it. With only 500 training pairs neither model solved it, so attention does not remove the need for data.

## Where it leads

Remove the recurrence and let every position query every other and you have self-attention ([[Self-Attention Mechanism]], [[Transformer Architecture]]).

## Word vectors

In one-hot form every pair of words is equally far apart. Embeddings give geometry: analogies by a - b + c with cosine similarity (man : woman :: king : queen). Neutralising removes a component along a bias direction (a doctor's cosine to the gender direction went from -0.337 to 0.000), with equalise as its companion. Pretrained vectors let a classifier generalise from 127 sentences; averaging them ignores order, an LSTM over them does not. See [[Neural Probabilistic Language Model]].

## The TensorFlow translation tutorial dissected (Fundamentals of Deep Learning, chapter 7)

The textbook walks through the TensorFlow English-to-French attention translator (WMT'15 en-fr), which the chapter says took four days on 8 M40 GPUs; its one reported metric is training perplexity, dropping from roughly 6 to 4 over the first 50k steps and described as reasonable for neural machine translation (no BLEU). Practices it lists:

- group sequence pairs into length buckets (the example uses (5, 10), (10, 15), (20, 25) and (30, 40)) and pad only up to a bucket's size, which it says speeds training and testing considerably, with no timing given;
- reverse the source sequence, which it says helps because the sentence start, the harder part to translate, is then read last (a standard trick, stated without citation or number);
- add GO and EOS symbols and give PAD targets zero loss weight;
- lower the learning rate when the loss is no better than any of the previous three checkpoints, use sampled softmax with an output projection when the target vocabulary is large, and prefer beam search where an early output alters later inputs.

It also describes skip-thought vectors (a single encoder feeding two decoders, one rebuilding the previous sentence and one the next), a feed-forward 3-gram POS tagger (above 96% accuracy within 100 epochs on CoNLL-2000, 300-d Google News vectors, held-out status unclear), and global normalisation with beam search for dependency parsing, where an exhaustive search over 10-word sentences with 15 actions is intractable.

## Limits

- The prose describes attention as a dot product between encoder outputs and the decoder state, while the listed code scores additively (Bahdanau style).
- No baselines, test protocol or significance; translator hyperparameters are not stated, and its translation loop calls a single batch step an epoch. The POS listing reloads the training file as the test set.
- Dated: TensorFlow 0.x and Python 2; it stops at RNN attention with no self-attention, and calls SyntaxNet's parser the most accurate publicly reported at the time of writing.

## See Also
- [[LSTM Forget-Gate Bias and Vanishing Gradients]] — prerequisite-for
- [[Self-Attention Mechanism]] — extends
- [[Autoencoder Bottleneck vs PCA and Anomaly Scores]] — related (the bottleneck as the point)
- [[Scheduled Sampling]] — related (a training schedule for the decoder of such models)
- [[PERSONA-CHAT]] — related (dialogue dataset with generative baselines)
- [[Multi-News]] — related (pointer-generator summarisation benchmark)
- [[End-to-End Memory Networks]] — related
- [[Word Embeddings and Similarity Measures]] — related
