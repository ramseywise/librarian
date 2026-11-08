---
title: Delta-Mem Fixed-Size State Memory
tags: [foundations, pattern]
summary: "delta-mem keeps a frozen language model and adds a small 8x8 matrix state updated by a gated delta rule, whose read-out nudges attention; at 4.87M trainable parameters it raises a 5-benchmark average on Qwen3-4B from 46.79 to 51.66 (self-reported) with text-memory baselines falling below the backbone."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-lei-2026-mem.md
---

# Delta-Mem Fixed-Size State Memory

delta-mem (a 2026 preprint) is an online memory for a frozen backbone. A small matrix state S (8x8) is updated with a gated delta rule: the old state is decayed per dimension, then corrected toward a new key-value association by an amount set by a write gate. At each step a read-out S times the query yields low-rank corrections to the attention query and output projections, so history shapes generation without being placed in the prompt. Three write granularities are tried: TSW, SSW and MSW (the source gives these write-granularity names only as acronyms). Only the small projection modules train (4.87M parameters for SSW and TSW, about 0.12% of the backbone; 19.47M for MSW), by SFT on 2,219 QASPER samples with one seed.

## Results (greedy decoding unless noted; single seed)

- On Qwen3-4B-Instruct the five-benchmark average (IFEval, HotpotQA, GPQA-Diamond, MemoryAgentBench, LoCoMo; greedy decoding, single seed) is 46.79 for the bare backbone, 44.90 for the best other method (Context2LoRA) and 51.66 for delta-mem TSW (self-reported). MemoryAgentBench rises 29.54 to 38.85 and LoCoMo 40.79 to 49.12 (self-reported, same setup).
- Other backbones: Qwen3-8B 47.20 to 50.86; SmolLM3-3B 26.08 to 36.96 (self-reported, same five-benchmark average, single seed).
- Text-memory baselines land under the backbone: 44.56 for BM25 RAG, 42.96 for LLMLingua-2 and 43.88 for MemoryBank (self-reported, same average on Qwen3-4B). The authors attribute this to retrieval noise, a hypothesis they did not test.
- Probing whether the 8x8 state alone recovers context: HotpotQA exact match goes from 0.08 to 6.48 (self-reported, no-context ablation), so the state is a lossy summary rather than a store.

## Limits

- The state only approximates context; decoding is slower than the vanilla model; nothing above 8B was tested; one seed and one small training set; modules are tied to the backbone they were trained on. Some baseline cells are missing.
- Gains are on average across mixed benchmarks; per-benchmark behaviour varies and baselines include several systems that start below the backbone.

## See Also
- [[Doc-to-LoRA]] — alternative-to (writing context into weights instead of a state)
- [[Query-Only Test-Time Training (qTTT)]] — related
- [[LM2 Large Memory Models]] — alternative-to
- [[Memory Forms Taxonomy]] — prerequisite-for
