---
title: kNN-LM Nearest Neighbor Language Models
tags: [rag, concept]
summary: "kNN-LM mixes a trained LM's next-token distribution with one built from nearest neighbours in a datastore, with no extra training; the page also covers its translation variant kNN-MT, a gated variant (SPALM) and an ablation study of why it works."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-khandelwal-2019-generalization-through-memorization.md
  - data/raw/papers/2026-11-08-khandelwal-2020-nearest-neighbor-machine-translation.md
  - data/raw/papers/2026-11-08-xu-2023-why-do-nearest-neighbor-language.md
  - data/raw/papers/2026-11-07-yogatama-2021-adaptive-semiparametric-language-models.md
---

# kNN-LM Nearest Neighbor Language Models

kNN-LM (Khandelwal et al., ICLR 2020) improves a pre-trained decoder-only language model at test time without training it further. A single pass of the LM over a text collection stores pairs of a context representation (the input to the final feed-forward layer, after layer norm) and the token that followed. The pairs go into a FAISS index. When predicting, the k nearest keys by L2 distance yield a distribution via a softmax over negative distances, and the output is a weighted mix of that distribution with the LM's own, using a weight lambda. The authors' hypothesis is that learning a similarity between contexts is an easier job than predicting the next word, which should help rare patterns. A **datastore** is the key-value store of context representations and next words.

## Results of the original paper (self-reported)

- WikiText-103, 247M LM, datastore of the 103M training tokens, k=1024, median of 3 seeds: kNN-LM lowers test perplexity of the base LM, and adding a continuous cache gives a perplexity of 15.79, reported as a new state of the art.
- Pairing a small LM (100M training tokens) with a datastore built from 3B tokens beats training that LM on the whole 3B corpus; a datastore of 1.6B entries already passes the LM trained on Wiki-3B (Wiki-100M LM, test set).
- Swapping in an in-domain Books datastore under a Wikipedia-trained LM lowers Books perplexity; the in-domain Books LM reaches 11.89 for comparison.
- An interpolation weight of 0.25 suits in-domain WikiText-103, while 0.65 suits the domain-adaptation setting; k=8 already reaches the state of the art on validation, and full-precision squared L2 beats quantized distances.
- A Transformer with dropout removed memorises its training data; interpolating with it gains 0.1 where kNN-LM gains 1.9 (WikiText-103 validation).

## kNN-MT: the same idea for translation

Nearest Neighbor Machine Translation (Khandelwal et al., ICLR 2021) caches decoder representations from one forward pass over parallel data (1024-d keys, gold target tokens as values). Compared with kNN-LM, its keys include the source context and it adds a softmax temperature. Setups differ per result (all self-reported): a WMT'19 de-en model gains 1.5 BLEU using a datastore of about 770M training tokens (newstest2019); an in-domain datastore averages +9.2 BLEU on five domain sets, with the largest gains on Law (16) and Medical (14.5); and a multilingual model gains up to 3 BLEU on en-de, en-zh and zh-en (CCMatrix datastores, 418M model). A temperature of 10 or 100 was best on validation sets, and more than 64 neighbours did not help.

## Why it works (Xu et al., 2023)

The authors re-implement kNN-LM on a 268M Transformer (WikiText-103; 33K BPE vocabulary; k of 1024; the whole 150M-token training set as datastore) and change one design choice at a time. The base perplexity of 21.750 falls to 19.174 (attention-output query, L2) and 19.095 (inner product). Querying with the feed-forward output instead leaves it at 20.734 (L2). Approximate FAISS search beat exact search (19.174 against 19.735), which the authors suggest acts as a regulariser. Temperature tuning matters; the gap between the default and the best setting can reach 3.7% relative perplexity. Interpolating the base LM with a separately trained output matrix applied to the attention output, with no retrieval, captures about 55% of the gain (self-reported).

## SPALM: a learned gate instead of output interpolation

SPALM (Yogatama et al., 2021) uses a Transformer-XL in which a sigmoid gate blends the final hidden state with an attention-weighted summary of what followed each of k neighbours (ScaNN, frozen datastore, keys from a separately pretrained transformer). Only the gate vector is new. On WikiText-103 (142M parameters, M=3072, 4 neighbours) SPALM interpolated with the kNN distribution reaches test perplexity 17.6; on enwik8 it gets 1.00 BPC against 1.02 for kNN-LM (self-reported).

## Limits

- Khandelwal et al. report perplexity only, with one datastore entry per token; latency and memory for the 3B datastore are not reported, and run counts are given only for Table 1.
- kNN-MT decoding is roughly 100x slower with billion-scale datastores; lambda and temperature are tuned per language pair or domain; only BLEU was measured.
- Xu et al. use one model size and dataset, and their datastore is the training set, so the study explains the gain there rather than retrieval from fresh text. The regularisation account is correlational.
- SPALM needs neighbours for every training token (6-8 hours on 1,000 CPUs for WikiText-103 and enwik8), uses static evaluation, and with M of 512 kNN-LM scores 18.5 on test against 18.8 for SPALM alone.
- The causal explanation of why kNN-LM works in the original paper is a conjecture, not tested.

## See Also
- [[RETRO Chunked Cross-Attention Retrieval]] — related (chunk-level retrieval keeps the index far smaller than one entry per token)
- [[In-Context RALM and REPLUG]] — alternative-to (prepends passages instead of interpolating output distributions)
- [[Retrieval-Pretrained Transformer Self-Retrieval]] — related (test-time-only retrieval contrasted with joint training)
- [[RAG Survey Taxonomies]] — related (parallel interpolation as an interaction mode)
- [[Vector Database Comparison]] — related
