---
title: WikiSum and Memory-Compressed Attention
tags: [llm, architecture, concept]
summary: "Liu et al. generate Wikipedia lead sections from reference documents in two stages, extractive ranking then an abstractive decoder-only Transformer whose T-DMCA variant uses local attention blocks and memory-compressed keys and values for inputs of up to 11,000 tokens."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-liu-2018-generating-wikipedia-summarizing-long-sequences.md
  - data/raw/papers/2026-11-08-tay-2022-efficient-transformers.md
---

# WikiSum and Memory-Compressed Attention

Liu, Saleh, Pot et al. ask whether English Wikipedia lead sections can be produced by multi-document summarisation of reference documents, and whether a decoder-only model can cope with the very long inputs. Their hypothesis is that a decoder-only Transformer using local and memory-compressed attention takes longer inputs than encoder-decoder models and does better on long sequences. WikiSum is the dataset built for this task.

## Method

- **Stage 1 (extractive):** rank paragraphs of cited and web-search documents by tf-idf against the title and keep the first L tokens.
- **Stage 2 (abstractive):** train a model to write the lead: a seq2seq-attention baseline, a Transformer encoder-decoder (T-ED), a decoder-only Transformer (T-D) or T-DMCA.
- **T-DMCA:** a Transformer decoder with local attention blocks plus memory-compressed attention, where keys and values are compressed by a strided convolution. Tay et al. report the compressed cost as O(n*n/k) for kernel and stride k, and blockwise local attention as O(b*n).
- A mixture-of-experts layer is used in some variants.

## Results (all self-reported, WikiSum test set, tf-idf extractor, combined corpus)

- T-ED at L = 500 gets perplexity 2.46645 (ROUGE-L 34.2); T-D at L = 4000 gets 2.22216; T-DMCA without MoE at L = 11000 gets 2.05159. Table 4 puts the T-DMCA model with 256 MoE experts, run at L = 7500, ahead on ROUGE-L and on perplexity.
- T-ED cannot learn at L = 2000, and T-D improves to L = 4000 before running out of memory on a 16GB P100. The seq2seq-attention baseline is far worse.
- Using 128 experts of MoE reduces log-perplexity at L = 11000.
- The choice of extractor matters (tf-idf versus identity versus a cheating oracle, with T-ED at L = 500), and the combined corpus does better than citations alone or search results alone.
- WikiSum has the lowest ROUGE-1 recall of output given input among the summarisation datasets compared.
- Against Sauper and Barzilay, T-DMCA is ahead on ROUGE-1 F1 on American Actors (n = 1322) and worse on Diseases (n = 161). Human linguistic-quality evaluation uses 25 examples and 3 raters.

## Limits

- The full-article generation experiment is early and untuned.
- The comparison with Sauper and Barzilay is best-effort: lead against article, different subsets, clone detection unknown.
- The extractive stage is a coarse bottleneck, and the authors suggest supervised relevance.
- The optimiser, learning rate, batch size and step count for T-D and T-DMCA are not given; runs are single. Human side-by-side evaluation is harder when quality is high.
- Models translate names across languages, which is not systematically evaluated.

## See Also

- [[Self-Attention Mechanism]] — prerequisite-for
- [[Efficient Attention Approximations]] — related (Tay et al.'s survey covers memory-compressed attention)
- [[Longformer Sliding-Window and Global Attention]] — alternative-to (a different way to attend over long inputs; Longformer's LED is evaluated on summarisation)
