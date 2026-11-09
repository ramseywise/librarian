---
title: HtmlRAG HTML as Retrieval Format
tags: [rag, pattern]
summary: "HtmlRAG keeps retrieved web pages as cleaned and pruned HTML rather than plain text, cutting tokens with rule cleaning and a two-stage block-tree pruner; under a 4K window it beats plain-text chunk-and-rerank baselines on some metrics, though the 70B gains are small (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-tan-2024-htmlrag.md
---

# HtmlRAG HTML as Retrieval Format

Tan and colleagues (WWW 2025) ask whether RAG answers improve when retrieved web pages stay in HTML form, cleaned and pruned, and are not flattened to plain text. Their hypothesis is that HTML preserves structure and semantics lost in plain-text conversion, and that LLMs can read it without fine-tuning.

## Mechanism

1. **Clean** with rules: drop CSS, JS and comments, strip long attributes, merge single-nested tags and drop empty tags. The paper says this removes over 94 percent of tokens. In its preliminary count (no dataset named), raw web HTML averages more than 80K tokens, with CSS, JS and comments making up over 90 percent.
2. **Parse** into a **block tree**, a coarser structure derived from the DOM in which fragmented child nodes are folded into their parents up to a maximum word count. A **block path** is the tag sequence from the root to a block.
3. **Prune by embedding:** greedily keep blocks by BGE similarity at 256-word blocks.
4. **Prune generatively:** a fine-tuned Phi-3.5-mini model scores 128-word blocks by the generation probability of the block path. The result, about 4K tokens, goes to Llama-3.1 readers.

For 20 retrieved documents the token budget falls from 1.6M raw to 135K once cleaned, then 8K after embedding pruning and 4K after generative pruning.

## Results

Self-reported. Setup: Bing-retrieved web HTML, 400 sampled questions per dataset, one run.

- 4K window, Llama-3.1-8B: on ASQA Hit@1 HtmlRAG is ahead of the strongest baseline, which chunks with BGE and reranks. With the 70B reader it wins on MuSiQue EM and lands within 0.1 point of the baseline on ASQA EM and TriviaQA EM. ELI5 ROUGE and BLEU show no advantage (15.51 and 5.84 against 15.87 and 6.30 at 8B).
- 128K window, 70B: HtmlRAG without pruning roughly ties plain text overall (better on NQ, TriviaQA and MuSiQue, worse on ASQA Hit@1 and ELI5). Raw uncleaned HTML does far worse than every cleaned format.
- Ablations (70B, 4K, ASQA Hit@1): dropping the block tree for the DOM costs 9 points, dropping embedding pruning 11.75, dropping generative pruning 6.5.
- Cost (ELI5): pruner latency 6.15 ms for generative pruning, 30.8 ms for embedding pruning and 915 ms for the 70B reader; more than 45 percent of nodes need not be scored by the generative pruner. The pruner was trained on 2635 samples; a 1.5B pruner is slightly worse than the 3.8B one (very preliminary).
- On ASQA, the final 4K context retains more of the reference-answer information than the other 4K methods.

## Limits

- Pruner scaling is "very preliminary" with only two pruners tried. Retrieval is Bing only; no decoding settings or reader prompt are reported; the training data sources are not named.
- At 128K, unpruned HTML ties plain text rather than beating it, and HTML costs extra tokens under 4K windows. The authors observe that the 70B reader sometimes scores below the 8B one and attribute that to distraction by noise.

## See Also
- [[RAG Retrieval Strategies]] — prerequisite-for
- [[RAG Reranking]] — prerequisite-for
- [[Context-Aware Compression]] — related
- [[LLMLingua Coarse-to-Fine Prompt Compression]] — alternative-to
- [[ASQA]] — related
