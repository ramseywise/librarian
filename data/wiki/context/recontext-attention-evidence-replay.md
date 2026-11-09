---
title: "ReContext Attention Evidence Replay"
tags: [context, pattern]
summary: "ReContext, a training-free harness, scores context tokens by attention from the last eight prompt tokens, copies the top sentences into a pool and replays them before the question; mean accuracy rose 0.24 to 0.30 across eight datasets (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-zhao-2026-recontext.md
---

# ReContext Attention Evidence Replay

Models with long windows frequently miss evidence that is present in the prompt. ReContext is a retrieve-within-the-prompt step that needs no training and no external index.

## Mechanism

The last w=8 prompt tokens' attention, averaged over chosen heads with exponential decay, gives each context token a score. The top-K tokens are mapped to their containing sentences, which are copied into an evidence pool. The pool is replayed in the prompt before the question, and the process repeats for R rounds (R=2 in the headline setting). The paper observes that the top 0.1% of tokens (128 tokens in a 128K context) carry about half to 80% of the accumulated relevance score across three models.

## Results (self-reported)

Eight datasets (NQ, TriviaQA, HotpotQA, PopQA and NarrativeQA at 128K, two InfBench tasks, and CLIPPER), run on Qwen3-4B, Qwen3-8B and Llama3.1-8B with thinking disabled, against Vanilla, AttnSharp, DySCO, A-MEM and DAC.
- Mean accuracy rose from 0.24 to 0.30, a 24.6% relative improvement (self-reported). Best average rank on every backbone, but not best on every metric (Qwen3-8B loses HotpotQA, one InfBench task and CLIPPER).
- Cost on CLIPPER with Llama3-8B at 128K: 44 minutes vanilla, 62 minutes ReContext, 2h13m DySCO (self-reported). Memory is about unchanged.
- At 64K, macro-average on three datasets went 0.21 to 0.28 (self-reported). R=1 to R=2 raised a macro-average 0.17 to 0.22 on one ablation.

## Limits

- Needs access to attention scores, so it does not work through closed APIs, and it adds latency.
- No comparison with standard RAG or an external retriever; no variance, seeds or per-dataset sample counts; differences are often 0.01-0.03. Qwen3-4B vanilla scores are near zero in places (NQ 0.02), so relative gains are large and absolute gains small.
- Robustness and ablation tables cover three datasets and one backbone. Best R and K vary by task. The convergence theorem assumes orthogonal token embeddings and is a stylized argument. No model above 8B, no context beyond 128K.

## See Also
- [[Why Context Is Finite]] — prerequisite-for
- [[Context Retrieval Strategies]] — related (retrieval inside the prompt rather than over an index)
- [[Long-Context Prompting]] — related
- [[Trace as State]] — related
