---
title: "Seq2seq Bottleneck and Attention"
tags: [foundations, concept]
summary: "Encoding a whole input into one vector bottlenecks long inputs; letting the decoder weight all encoder states at each step fixed date normalisation (0.032 to 1.000 whole dates), and removing the recurrence from this idea gives self-attention."
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--notes--05-sequence-models.md
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

## See Also
- [[LSTM Forget-Gate Bias and Vanishing Gradients]] — prerequisite-for
- [[Self-Attention Mechanism]] — extends
- [[Autoencoder Bottleneck vs PCA and Anomaly Scores]] — related (the bottleneck as the point)
- [[Scheduled Sampling]] — related (a training schedule for the decoder of such models)
- [[PERSONA-CHAT]] — related (dialogue dataset with generative baselines)
- [[Multi-News]] — related (pointer-generator summarisation benchmark)
- [[End-to-End Memory Networks]] — related
