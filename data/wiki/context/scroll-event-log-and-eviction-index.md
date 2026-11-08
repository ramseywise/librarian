---
title: Scroll Event Log and Eviction Index
tags: [context, concept]
summary: Scroll keeps an agent's whole history in an append-only log outside the prompt, evicts stale spans from the view only, and leaves model-written headlines pointing at the verbatim record; it scored 73.1 on BEAM 10M against 68.0 published (self-reported, not a controlled comparison).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-lin-2026-context-as-environment.md
---

# Scroll Event Log and Eviction Index

Lin et al. (Alibaba technical report, 2026) treat context as an environment that the agent manages by writing code. In their framing, compaction and write-time memory extraction fix what is kept before anyone knows what will be needed. Scroll postpones that decision until a query arrives.

## Mechanism

- **Event Log.** Append-only SQLite; every event has a stable `seq` address and stays verbatim.
- **Kernel.** A persistent sandboxed Python process holds working state, and only `print` output enters the context.
- **Eviction.** Over budget, the view first protects the current turn, the latest tail and the newest tool results. Finished tool payloads are replaced by `seq` pointers before anything else, and entire spans are dropped only if the view is still too large. Eviction alters the view, never the record.
- **Eviction index.** Tiers of headlines written by the model, each tied to a `seq`, tell the agent which material has left its view. A tier keeps at most k blocks, which bounds the index at O(k log_k n) blocks.
- **Operations.** Locate (`ms.search`, BM25, no index-time model calls), materialise (`ms.expand`), compute (ordinary Python), expose (`print`).

## Results (self-reported)

One run per task, with Qwen3.8-Max as the backbone.
- BEAM 10M: 73.1 against 68.0 for the best published system, whose numbers use other readers and were not reproduced. The median query used about 105K tokens, about 1% of the corpus.
- LOCA from 128K to 256K with one backbone and one toolset. Accuracy fell from 86.7 to 65.3 for a summarisation agent and from 88.0 to 66.7 for a recall-tool agent, against 89.3 to 85.3 for CodeAct and 89.3 to 86.7 for Scroll. The "+37.4" claim is against a different backbone. The extraction infers about 75 tasks.
- Ablations on BEAM 10M: lossy summarisation at ingestion 19.9, no REPL 7.3 below full Scroll, no eviction index 1.8 below.
- LongMemEval S 94.8 (below one published system at 96.4) and M 89.6.

## Limits

- No confidence intervals, one main backbone. Weaker backbones fall far behind at 256K (GLM-5.2 62.7, Qwen3.6-35B-A3B 22.7).
- Weaker than baselines on summarisation (70.5 against 91.9), preference following and temporal reasoning. Cost is in tokens only, and BEAM and LongMemEval measure retrieval only.
- Crash recovery is described but never tested. Production compactors are not compared.

## See Also
- [[Context Compaction]] — alternative-to
- [[PRO-LONG Programmatic Memory]] — related (lossless log read by code)
- [[Context Window Budgeting]] — related
- [[Memory as Context]] — related
