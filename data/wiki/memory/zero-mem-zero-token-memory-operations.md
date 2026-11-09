---
title: "Zero-Mem Zero-Token Memory Operations"
tags: [memory, pattern, conflict]
summary: "Zero-Mem keeps raw conversation traces and builds its retrieval structure with encoders, entity tagging, BM25 and graph propagation instead of LLM calls; it reports higher LoCoMo and long-context HotpotQA scores than every LLM-memory baseline at zero memory-operation tokens (self-reported, single runs)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-xiao-2026-zero-mem.md
---

# Zero-Mem Zero-Token Memory Operations

Zero-Mem (a 2026 preprint) stores raw traces and uses no LLM call in the memory pipeline; only the final answer reader calls a model. Structure comes from deterministic machinery: a BGE-M3 encoder, spaCy entity tagging, BM25, Personalized PageRank over a graph view, a hierarchical view, a closure step and score calibration. Primary and secondary scores are fused with a weight of 0.6. The authors note that zero tokens is not zero compute, since encoder inference, organisation, retrieval and calibration still run.

## Reported results (self-reported)

- **LoCoMo.** With a GPT-4o-mini reader and a top-5 cap for every method, average F1 is 59.15 against 53.75 for the strongest baseline (GAM), a gap of 5.40 F1 and 5.45 BLEU-1.
- **Distilled memory below memory-free.** With the same reader, plain RAG averages 44.73 F1, which beats MemoryOS (42.84), A-Mem (39.65) and LightMem (38.44); only Mem0 edges ahead, at 45.10. With Qwen2.5-14B, A-Mem, Mem0 and LightMem all fall below RAG and the long-context baseline.
- **Cost** (LoCoMo with GPT-4o-mini; four concurrent threads on identical hardware; just three baselines timed: SimpleMem, LightMem and GAM). SimpleMem spends 14.1M tokens on memory operations, LightMem 0.88M and GAM 28.6M; Zero-Mem spends none. Total time is 334.77 s against 788.76 s for LightMem, a 57.6% cut; tokens exclude the shared answer stage and encoder compute.
- **Long context** (HotpotQA in the MemAgent variant, F1). At 56K tokens Zero-Mem scores 72.07 F1 against 63.22 for GAM, 52.71 for RAG and 56.56 for long-context; at 448K it reaches 65.04 against 54.01 for RAG.
- **Ablation** (HotpotQA, 56K tokens, GPT-4o-mini). The graph view alone gives 62.50 and the hierarchy alone 54.88, so the graph matters more on multi-hop questions.

## Limits

- The authors state no limitations, there is no no-memory baseline, and the long-context baseline is a sliding-window variant. Matching is partial; the extraction notes the five-item cap clearly does not govern that baseline.
- Single runs, two QA benchmarks, no tool use or memory updates. Timing mixes API-bound baselines with a local-GPU run, and top-10 beats the reported top-5, with no account of how the fusion weight was chosen. Code is unreleased.

## See Also
- [[Designed Memory vs Raw-Record Search]] — related (supports raw storage; AtomMem reports the opposite)
- [[A-Mem Zettelkasten Agentic Memory]] — related (a baseline it trails)
- [[Mem0 Extract-and-Update Memory]] — related (a baseline it trails)
- [[Memory Architecture]] — prerequisite-for
