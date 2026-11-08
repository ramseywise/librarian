---
title: Unlimiformer
tags: [foundations, concept]
summary: Unlimiformer replaces cross-attention in a pretrained encoder-decoder with a kNN lookup over the encoder states of the whole input, so one index serves every head and layer; it improves summarization at book length, and does nothing when the input is already ranked.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-bertsch-2023-unlimiformer.md
---

# Unlimiformer

Bertsch et al. (2023) wrap a pretrained encoder-decoder (BART-base, PRIMERA) so that each decoder step retrieves only the keys it needs from an index covering an unbounded input. This is retrieval inside the attention layer, per hidden state and head, not chunk retrieval as in document RAG.

## Mechanism

- The input is encoded in overlapping chunks and only the central half of each chunk's vectors is stored, so each stored vector saw context on both sides. Every input token contributes one vector to a Faiss index.
- Attention scores are a product of decoder state, the query and key projections, and encoder state. Regrouping that product lets the decoder state be projected once into a per-head, per-layer query against a single index of encoder states. The naive approach needs one index per layer and head for keys and values. Memorizing Transformers avoided that cost by using one layer.
- Each head fetches its own top-k keys, and the dot-product scores serve as attention scores. The authors report, from preliminary tests they do not show, that the top-k keys carry over 99% of the attention mass.
- The index costs about 2 GB per million tokens at 16-bit and hidden size 1024.

## Results (self-reported)

- No training: GovReport ROUGE-1 for BART-base goes from 48.7 to 49.7 and SummScreen from 29.7 to 30.9. SLED without training hurt.
- With long-range training on BART-base, GovReport ROUGE-1 is 56.6 against 54.7 for SLED and 55.2 for a single-layer reimplementation of Memorizing Transformers (the reimplementation is an approximation).
- BookSum (about 143K tokens on average): ROUGE is flat or lower (36.4 to 35.5 at test time only) but entity recall doubles (10.0 to 21.9), and 43.5% to 64.5% of tokens are retrieved at least once.
- Inference on BookSum cost about 4.5 times a baseline's GPU time, with inputs near 113K tokens, on a 48 GB card.
- Negative result: on WikiSum with TF-IDF ranked paragraphs it did not beat the first 1,024 tokens.

## Limits

- English only, small old models (139M and 447M), mostly summarization plus a few QA tasks, one model per setting. The decoder-only extension is only claimed.
- BookSum gains rest on an entity-recall proxy with no human check, and ROUGE and BERTScore barely separate the models.
- Training inputs were capped at 16K tokens by GPU memory. A CPU index adds latency, and Faiss GPU retrieval is limited to 2,048 neighbours.

## See Also
- [[Self-Attention Mechanism]] — prerequisite-for
- [[Recurrent Memory Transformer (RMT)]] — alternative-to (recurrent memory instead of retrieval)
- [[Context Retrieval Strategies]] — related (retrieval outside attention)
- [[Why Context Is Finite]] — related
