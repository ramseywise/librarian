---
title: CCNet Web Crawl Corpus Pipeline
tags: [foundations, method]
summary: "CCNet deduplicates Common Crawl paragraphs before language identification, then buckets each language's documents by perplexity under a Wikipedia language model."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-wenzek-2019-ccnet.md
---

# CCNet Web Crawl Corpus Pipeline

The paper asks how to pull clean monolingual corpora for many languages out of Common Crawl without manual work. Its hypothesis is that removing duplicate paragraphs before identifying language, then grouping documents by how well a Wikipedia-trained language model predicts them, yields better pretraining text than raw crawl or Wikipedia itself.

## Mechanism

For each Common Crawl WET snapshot the pipeline shards the data into 5GB JSON files, hashes normalised paragraphs (a 64-bit SHA-1 hash) to drop duplicates, applies fastText language ID with a 0.5 score cutoff, and scores each document with a KenLM model trained on that language's Wikipedia. Each language is then cut into three equal-size buckets (head, middle, tail) by perplexity; no document is discarded on the LM score. Quality is probed by training fastText embeddings and a BERT-Base model on the buckets.

## Results

- In a Feb 2019 snapshot, repeated paragraphs make up 70% of the text; deduplicating within one shard leaves 42% of characters, and across 100 shards 28% (self-reported).
- One snapshot takes roughly 9 hours on 5000 CPU cores and produces 1.5B documents across 174 languages, 700M of them English (self-reported).
- On XNLI dev, BERT-Base pretrained on the CC head outperforms the Wikipedia-pretrained model by an average of 3.3 points, 75.9 against 72.6 (self-reported). Setup: en, ru, zh, ur; equal training steps, stopped early at 2 days on 16 Volta32 GPUs; head data capped at 21G/21G/17G/2.2G versus Wikipedia sizes of 16G/5G/1.1G/106M.
- The Urdu model gains 7 points over its Wikipedia-trained counterpart, which sits close to a randomly initialised model; English XNLI is 85.0 versus 82.8 (self-reported).
- fastText total analogy accuracy rises from tail to head in English (62.0, 74.2, 77.9) and Polish head is 65.3 against 59.9 for tail (self-reported).
- For low-resource languages the CC data exceeds Wikipedia in size, for example Khmer at 154MB versus 71MB (self-reported).

## Limits

- One run per cell, no seeds.
- The comparison with Wikipedia mixes data quality with data volume, since the CC head is larger for ru, zh and ur.
- Only fastText was run on all three buckets; the BERT experiments used the head alone.
- A Wikipedia-based LM scores valid text with other vocabulary as worse, which the authors acknowledge; the LM differs in size per language, so cutoffs are chosen per language.
- The paper does not report the BERT hyperparameters.

## See Also
- [[Eval Contamination Defenses]] — related (corpus-level deduplication by hashing)
- [[Vision-Language Model Training Families]] — related (web-scale data filtering for pretraining)
