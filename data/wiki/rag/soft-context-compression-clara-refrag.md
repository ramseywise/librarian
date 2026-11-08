---
title: Soft Context Compression for RAG (CLaRa and REFRAG)
tags: [rag, foundations, llm, concept]
summary: "Two 2025 papers feed the decoder compressed chunk embeddings instead of passage tokens: CLaRa trains retrieval and generation together through a straight-through top-k, REFRAG buys time-to-first-token with chunk embeddings and an RL policy that expands some chunks."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-he-2025-clara.md
  - data/raw/papers/2026-11-06-lin-2025-refrag.md
---

# Soft Context Compression for RAG

Soft compression replaces retrieved text with a few continuous vectors per chunk. Both papers below are preprints and all numbers are self-reported.

## CLaRa

CLaRa (arXiv 2511.18659) compresses each 256-token chunk to memory tokens (256 divided by the ratio) and trains the query encoder and generator jointly. The mechanism that makes joint training work is a differentiable top-k: a hard selection when computing the output and softmax gradients when learning (a straight-through estimator). The authors contrast it with RL sampling, which they call unstable and inefficient. Retrieval therefore learns from the generator's next-token loss alone, with no relevance labels.

Setup: LoRA-tuned Mistral-7B-Instruct, a 2021 Wikipedia corpus, twenty BGE candidates cut to five, four QA sets.
- At 16x compression, average F1 was 40.30 against 41.96 for a raw-text jointly trained baseline (copied from that paper, not re-run), so the extraction's safe reading is "comparable, not better".
- Under the oracle setting (gold document guaranteed in the candidates), HotpotQA Recall@5 was 96.21% at 4x, where an untuned BGE reranker scored 85.93%. A supervised baseline the authors trained reached 82.84% in that cell, the win does not hold on 2Wiki, and it falls to 87.85% at 16x.
- Decoding took about 40% of the time of raw text on Mistral-7B (502 to 533 ms against 1290.57 ms, single H100). Compression time (835 to 1092 ms per query) is excluded as offline.
- Ratio sweep, normal setting: average 39.86 at 4x, 38.96 at 16x and 37.38 at 256x. Entity preservation on seen data drops from 54.78 at 4x to 42.12 at 256x.

## REFRAG

REFRAG (arXiv 2509.01092) feeds precomputed chunk embeddings (RoBERTa-large encoder) to a LLaMA-2-7B decoder. The motivating observation is that retrieved passages show block-diagonal attention (one query and five hand-picked passages, qualitative only). A policy (a small two-layer transformer reading chunk embeddings, trained GRPO-style with negative output log-perplexity as the reward) chooses which chunks to expand back to tokens.

- Time-to-first-token (batch size 1, single A100, 16384 context): at k=16, 16.53x when chunk embeddings are cached and 8.59x when they are not, against 2.01x and 1.04x for CEPE. Per-token decoding speed improved only about 3x at long context.
- At matched latency (8 passages for REFRAG, 1 for the baseline), the average over 16 RAG tasks improved by 1.22% with a strong retriever and 1.93% with a weak one.
- Perplexity at 2048 context: REFRAG8 1.062 against 1.069 for full context; REFRAG16 and REFRAG32 are worse than full context.
- RL-selected expansion at an effective rate of 8.25 matched or beat REFRAG trained at k=8. Curriculum learning and a reconstruction pre-task were essential (reconstruction log-perplexity 0.669 with curriculum against 3.719 without).
- Beyond roughly 20 to 50 passages many tasks stayed flat or fell.

## Limits

- CLaRa: the abstract and prose say it beats text-based baselines, but Table 2 shows comparable at best (NQ F1 51.41 is the 128x row, not 16x). There is no limitations section; the offline-compression claim holds only for a static corpus, and vector storage is not reported. Explanations such as compression filtering out noise are untested.
- REFRAG: the 32-passage speedup is given as 30.85x, 30.75x and 32.99x in different places. "Without loss in perplexity" is stronger than Table 1 (true only at k=8). The strongest baselines at 80 passages are not like for like.
- Different decoders (7B-class), tasks and metrics, so the two papers are not comparable with each other.

## See Also
- [[Context-Aware Compression]] — related (text-level compression of context)
- [[RL for Retrieval Policies]] — alternative-to (RL over retrieval versus CLaRa's straight-through gradient)
- [[RAG Reranking]] — alternative-to (CLaRa replaces a separate trained reranker with a generator-trained scorer)
- [[Prefix Caching]] — related (another way to cut time-to-first-token on repeated context)
